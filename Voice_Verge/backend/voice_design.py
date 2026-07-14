"""
voice_design.py
Orchestrates the Voice Design pipeline using the real OmniVoice API.

Architecture (Unified for all versions):
    user input
        ↓
    Expression Engine → inject [expression-tag] into text   (V2 global, V3 inline)
        ↓
    Tag Parser (split text into emotion segments, using global emotion as fallback)
        ↓
    For each segment:
      ├─ is_expression_segment=True  → gender-only instruct, speed=1.0
      └─ is_expression_segment=False → EmotionEngine.build_instruct(), speed from emotion
        ↓
    OmniVoice model.generate(text=..., instruct=..., speed=...)
        ↓
    Concatenate segments → Audio WAV bytes

Key stability rule:
    Expression tokens ([laughter], [sigh], [surprise-ah], etc.) MUST be
    generated with a clean, minimal instruct — gender only, no pitch hints.
    Any pitch or style hint in the instruct string causes the diffusion model
    to produce blank or noisy audio when combined with these non-speech tokens.
"""

import io
import re
import random
import numpy as np
import soundfile as sf
import librosa
import torch
import torchaudio
from typing import Optional

from emotion_engine import EmotionEngine
from expression_engine import ExpressionEngine
from language_router import LanguageRouter
from tag_parser import TagParser
from omnivoice_engine import OmniVoiceEngine, SAMPLE_RATE
from audio_verifier import AudioVerifier
from noise_reduction import apply_mossformer_enhancement

# Diffusion steps: 50 = highest quality, 16 = faster inference
DEFAULT_NUM_STEP = 50


class VoiceDesignService:
    """
    Entry-point for the Voice Design feature.

    Handles:
      - V1: Emotion dropdown only (no expression).
      - V2: Emotion dropdown + Expression dropdown (global expression injected into text).
      - V3: Inline <emotion> tags + inline expression tags in text.
    """

    def __init__(self, engine: Optional[OmniVoiceEngine] = None):
        self.engine = engine or OmniVoiceEngine.get_instance()

    def generate(
        self,
        text: str,
        language: str,
        gender: str = "neutral",
        age: int = 30,
        emotion: str = "neutral",
        expression: str = "none",
        version: int = 2,
        num_step: int = DEFAULT_NUM_STEP,
    ) -> bytes:
        """
        Generate speech via OmniVoice Voice Design.

        V1 — Emotion dropdown only. All inline tags stripped, expression ignored.
        V2 — Emotion dropdown + Expression dropdown (injected globally at punctuation).
        V3 — Inline <emotion> tags + inline <expression> tags processed natively.
        """
        lang_code = LanguageRouter.resolve(language)
        accent    = LanguageRouter.get_accent(language)

        if version == 1:
            # V1: emotion instruct only — strip everything else.
            final_text = TagParser.strip_all_tags(text)

        elif version == 2:
            # V2: strip any user-typed inline tags, then inject the dropdown expression globally.
            final_text = TagParser.strip_all_tags(text)
            final_text = ExpressionEngine.inject_tag(final_text, expression)

        else:
            # V3: keep inline emotion tags + inline expression tags as-is.
            # If a global expression was also selected, inject it too.
            final_text = text
            if expression and expression.lower() != "none":
                final_text = ExpressionEngine.inject_tag(final_text, expression)

        out_bytes = self._generate_multi_segment(
            final_text, gender, age, accent, emotion, num_step
        )
        # Apply gentle post-processing (trim_silence=False — expressions are short!)
        return apply_mossformer_enhancement(out_bytes, trim_silence=False, force_process=False)

    # ------------------------------------------------------------------ #
    #  Internal: multi-segment synthesis                                   #
    # ------------------------------------------------------------------ #

    def _generate_multi_segment(
        self,
        text: str,
        gender: str,
        age: int,
        accent: str,
        fallback_emotion: str,
        num_step: int,
        max_attempts: int = 5,
    ) -> bytes:
        """
        Parse <emotion> blocks → synthesise each with its own instruct
        → concatenate with 200 ms silence between segments.

        CRITICAL:
            Segments where is_expression_segment=True are given:
              • instruct = gender-only  (e.g. "female" or "male" or "")
              • speed    = 1.0
            This is REQUIRED so the diffusion model can render expression tokens
            ([laughter], [sigh], etc.) without producing blank or noisy audio.
        """
        segments    = TagParser.parse(text, default_emotion=fallback_emotion)
        audio_parts = []

        request_seed = random.randint(1, 999999)

        for idx, seg in enumerate(segments):
            is_last   = (idx == len(segments) - 1)
            seg_text  = seg.text.strip()

            # Skip empty or punctuation-only segments
            if not seg_text:
                continue
            if not re.search(r'[\w\u0080-\uFFFF\[]', seg_text):
                continue

            # ── Instruct & speed selection ────────────────────────────────
            if seg.is_expression_segment:
                # Expression token: use gender-only instruct, neutral speed.
                # Any pitch/style/age hint will corrupt the expression generation.
                g = gender.lower().strip()
                instruct = g if g in ("male", "female") else ""
                speed    = 1.0
            else:
                # Normal speech segment: full emotion instruct.
                params   = EmotionEngine.resolve(seg.emotion, gender, age)
                instruct = EmotionEngine.build_instruct(gender, age, params, accent)
                speed    = params.speed

            # ── Generate with retry ───────────────────────────────────────
            best_wav_bytes = None
            is_valid       = False

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f"  [VD] Segment {idx+1} retry {attempt+1}/{max_attempts} "
                          f"(expr={seg.is_expression_segment}) …")
                    torch.manual_seed(request_seed + attempt)
                    np.random.seed(request_seed + attempt)
                    random.seed(request_seed + attempt)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(request_seed + attempt)

                try:
                    wav_bytes = self.engine.synthesize_voice_design(
                        text=seg_text,
                        instruct=instruct,
                        speed=speed,
                        num_step=num_step,
                    )
                    is_valid       = True
                    best_wav_bytes = wav_bytes
                    break
                except ValueError as ve:
                    # engine raises ValueError on blank/noisy audio — retry
                    print(f"  [VD] Segment {idx+1} attempt {attempt+1} failed: {ve}")
                except Exception as exc:
                    print(f"  [VD] Segment {idx+1} unexpected error: {exc}")
                    break   # non-retryable

            if not is_valid or best_wav_bytes is None:
                print(f"  [VD] Segment {idx+1} — all attempts failed, skipping.")
                continue

            try:
                waveform, sr = torchaudio.load(io.BytesIO(best_wav_bytes))
                audio_parts.append(waveform.squeeze().numpy())
            except Exception as e:
                print(f"  [VD] Segment {idx+1} — could not decode WAV: {e}")
                continue

            # 200 ms silence gap between segments
            if not is_last:
                silence_samples = int(sr * 0.20)
                audio_parts.append(np.zeros(silence_samples, dtype=np.float32))

        if not audio_parts:
            # Fallback: 1-second silence (prevents completely empty file)
            dummy_wav = np.zeros(SAMPLE_RATE, dtype=np.float32)
            out_io = io.BytesIO()
            sf.write(out_io, dummy_wav, SAMPLE_RATE, format="WAV", subtype="PCM_16")
            return out_io.getvalue()

        final_waveform = np.concatenate(audio_parts)
        out_io = io.BytesIO()
        sf.write(out_io, final_waveform, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        return out_io.getvalue()
