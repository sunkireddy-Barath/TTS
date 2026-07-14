"""
voice_clone.py
Orchestrates the Cross-Lingual Voice Cloning pipeline using the real OmniVoice API.

Architecture (correct for OmniVoice):
    reference audio + target text
        ↓
    Expression Engine → inject [expression-tag] into text   (V2 global, V3 inline)
        ↓
    Tag Parser → split into TextSegment list
        ↓
    For each segment:
      ├─ is_expression_segment=True  → speed=1.0, no instruct (clone mode never uses instruct)
      └─ is_expression_segment=False → speed from EmotionEngine.resolve()
        ↓
    OmniVoice model.generate(text=..., ref_audio=..., speed=..., num_step=...)
        ↓
    Concatenate segments → Audio WAV bytes

Version behaviour:
  V1 — emotion speed only, no expression, all inline tags stripped
  V2 — emotion speed + expression tag injected globally at punctuation boundaries
  V3 — inline <emotion> tags + inline expression tags processed natively

Key stability rule (same as voice_design.py):
    Expression segments (is_expression_segment=True) MUST use speed=1.0.
    The diffusion model self-paces expression tokens; forcing a slow/fast speed
    causes blank or noisy output.

Notes
-----
- Cross-lingual cloning does NOT use the instruct parameter.
  The reference audio carries the voice identity; the target language is
  inferred from the text content.
- ref_text is optional: if provided it improves cloning accuracy.
  If omitted, OmniVoice uses Whisper ASR to auto-transcribe the reference.
"""

import io
import re
import random
import numpy as np
import soundfile as sf
import torch

from typing import Optional

from emotion_engine import EmotionEngine
from expression_engine import ExpressionEngine
from tag_parser import TagParser
from audio_verifier import AudioVerifier
from omnivoice_engine import OmniVoiceEngine, SAMPLE_RATE
from noise_reduction import apply_mossformer_enhancement

DEFAULT_NUM_STEP = 50


class VoiceCloneService:
    """
    Entry-point for the Cross-Lingual Voice Cloning feature.
    """

    def __init__(self, engine: Optional[OmniVoiceEngine] = None):
        self.engine = engine or OmniVoiceEngine.get_instance()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate(
        self,
        text: str,
        target_language: str,
        reference_audio_bytes: bytes,
        gender: str = "neutral",
        age: int = 30,
        emotion: str = "neutral",
        expression: str = "none",
        version: int = 2,
        ref_text: str = "",
        num_step: int = DEFAULT_NUM_STEP,
    ) -> bytes:
        """
        Generate cross-lingual cloned speech.

        Parameters
        ----------
        text                  : Text in the target language.
        target_language       : Frontend language code (e.g. 'ta', 'fr').
        reference_audio_bytes : Raw bytes of reference WAV / MP3 / OGG / FLAC.
        gender                : Hint only — clone mode does not change pitch via instruct.
        age                   : Age hint — used for speed scaling on speech segments.
        emotion               : Emotion label → mapped to speed on speech segments.
        expression            : Expression label. Ignored for V1.
        version               : 1 | 2 | 3.
        ref_text              : Transcription of the reference audio (optional).
        num_step              : OmniVoice diffusion steps.

        Returns
        -------
        bytes : WAV bytes at 24 kHz mono PCM-16.
        """
        # Enhance/clean the reference audio first
        reference_audio_bytes = apply_mossformer_enhancement(reference_audio_bytes)

        if version == 1:
            # V1: emotion speed only — strip all inline tags, ignore expression.
            final_text = TagParser.strip_all_tags(text)

        elif version == 2:
            # V2: strip inline tags, then inject the dropdown expression globally.
            final_text = TagParser.strip_all_tags(text)
            final_text = ExpressionEngine.inject_tag(final_text, expression)

        else:
            # V3: keep inline emotion + expression tags as-is.
            # If a global expression was also selected, inject it too.
            final_text = text
            if expression and expression.lower() != "none":
                final_text = ExpressionEngine.inject_tag(final_text, expression)

        out_bytes = self._generate_multi_segment(
            text=final_text,
            reference_audio_bytes=reference_audio_bytes,
            gender=gender,
            age=age,
            fallback_emotion=emotion,
            ref_text=ref_text,
            num_step=num_step,
        )

        # MossFormer2 post-processing on the generated output
        return apply_mossformer_enhancement(out_bytes, force_process=True)

    # ------------------------------------------------------------------ #
    #  Internal: multi-segment cloning                                     #
    # ------------------------------------------------------------------ #

    def _generate_multi_segment(
        self,
        text: str,
        reference_audio_bytes: bytes,
        gender: str,
        age: int,
        fallback_emotion: str,
        ref_text: str,
        num_step: int,
        max_attempts: int = 5,
    ) -> bytes:
        """
        Parse <emotion> blocks → synthesise each with its own speed
        → concatenate with 200 ms silence between segments.

        CRITICAL:
            Segments where is_expression_segment=True are given speed=1.0.
            Expression tokens self-pace; forcing a non-neutral speed causes
            the diffusion model to generate blank or noisy audio.
            Clone mode never uses instruct, so that is always "".
        """
        segments   = TagParser.parse(text, default_emotion=fallback_emotion)
        audio_parts: list[np.ndarray] = []

        # Fix seed to ensure voice stability across segments
        request_seed = random.randint(1, 999999)

        for idx, seg in enumerate(segments):
            is_last  = (idx == len(segments) - 1)
            seg_text = seg.text.strip()

            # Skip empty or punctuation-only segments
            if not seg_text:
                continue
            if not re.search(r'[\w\u0080-\uFFFF\[]', seg_text):
                continue

            # ── Speed selection ───────────────────────────────────────────
            if seg.is_expression_segment:
                # Expression token: neutral speed so the token self-paces.
                speed = 1.0
            else:
                # Normal speech: emotion → speed mapping.
                params = EmotionEngine.resolve(seg.emotion, gender, age)
                speed  = params.speed

            # Clone mode NEVER uses instruct.
            instruct = ""

            # ── Generate with retry ───────────────────────────────────────
            best_wav_bytes = None
            is_valid       = False

            for attempt in range(max_attempts):
                seed_val = request_seed + attempt
                random.seed(seed_val)
                np.random.seed(seed_val)
                torch.manual_seed(seed_val)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed_val)

                if attempt > 0:
                    print(f"  [VC] Segment {idx+1} retry {attempt+1}/{max_attempts} "
                          f"(expr={seg.is_expression_segment}) …")

                try:
                    wav_bytes = self.engine.synthesize_voice_clone(
                        text=seg_text,
                        reference_audio_bytes=reference_audio_bytes,
                        ref_text=ref_text,
                        speed=speed,
                        num_step=num_step,
                        instruct=instruct,
                    )
                    is_valid       = True
                    best_wav_bytes = wav_bytes
                    break
                except ValueError as ve:
                    # engine raises ValueError on blank/noisy audio — retry
                    print(f"  [VC] Segment {idx+1} attempt {attempt+1} failed: {ve}")
                except Exception as exc:
                    print(f"  [VC] Segment {idx+1} unexpected error: {exc}")
                    break   # non-retryable

            if not is_valid or best_wav_bytes is None:
                print(f"  [VC] Segment {idx+1} — all attempts failed, skipping.")
                continue

            try:
                arr, _ = sf.read(io.BytesIO(best_wav_bytes))
                arr = arr.astype(np.float32)
            except Exception as e:
                print(f"  [VC] Segment {idx+1} — could not decode WAV: {e}")
                continue

            # 10 ms fade-in/out to prevent clicks at segment boundaries
            fade_len = int(SAMPLE_RATE * 0.01)
            if len(arr) > fade_len * 2:
                fade_in  = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
                fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
                arr[:fade_len]  *= fade_in
                arr[-fade_len:] *= fade_out

            audio_parts.append(arr)

            # 200 ms silence gap between segments
            if not is_last:
                audio_parts.append(np.zeros(int(SAMPLE_RATE * 0.20), dtype=np.float32))

        if not audio_parts:
            raise ValueError("No valid text segments produced audio.")

        combined = np.concatenate(audio_parts)
        buf = io.BytesIO()
        sf.write(buf, combined, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        buf.seek(0)
        return buf.read()
