"""
voice_design.py
Orchestrates the Voice Design pipeline using the real OmniVoice API.

Architecture (Unified for all versions):
    user input
        ↓
    Expression Engine → inject [expression-tag] into text
        ↓
    Tag Parser (split text into emotion segments, using global emotion as fallback)
        ↓
    Emotion Engine → EmotionParams (pitch_hint, style_hint, speed)
        ↓
    EmotionEngine.build_instruct() → "female, high pitch, British accent"
        ↓
    OmniVoice model.generate(text=..., instruct=..., speed=...)
        ↓
    Audio WAV bytes
"""

import io
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
      - Multi-emotion tagged synthesis seamlessly unified with single-emotion synthesis.
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
        Unifies V1, V2, and V3:
          - Applies expression from dropdown globally.
          - Parses inline emotion tags, falling back to emotion dropdown.
        """
        lang_code = LanguageRouter.resolve(language)
        accent    = LanguageRouter.get_accent(language)

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

        # 2. Treat everything as multi-segment (seamlessly handles single segments).
        # We pass `emotion` so TagParser can use it for untagged segments!
        out_bytes = self._generate_multi_segment(
            final_text, gender, age, accent, emotion, num_step
        )
        # Apply MossFormer2 to the generated output to remove trailing silence
        return apply_mossformer_enhancement(out_bytes, force_process=False)

    def _generate_multi_segment(
        self,
        text: str,
        gender: str,
        age: int,
        accent: str,
        fallback_emotion: str,
        num_step: int,
        max_attempts: int = 4
    ) -> bytes:
        """
        Parse <emotion> blocks → synthesise each with its emotion instruct
        → concatenate with 200 ms silence between segments.
        """
        segments    = TagParser.parse(text, default_emotion=fallback_emotion)
        audio_parts = []

        request_seed = random.randint(1, 999999)

        for idx, seg in enumerate(segments):
            is_last = (idx == len(segments) - 1)
            
            # 1. Resolve parameters for THIS specific chunk
            params = EmotionEngine.resolve(seg.emotion, gender, age)
            instruct = EmotionEngine.build_instruct(gender, age, params, accent)
            
            # We strip trailing punctuation for isolated multi-segment generation so it doesn't leave gaps
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

            for attempt in range(max_attempts):
                if attempt > 0:
                    print(f" Expression not detected in segment {idx+1}. Retrying (Attempt {attempt+1}/{max_attempts})...")
                    random.seed(request_seed + attempt)
                    np.random.seed(request_seed + attempt)
                    torch.manual_seed(request_seed + attempt)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed_all(request_seed + attempt)

                wav_bytes = self.engine.synthesize_voice_design(
                    text=seg_text,
                    instruct=instruct,
                    speed=params.speed,
                    num_step=num_step,
                )

                is_valid, current_score = AudioVerifier.verify_expression(wav_bytes, tags_to_verify)
                
                if current_score > best_score:
                    best_score = current_score
                    best_wav_bytes = wav_bytes
                    
                if is_valid:
                    break
            
            if not is_valid:
                print(f" Exhausted attempts for segment {idx+1}. Using best scored chunk ({best_score:.4f}).")

            if best_wav_bytes:
                waveform, sr = torchaudio.load(io.BytesIO(best_wav_bytes))
                audio_parts.append(waveform.squeeze().numpy())
            
            if not is_last and best_wav_bytes:
                silence_samples = int(sr * 0.2)
                audio_parts.append(np.zeros(silence_samples, dtype=np.float32))

        if not audio_parts:
            # If no audio was generated dynamically, we just return empty array
            dummy_wav = np.zeros(16000, dtype=np.float32)
            out_io = io.BytesIO()
            sf.write(out_io, dummy_wav, 24000, format='WAV', subtype='PCM_16')
            return out_io.getvalue()

        final_waveform = np.concatenate(audio_parts)
        out_io = io.BytesIO()
        sf.write(out_io, final_waveform, sr, format='WAV', subtype='PCM_16')
        return out_io.getvalue()
