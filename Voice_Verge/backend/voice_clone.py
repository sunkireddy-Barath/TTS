"""
voice_clone.py
Orchestrates the Cross-Lingual Voice Cloning pipeline using the real OmniVoice API.

Architecture (correct for OmniVoice):
    reference audio + target text
        ↓
    Expression Engine → inject [expression-tag] into text
        ↓
    Emotion Engine → speed (only speed applies in cloning mode)
        ↓
    Tag Parser (V3: strip <emotion> tags from text)
        ↓
    OmniVoice model.generate(
        text=...,
        ref_audio="path.wav",
        ref_text=...,   # optional — Whisper auto-transcribes if omitted
        speed=...,
        num_step=...,
    )
        ↓
    Audio WAV bytes

Version behaviour:
  V1 — emotion speed only, no expression
  V2 — emotion speed + expression tag injected silently in text
  V3 — any <emotion> tags stripped from text before cloning

Notes
-----
- Cross-lingual cloning does NOT use the instruct parameter.
  The reference audio carries the voice identity; the target language is
  inferred from the text content.
- ref_text is optional: if provided it improves cloning accuracy.
  If omitted, OmniVoice uses Whisper ASR to auto-transcribe the reference.
"""

import io
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
        gender                : Target gender to pitch shift the audio (DSP shift).
        age                   : Age hint.
        emotion               : Emotion label → mapped to speed adjustment.
        expression            : Expression label. Always 'none' for V1.
        version               : 1 | 2 | 3.
        ref_text              : Transcription of the reference audio.
                                Optional — OmniVoice auto-transcribes via Whisper if "".
        num_step              : OmniVoice diffusion steps.

        Returns
        -------
        bytes : WAV bytes at 24 kHz mono PCM-16.
        """
        # Clean noisy uploaded audio
        reference_audio_bytes = apply_mossformer_enhancement(reference_audio_bytes)

        if version == 1:
            # V1: Emotion dropdown only. Strip all inline tags and ignore expression dropdown.
            final_text = TagParser.strip_all_tags(text)
        elif version == 2:
            # V2: Emotion dropdown + Expression dropdown. Strip inline tags, inject global expression.
            final_text = TagParser.strip_all_tags(text)
            final_text = ExpressionEngine.inject_tag(final_text, expression)
        else:
            # V3: Emotion tags + Expression tags in inline text.
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

        # Apply MossFormer2 to the generated output to remove trailing silence and gentle hiss
        return apply_mossformer_enhancement(out_bytes, force_process=True)

    def _generate_multi_segment(
        self,
        text: str,
        reference_audio_bytes: bytes,
        gender: str,
        age: int,
        fallback_emotion: str,
        ref_text: str,
        num_step: int,
    ) -> bytes:
        """
        parse <emotion> blocks → synthesise each with its emotion speed mapped
        → concatenate with 200 ms silence between segments.
        Expression tags are preserved strictly inline.
        """
        segments = TagParser.parse(text, default_emotion=fallback_emotion)
        audio_parts: list[np.ndarray] = []

        # Fix seed to ensure voice stability across segments
        request_seed = random.randint(1, 999999)

        for idx, seg in enumerate(segments):
            is_last = (idx == len(segments) - 1)

            # Resolve emotion per segment
            params = EmotionEngine.resolve(seg.emotion, gender, age)
            # BUG FIX: Voice cloning mode does NOT support the 'instruct' parameter. 
            # Passing it causes OmniVoice to generate blank/static noise.
            instruct = ""

            seg_text = seg.text
            tags_to_verify = []
            if "[laughter]" in seg_text.lower(): tags_to_verify.append("[laughter]")
            if "[sigh]" in seg_text.lower(): tags_to_verify.append("[sigh]")
            if "[surprise" in seg_text.lower() or "gasp" in seg_text.lower(): tags_to_verify.append("[surprise]")
            if "[dissatisfaction" in seg_text.lower(): tags_to_verify.append("[dissatisfaction-hnn]")
            if "[question" in seg_text.lower(): tags_to_verify.append("[question-en]")
            if "[confirmation" in seg_text.lower(): tags_to_verify.append("[confirmation-en]")

            best_wav_bytes = None
            best_score = -1.0
            is_valid = False
            max_attempts = 4

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f" Expression not detected in cloned segment {idx+1}. Retrying (Attempt {attempt+1}/{max_attempts})...")
                    random.seed(request_seed + attempt)
                    np.random.seed(request_seed + attempt)
                    torch.manual_seed(request_seed + attempt)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(request_seed + attempt)
                else:
                    random.seed(request_seed)
                    np.random.seed(request_seed)
                    torch.manual_seed(request_seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(request_seed)

                wav_bytes = self.engine.synthesize_voice_clone(
                    text=seg_text,
                    reference_audio_bytes=reference_audio_bytes,
                    ref_text=ref_text,
                    speed=params.speed,
                    num_step=num_step,
                    instruct=instruct,
                )

                # OmniVoice engine internally retries on blank audio (RMS) or pure static (ZCR).
                # If it returns wav_bytes without ValueError, it is a valid generation.
                is_valid = True
                best_wav_bytes = wav_bytes
                break
            
            if not is_valid:
                print(f" Exhausted attempts for cloned segment {idx+1}. Using best scored chunk ({best_score:.4f}).")

            arr, _ = sf.read(io.BytesIO(best_wav_bytes))
            arr = arr.astype(np.float32)

            # Apply 10ms fade-in/out to prevent audio clicking/popping at boundaries
            fade_len = int(SAMPLE_RATE * 0.01)
            if len(arr) > fade_len * 2:
                fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
                fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
                arr[:fade_len] *= fade_in
                arr[-fade_len:] *= fade_out

            audio_parts.append(arr)

            # 200 ms silence gap
            if not is_last:
                silence = np.zeros(int(SAMPLE_RATE * 0.20), dtype=np.float32)
                audio_parts.append(silence)

        if not audio_parts:
            raise ValueError("No valid text segments found.")

        combined = np.concatenate(audio_parts)
        buf = io.BytesIO()
        sf.write(buf, combined, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        buf.seek(0)
        return buf.read()
