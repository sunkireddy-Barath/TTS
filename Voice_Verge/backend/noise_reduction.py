import os
import io
import numpy as np
import librosa
import soundfile as sf
import tempfile
import noisereduce as nr

def is_noisy(audio_bytes: bytes, threshold_db=-45.0) -> bool:
    """
    Detects if the audio file contains significant background noise.
    Uses RMS energy to estimate the noise floor.
    """
    try:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
        if len(y) == 0:
            return False
            
        S, phase = librosa.magphase(librosa.stft(y))
        rms = librosa.feature.rms(S=S)[0]
        
        noise_floor_rms = np.percentile(rms, 5)
        
        if noise_floor_rms < 1e-7:
            return False
            
        noise_floor_db = 20 * np.log10(noise_floor_rms)
        print(f"[Noise Detection] Noise floor estimated at: {noise_floor_db:.2f} dB")
        return noise_floor_db > threshold_db
    except Exception as e:
        print(f"[Noise Detection Error] {e}")
        return True

def apply_mossformer_enhancement(
    audio_bytes: bytes,
    trim_silence: bool = True,
    force_process: bool = False
) -> bytes:
    """
    Applies Noisereduce (spectral gating) to remove background noise without affecting voice quality.
    (Kept function name as apply_mossformer_enhancement for backward compatibility)
    """
    noisy = force_process or is_noisy(audio_bytes, threshold_db=-45.0)
    
    if not noisy and not trim_silence:
        print("[Noisereduce] Audio is clear and no silence trim requested. Bypassing.")
        return audio_bytes

    try:
        if noisy:
            print("[Noisereduce] Noisy audio detected. Applying noise reduction...")
            arr_out, out_sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
            
            # Apply stationary noise reduction (prop_decrease controls how aggressive it is)
            arr_out = nr.reduce_noise(y=arr_out, sr=out_sr, prop_decrease=0.8, stationary=False)
        else:
            print("[Noisereduce] Audio is clear. Bypassing noise reduction.")
            arr_out, out_sr = sf.read(io.BytesIO(audio_bytes))
            if len(arr_out.shape) > 1:
                arr_out = arr_out.mean(axis=1)
            
        if trim_silence:
            print("[Noisereduce] Trimming blank silences...")
            arr_out, _ = librosa.effects.trim(arr_out, top_db=40)
            
        if np.max(np.abs(arr_out)) < 1e-6:
            return audio_bytes

        buf = io.BytesIO()
        sf.write(buf, arr_out, out_sr, format="WAV", subtype="PCM_16")
        return buf.getvalue()
        
    except Exception as e:
        print(f"[Noisereduce] CRITICAL ERROR: {e}")
        return audio_bytes
