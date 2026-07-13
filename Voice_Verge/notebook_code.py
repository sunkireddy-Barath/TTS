# ── Cell 1: Environment Setup ──────────────────────────────────────────────────
import sys, os, torch, subprocess
# ── 1. Clone GitHub Repository ────────────────────────────────────────────────
if not os.path.exists('/content/TTS'):
  print("Cloning repository...")
  subprocess.run(['git', 'clone', 'https://github.com/sunkireddy-Barath/TTS.git', '/content/TTS'])
else:
  print("Repository already cloned.")

# ── 2. Locate Voice_Verge project folder ───────────────────────────────────────
DRIVE_PROJECT_PATH = '/content/TTS/Voice_Verge'

if not os.path.isdir(DRIVE_PROJECT_PATH):
  raise FileNotFoundError(
    f'\nVoice_Verge not found at: {DRIVE_PROJECT_PATH}\n'
    ' Please make sure you uploaded the Voice_Verge folder directly to your Google Drive root.'
  )
print(f'Project found: {DRIVE_PROJECT_PATH}')

BACKEND_DIR  = os.path.join(DRIVE_PROJECT_PATH, 'backend')
CHECKPOINT_DIR = os.path.join(DRIVE_PROJECT_PATH, 'checkpoints')
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# ── 3. Add backend to Python path ──────────────────────────────────────────────
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# ── 4. Environment variables ───────────────────────────────────────────────────
os.environ['HF_HOME']  = CHECKPOINT_DIR
os.environ['PORT']   = '8000'
os.environ['ALLOWED_ORIGINS'] = '*'

# ── 5. GPU check ───────────────────────────────────────────────────────────────
if torch.cuda.is_available():
  gpu  = torch.cuda.get_device_name(0)
  vram = torch.cuda.get_device_properties(0).total_memory / 1e9
  print(f'GPU: {gpu}  ({vram:.1f} GB VRAM)')
else:
  print('No GPU — go to Runtime → Change runtime type → T4 GPU')

print(f'\nBackend  : {BACKEND_DIR}')
print(f'HF Cache : {CHECKPOINT_DIR}')
print(f'Python {sys.version.split()[0]}  |  PyTorch {torch.__version__}')
print('\nCell 1 complete.\n')


# --------
# ── Cell 2: Install OmniVoice & Dependencies ───────────────────────────────────
import subprocess, sys
# ── OmniVoice — the TTS engine ────────────────────────────────────────────────
# From PyPI (stable) — recommended
OMNIVOICE_INSTALL = 'omnivoice'
# From GitHub latest (uncomment to use):
# OMNIVOICE_INSTALL = 'git+https://github.com/k2-fsa/OmniVoice.git'
print(f' Installing OmniVoice ({OMNIVOICE_INSTALL})…')
r = subprocess.run(
  [sys.executable, '-m', 'pip', 'install', '-q', OMNIVOICE_INSTALL],
  capture_output=True, text=True
)
print('omnivoice installed.' if r.returncode == 0 else f'{r.stderr[-400:]}')
# ── Rust/Cargo dependency for MossFormer2_SE_48K ────────────────────────────
print(' Installing Rust (required for MossFormer2_SE_48K)...')
subprocess.run(['apt-get', 'install', '-y', 'cargo'], capture_output=True)
# ── Backend dependencies ──────────────────────────────────────────────────────
PACKAGES = [
  'transformers>=4.40.0',
  'accelerate>=0.29.0',
  'fastapi>=0.111.0',
  'uvicorn[standard]>=0.29.0',
  'python-multipart>=0.0.9',
  'soundfile>=0.12.1',
  'pyngrok>=7.1.0',
  'pydantic>=2.7.0',
  'modelscope>=1.15.0',
  'numpy<2.0.0',
  'deepfilternet',
]
print('\nInstalling backend dependencies…')
failed = []
for pkg in PACKAGES:
  r = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-q', pkg],
    capture_output=True, text=True
  )
  status = '' if r.returncode == 0 else ''
  print(f' {status}  {pkg}')
  if r.returncode != 0:
    failed.append(pkg)
if failed:
  print(f'\n{len(failed)} failed: {failed}')
else:
  print('\nAll dependencies installed.')


# --------
# ── Cell 3: Verify OmniVoice Import ───────────────────────────────────────────
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
import sys, os

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# ── OmniVoice import test ─────────────────────────────────────────────────────
try:
  from omnivoice import OmniVoice
  print(f'OmniVoice importable: {OmniVoice}')
except ValueError as ve:
  if "numpy" in str(ve).lower() or "numpy.dtype size changed" in str(ve):
    print("\nNUMPY CONFLICT DETECTED!")
    print(" This happens because Colab comes with a different Numpy version.")
    print(" FIX: Go to the top menu and click: Runtime -> Restart session")
    print(" Then run THIS cell (Cell 3) again! Do not run Cell 1 & 2 again.\n")
    raise ve
except ImportError as e:
  print(f'OmniVoice import failed: {e}')
  print(' Run Cell 2 first.')

# ── Backend module verification ───────────────────────────────────────────────
required = [
  'omnivoice_engine.py', 'emotion_engine.py', 'expression_engine.py',
  'tag_parser.py', 'language_router.py', 'voice_design.py',
  'voice_clone.py', 'main.py',
]
print(f'\nBackend module check ({BACKEND_DIR}):')
missing = []
for f in required:
  path = os.path.join(BACKEND_DIR, f)
  if os.path.isfile(path):
    size = os.path.getsize(path)
    print(f' {f:<35} {size:>8,} bytes')
  else:
    print(f' {f}  ← MISSING')
    missing.append(f)

if missing:
  print(f'\nWARNING: {len(missing)} backend files missing: {missing}\n')
  print('  Make sure you have uploaded these files to your Google Drive backend folder!')
  print('  If voice_design.py is missing, the server will crash in Cell 7.\n')
else:
  print('\nAll backend modules found.  Cell 3 complete.')

# --------
# ── Cell 4: Download OmniVoice Model ──────────────────────────────────────────
import os
from huggingface_hub import snapshot_download

MODEL_ID   = 'k2-fsa/OmniVoice'
CHECKPOINT_DIR = '/content/TTS/Voice_Verge/checkpoints'
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.environ['HF_HOME'] = CHECKPOINT_DIR

# Check if model already cached
model_marker = os.path.join(CHECKPOINT_DIR, 'hub', 'models--k2-fsa--OmniVoice')
if os.path.isdir(model_marker):
  print(f'OmniVoice already cached at: {model_marker}')
  print(' Skipping download (delete the folder to force re-download).')
else:
  print(f' Downloading {MODEL_ID} → {CHECKPOINT_DIR}')
  print(' This may take 5–20 minutes (model is several GB)…')

  try:
    path = snapshot_download(
    repo_id=MODEL_ID,
    cache_dir=CHECKPOINT_DIR,
    ignore_patterns=['*.msgpack', '*.h5', 'flax_model*', 'tf_model*'],
    )
    total_gb = sum(
    os.path.getsize(os.path.join(dp, f))
    for dp, _, files in os.walk(path)
    for f in files
    ) / 1e9
    print(f'\nModel downloaded: {path}')
    print(f' Total size: {total_gb:.2f} GB')
  except Exception as e:
    print(f'\nDownload failed: {e}')

print('\nCell 4 complete.')


# --------
# ── Cell 5: Load OmniVoice Model ──────────────────────────────────────────────
import sys, os, time, torch

BACKEND_DIR  = '/content/TTS/Voice_Verge/backend'
CHECKPOINT_DIR = '/content/TTS/Voice_Verge/checkpoints'
for d in [BACKEND_DIR]:
  if d not in sys.path: sys.path.insert(0, d)

os.environ['HF_HOME'] = CHECKPOINT_DIR

from omnivoice_engine import OmniVoiceEngine

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
dtype  = torch.float16 if torch.cuda.is_available() else torch.float32

print(f'Loading OmniVoice on {device} ({dtype})…')
t0 = time.time()

engine = OmniVoiceEngine.get_instance()

try:
  engine.load(
    model_id='k2-fsa/OmniVoice',
    device_map=device,
    dtype=dtype,
  )

  elapsed = time.time() - t0
  print(f'\nOmniVoice loaded in {elapsed:.1f}s')

  print(f' Device  : {engine.device}')
  print(f' Loaded  : {engine.loaded}')

  if torch.cuda.is_available():
    used  = torch.cuda.memory_allocated() / 1e9
    total = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f' VRAM used : {used:.2f} GB / {total:.1f} GB')

  print('\nCell 5 complete.')
except KeyboardInterrupt:
  print('\n\nModel loading was manually interrupted (Stop button was clicked)!')
  print('  Please run this cell again and let the download finish without stopping it.\n')
  import sys; sys.exit(1)
except Exception as e:
  print(f'\nFailed to load model: {e}\n')
  import sys; sys.exit(1)

# --------
# ── Cell 6: Test Audio Pipeline ───────────────────────────────────────────────
import sys, os
BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

import io, time
import soundfile as sf
from IPython.display import Audio, display
from omnivoice_engine import OmniVoiceEngine
from voice_design import VoiceDesignService
from voice_clone import VoiceCloneService

engine = OmniVoiceEngine.get_instance()
vd = VoiceDesignService(engine)
vc = VoiceCloneService(engine)

print('\nStarting Audio Tests (Voice Design)...')

# ── V1 - Emotion Only
print('\nV1 (Female, Happy, No Expression):')
t0 = time.time()
w1_f = vd.generate("Hello! This is a version one test with a female voice.", 'en-US', 'female', 25, 'happy', 'none', 1)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(w1_f))[0], rate=24000))

# ── V2 - Emotion + Expression Dropdown
print('\nV2 (Female, Neutral, Giggle Expression):')
t0 = time.time()
w2_f = vd.generate("I just won the match today.", 'en-GB', 'female', 28, 'neutral', 'giggle', 2)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(w2_f))[0], rate=24000))

# ── V3 - Inline Tags
print('\nV3 (Male, Multi-Emotion Inline Tags):')
t0 = time.time()
w3_m = vd.generate("<angry>Get out of here!</angry> <calm>Just kidding, you can stay.</calm>", 'en-US', 'male', 30, 'neutral', 'none', 3)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(w3_m))[0], rate=24000))

print('\nStarting Audio Tests (Voice Cloning)...')

# We will use w2_f as the reference audio for Voice Cloning
print('\nV1 (Emotion Only):')
t0 = time.time()
vc1 = vc.generate("Hello, I am testing voice cloning now.", 'en-US', reference_audio_bytes=w2_f, gender='female', age=28, emotion='sad', expression='none', version=1)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(vc1))[0], rate=24000))

print('\nV2 (Emotion + Expression Dropdown):')
t0 = time.time()
vc2 = vc.generate("I can sigh like this.", 'en-US', reference_audio_bytes=w2_f, gender='female', age=28, emotion='neutral', expression='sigh', version=2)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(vc2))[0], rate=24000))

print('\nV3 (Inline Tags):')
t0 = time.time()
vc3 = vc.generate("<happy>I am so happy!</happy> <whisper>But keep it a secret.</whisper>", 'en-US', reference_audio_bytes=w2_f, gender='female', age=28, emotion='neutral', expression='none', version=3)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(vc3))[0], rate=24000))

print('\nAll tests complete!\n')

# --------
# ── Cell 6: Test Audio Pipeline ───────────────────────────────────────────────
import sys, os
BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

import io, time
import soundfile as sf
from IPython.display import Audio, display
from omnivoice_engine import OmniVoiceEngine
from voice_design import VoiceDesignService
from voice_clone import VoiceCloneService

engine = OmniVoiceEngine.get_instance()
vd = VoiceDesignService(engine)
vc = VoiceCloneService(engine)

print('\nStarting Audio Tests (Voice Design)...')

# ── V1 - Emotion Only
print('\nV1 (Female, Happy, No Expression):')
t0 = time.time()
w1_f = vd.generate("Hello! This is a version one test with a female voice.", 'en-US', 'female', 25, 'happy', 'none', 1)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(w1_f))[0], rate=24000))

# ── V2 - Emotion + Expression Dropdown
print('\nV2 (Female, Neutral, Giggle Expression):')
t0 = time.time()
w2_f = vd.generate("I just won the match today.", 'en-GB', 'female', 28, 'neutral', 'giggle', 2)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(w2_f))[0], rate=24000))

# ── V3 - Inline Tags
print('\nV3 (Male, Multi-Emotion Inline Tags):')
t0 = time.time()
w3_m = vd.generate("<angry>Get out of here!</angry> <calm>Just kidding, you can stay.</calm>", 'en-US', 'male', 30, 'neutral', 'none', 3)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(w3_m))[0], rate=24000))

print('\nStarting Audio Tests (Voice Cloning)...')

# We will use w2_f as the reference audio for Voice Cloning
print('\nV1 (Emotion Only):')
t0 = time.time()
vc1 = vc.generate("Hello, I am testing voice cloning now.", 'en-US', reference_audio_bytes=w2_f, gender='female', age=28, emotion='sad', expression='none', version=1)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(vc1))[0], rate=24000))

print('\nV2 (Emotion + Expression Dropdown):')
t0 = time.time()
vc2 = vc.generate("I can sigh like this.", 'en-US', reference_audio_bytes=w2_f, gender='female', age=28, emotion='neutral', expression='sigh', version=2)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(vc2))[0], rate=24000))

print('\nV3 (Inline Tags):')
t0 = time.time()
vc3 = vc.generate("<happy>I am so happy!</happy> <whisper>But keep it a secret.</whisper>", 'en-US', reference_audio_bytes=w2_f, gender='female', age=28, emotion='neutral', expression='none', version=3)
print(f' Generated in {time.time()-t0:.2f}s')
display(Audio(sf.read(io.BytesIO(vc3))[0], rate=24000))

print('\nAll tests complete!\n')

# --------
