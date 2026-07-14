# ── Cell 1: Environment Setup ──────────────────────────────────────────────────
import sys, os, subprocess

# ── 1. Clone GitHub Repository ────────────────────────────────────────────────
if not os.path.exists('/content/TTS'):
  print("⬇️  Cloning repository...")
  result = subprocess.run(
    ['git', 'clone', 'https://github.com/sunkireddy-Barath/TTS.git', '/content/TTS'],
    capture_output=True, text=True
  )
  if result.returncode != 0:
    print(f"❌ Git clone failed:\n{result.stderr}")
    raise RuntimeError("Repository clone failed.")
  print("✅  Repository cloned successfully.")
else:
  print("✅  Repository already cloned.")

# ── 2. Locate Voice_Verge project folder ──────────────────────────────────────
DRIVE_PROJECT_PATH = '/content/TTS/Voice_Verge'

if not os.path.isdir(DRIVE_PROJECT_PATH):
  raise FileNotFoundError(
    f'\n❌  Voice_Verge not found at: {DRIVE_PROJECT_PATH}\n'
    '    Make sure the repo was cloned correctly.'
  )
print(f'✅  Project found: {DRIVE_PROJECT_PATH}')

BACKEND_DIR    = os.path.join(DRIVE_PROJECT_PATH, 'backend')
CHECKPOINT_DIR = os.path.join(DRIVE_PROJECT_PATH, 'checkpoints')
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# ── 3. Add backend to Python path ─────────────────────────────────────────────
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# ── 4. Environment variables ───────────────────────────────────────────────────
os.environ['HF_HOME']         = CHECKPOINT_DIR
os.environ['PORT']            = '8000'
os.environ['ALLOWED_ORIGINS'] = '*'

# ── 5. GPU check ──────────────────────────────────────────────────────────────
import torch
if torch.cuda.is_available():
  gpu  = torch.cuda.get_device_name(0)
  vram = torch.cuda.get_device_properties(0).total_memory / 1e9
  print(f'✅  GPU: {gpu}  ({vram:.1f} GB VRAM)')
else:
  print('⚠️  No GPU detected!')
  print('    👉 Go to Runtime → Change runtime type → Hardware accelerator → T4 GPU')

print(f'\n📁  Backend  : {BACKEND_DIR}')
print(f'📁  HF Cache : {CHECKPOINT_DIR}')
print(f'🐍  Python {sys.version.split()[0]}  |  PyTorch {torch.__version__}')
print('\n✅  Cell 1 complete.\n')


# ----


# ── Cell 2: Install OmniVoice & Dependencies ──────────────────────────────────
import subprocess, sys

# ── Step 0: Pin numpy BEFORE everything else to prevent binary conflict ───────
print('🔧  Pinning numpy==1.26.4 (prevents binary conflict after restart)…')
r = subprocess.run(
  [sys.executable, '-m', 'pip', 'install', '-q', '--force-reinstall', 'numpy==1.26.4'],
  capture_output=True, text=True
)
print('✅  numpy pinned.' if r.returncode == 0 else f'❌  numpy pin failed: {r.stderr[-300:]}')

# ── Step 1: OmniVoice TTS engine ─────────────────────────────────────────────
OMNIVOICE_INSTALL = 'omnivoice'
print(f'\n⬇️  Installing OmniVoice ({OMNIVOICE_INSTALL})…')
r = subprocess.run(
  [sys.executable, '-m', 'pip', 'install', '-q', OMNIVOICE_INSTALL],
  capture_output=True, text=True
)
print('✅  omnivoice installed.' if r.returncode == 0 else f'❌  {r.stderr[-400:]}')

# ── Step 2: All backend dependencies ─────────────────────────────────────────
PACKAGES = [
  'transformers>=4.40.0',
  'accelerate>=0.29.0',
  'fastapi>=0.111.0',
  'uvicorn[standard]>=0.29.0',
  'python-multipart>=0.0.9',
  'soundfile>=0.12.1',
  'pyngrok>=7.1.0',
  'pydantic>=2.7.0',
  'librosa>=0.10.0',      # required by voice_design.py and noise_reduction.py
  'torchaudio',           # required by voice_design.py (torchaudio.load)
  'noisereduce>=3.0.0',   # required by noise_reduction.py
  'modelscope>=1.15.0',
  'numpy<2.0.0',          # keep numpy pinned at 1.x
]

print('\n📦  Installing backend dependencies…')
failed = []
for pkg in PACKAGES:
  r = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-q', pkg],
    capture_output=True, text=True
  )
  status = '✅' if r.returncode == 0 else '❌'
  print(f'  {status}  {pkg}')
  if r.returncode != 0:
    failed.append((pkg, r.stderr[-200:]))

if failed:
  print(f'\n⚠️  {len(failed)} package(s) failed:')
  for pkg, err in failed:
    print(f'   ❌ {pkg}: {err}')
else:
  print('\n✅  All dependencies installed.')

print('\n⚠️  IMPORTANT: Now go to Runtime → Restart session')
print('   Then run Cell 3 ONLY (skip Cells 1 & 2).\n')
print('✅  Cell 2 complete.\n')


# ----


# ── Cell 3: Verify OmniVoice Import ───────────────────────────────────────────
import subprocess, sys, os
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# ── Pre-flight: numpy binary compatibility check ──────────────────────────────
def _check_and_fix_numpy():
  try:
    import numpy as np
    _ = np.zeros(1)
    print(f'✅  numpy {np.__version__} OK')
    return True
  except ValueError as ve:
    if 'numpy.dtype size changed' in str(ve) or 'numpy' in str(ve).lower():
      print('\n🔧 numpy binary conflict — force-reinstalling numpy==1.26.4…')
      subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-q', '--force-reinstall', 'numpy==1.26.4'],
        check=True
      )
      print('✅  numpy reinstalled. Restarting runtime…')
      try:
        import IPython
        IPython.Application.instance().kernel.do_shutdown(True)
      except Exception:
        pass
      try:
        from google.colab import runtime
        runtime.unassign()
      except Exception:
        pass
      return False
    raise

if not _check_and_fix_numpy():
  raise SystemExit('Runtime restart triggered — re-run Cell 3 after restart.')

# ── OmniVoice import test ─────────────────────────────────────────────────────
try:
  from omnivoice import OmniVoice
  print(f'✅  OmniVoice importable: {OmniVoice}')
except ValueError as ve:
  if 'numpy.dtype size changed' in str(ve) or 'numpy' in str(ve).lower():
    print('\n❌  numpy conflict STILL present.')
    print('    Try: Runtime → Disconnect and delete runtime, then re-run all cells.')
  else:
    raise
except ImportError as e:
  print(f'❌  OmniVoice import failed: {e}')
  print('    Run Cell 2 first, then restart.')

# ── Backend module verification ───────────────────────────────────────────────
required = [
  'omnivoice_engine.py', 'emotion_engine.py', 'expression_engine.py',
  'tag_parser.py', 'language_router.py', 'voice_design.py',
  'voice_clone.py', 'audio_verifier.py', 'noise_reduction.py', 'main.py',
]
print(f'\n📄  Backend module check ({BACKEND_DIR}):')
missing = []
for f in required:
  path = os.path.join(BACKEND_DIR, f)
  if os.path.isfile(path):
    size = os.path.getsize(path)
    print(f'  ✅  {f:<35} {size:>8,} bytes')
  else:
    print(f'  ❌  {f}  ← MISSING')
    missing.append(f)

if missing:
  print(f'\n⚠️  WARNING: {len(missing)} backend file(s) missing: {missing}')
else:
  print('\n✅  All backend modules found.  Cell 3 complete.')


# ----


# ── Cell 4: Download OmniVoice Model ──────────────────────────────────────────
import os, subprocess, sys

os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'hf_transfer'], check=True)
print('✅  hf_transfer enabled (faster parallel download)')

from huggingface_hub import snapshot_download

MODEL_ID       = 'k2-fsa/OmniVoice'
CHECKPOINT_DIR = '/content/TTS/Voice_Verge/checkpoints'
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.environ['HF_HOME'] = CHECKPOINT_DIR

model_marker = os.path.join(CHECKPOINT_DIR, 'hub', 'models--k2-fsa--OmniVoice')
if os.path.isdir(model_marker):
  print(f'\n✅  OmniVoice already cached at: {model_marker}')
  print('   Skipping download (delete the folder to force re-download).')
else:
  print(f'\n⬇️  Downloading {MODEL_ID} → {CHECKPOINT_DIR}')
  print('   hf_transfer active — 3–5× faster. May still take 5–15 minutes…\n')
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
    print(f'\n✅  Model downloaded: {path}')
    print(f'   Total size: {total_gb:.2f} GB')
  except Exception as e:
    print(f'\n❌  Download failed: {e}')
    raise

print('\n✅  Cell 4 complete.')


# ----


# ── Cell 5: Load OmniVoice Model ──────────────────────────────────────────────
import sys, os, time, torch

BACKEND_DIR    = '/content/TTS/Voice_Verge/backend'
CHECKPOINT_DIR = '/content/TTS/Voice_Verge/checkpoints'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

os.environ['HF_HOME'] = CHECKPOINT_DIR

from omnivoice_engine import OmniVoiceEngine

# Reset singleton so re-running this cell always reloads cleanly
OmniVoiceEngine._instance = None

device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
dtype  = torch.float16 if torch.cuda.is_available() else torch.float32

print(f'🔄  Loading OmniVoice on {device} ({dtype})…')
print('   First load: 1–3 min | Subsequent: ~30s')
t0 = time.time()

engine = OmniVoiceEngine.get_instance()

try:
  engine.load(
    model_id='k2-fsa/OmniVoice',
    device_map=device,
    dtype=dtype,
  )

  elapsed = time.time() - t0
  print(f'\n✅  OmniVoice loaded in {elapsed:.1f}s')
  print(f'   Device  : {engine.device}')
  print(f'   Loaded  : {engine.loaded}')

  if torch.cuda.is_available():
    used  = torch.cuda.memory_allocated() / 1e9
    total = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f'   VRAM    : {used:.2f} GB used / {total:.1f} GB total')

  print('\n✅  Cell 5 complete.')

except KeyboardInterrupt:
  print('\n\n⚠️  Model loading interrupted! Run Cell 5 again.')
except Exception as e:
  import traceback
  print(f'\n❌  Failed to load model: {e}')
  traceback.print_exc()
  raise


# ----


# ── Cell 6: Test Audio Pipeline ───────────────────────────────────────────────
import sys, os, io, time
import soundfile as sf
from IPython.display import Audio, display

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

from omnivoice_engine import OmniVoiceEngine
from voice_design import VoiceDesignService
from voice_clone import VoiceCloneService

engine = OmniVoiceEngine.get_instance()
if not engine.loaded:
  raise RuntimeError('❌ Engine not loaded! Run Cell 5 first.')

vd = VoiceDesignService(engine)
vc = VoiceCloneService(engine)

def play(wav_bytes):
  arr, sr = sf.read(io.BytesIO(wav_bytes))
  print(f'   ▶ Duration: {len(arr)/sr:.2f}s')
  display(Audio(arr, rate=sr))

# ── Voice Design Tests ────────────────────────────────────────────────────────
print('\n🧪  Voice Design Tests\n' + '─'*50)

w1_f = w2_f = w3_m = None

print('\n1️⃣  V1 — Female, Happy, No Expression:')
try:
  t0 = time.time()
  w1_f = vd.generate(
    "Hello! This is a version one test with a female voice.",
    'en-US', 'female', 25, 'happy', 'none', version=1
  )
  print(f'   ✅ Generated in {time.time()-t0:.2f}s')
  play(w1_f)
except Exception as e:
  print(f'   ❌ Failed: {e}')

print('\n2️⃣  V2 — Female, Neutral, Giggle Expression:')
try:
  t0 = time.time()
  w2_f = vd.generate(
    "I just won the match today.",
    'en-GB', 'female', 28, 'neutral', 'giggle', version=2
  )
  print(f'   ✅ Generated in {time.time()-t0:.2f}s')
  play(w2_f)
except Exception as e:
  print(f'   ❌ Failed: {e}')

print('\n3️⃣  V3 — Male, Multi-Emotion Inline Tags:')
try:
  t0 = time.time()
  w3_m = vd.generate(
    "<angry>Get out of here!</angry> <calm>Just kidding, you can stay.</calm>",
    'en-US', 'male', 30, 'neutral', 'none', version=3
  )
  print(f'   ✅ Generated in {time.time()-t0:.2f}s')
  play(w3_m)
except Exception as e:
  print(f'   ❌ Failed: {e}')

# ── Voice Cloning Tests ───────────────────────────────────────────────────────
print('\n🧪  Voice Cloning Tests (reference = V2 output)\n' + '─'*50)

ref_audio = w2_f or w1_f
if ref_audio is None:
  print('⚠️  No reference audio — skipping clone tests. Fix Voice Design tests first.')
else:
  print('\n1️⃣  VC-V1 — Emotion Only (Sad):')
  try:
    t0 = time.time()
    vc1 = vc.generate(
      "Hello, I am testing voice cloning now.", 'en-US',
      reference_audio_bytes=ref_audio,
      gender='female', age=28, emotion='sad', expression='none', version=1
    )
    print(f'   ✅ Generated in {time.time()-t0:.2f}s')
    play(vc1)
  except Exception as e:
    print(f'   ❌ Failed: {e}')

  print('\n2️⃣  VC-V2 — Emotion + Sigh Expression:')
  try:
    t0 = time.time()
    vc2 = vc.generate(
      "I can sigh like this.", 'en-US',
      reference_audio_bytes=ref_audio,
      gender='female', age=28, emotion='neutral', expression='sigh', version=2
    )
    print(f'   ✅ Generated in {time.time()-t0:.2f}s')
    play(vc2)
  except Exception as e:
    print(f'   ❌ Failed: {e}')

  print('\n3️⃣  VC-V3 — Inline Tags:')
  try:
    t0 = time.time()
    vc3 = vc.generate(
      "<happy>I am so happy!</happy> <whisper>But keep it a secret.</whisper>",
      'en-US',
      reference_audio_bytes=ref_audio,
      gender='female', age=28, emotion='neutral', expression='none', version=3
    )
    print(f'   ✅ Generated in {time.time()-t0:.2f}s')
    play(vc3)
  except Exception as e:
    print(f'   ❌ Failed: {e}')

print('\n✅  Cell 6 complete!\n')


# ----


# ── Cell 7: Start FastAPI Server via ngrok ────────────────────────────────────
import sys, os, threading, time
import urllib.request

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# ── 1. Set your ngrok auth token ──────────────────────────────────────────────
# Free token at: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_AUTH_TOKEN = ''   # ← PASTE YOUR TOKEN HERE

if not NGROK_AUTH_TOKEN:
  raise ValueError(
    '❌  NGROK_AUTH_TOKEN is empty!\n'
    '    1. Go to https://dashboard.ngrok.com/get-started/your-authtoken\n'
    '    2. Copy your token and paste it above.\n'
  )

from pyngrok import ngrok, conf
conf.get_default().auth_token = NGROK_AUTH_TOKEN

# ── 2. Start uvicorn server in background thread ──────────────────────────────
PORT = 8000
import subprocess

def _run_server():
  subprocess.run(
    [sys.executable, '-m', 'uvicorn', 'main:app',
     '--host', '0.0.0.0', '--port', str(PORT), '--log-level', 'info'],
    cwd=BACKEND_DIR
  )

server_thread = threading.Thread(target=_run_server, daemon=True)
server_thread.start()
print('🚀  FastAPI server starting…')

# ── 3. Wait until server is ready ─────────────────────────────────────────────
for i in range(60):
  try:
    urllib.request.urlopen(f'http://localhost:{PORT}/api/health', timeout=2)
    print(f'✅  Server ready on port {PORT}')
    break
  except Exception:
    time.sleep(1)
    if i % 10 == 9:
      print(f'   Still waiting… ({i+1}s)')
    if i == 59:
      print('⚠️  Server taking longer than expected. Proceeding anyway…')

# ── 4. Open ngrok tunnel ──────────────────────────────────────────────────────
tunnel = ngrok.connect(PORT, 'http')
public_url = tunnel.public_url

print(f'\n🌐  ngrok tunnel active!')
print(f'    Public URL : {public_url}')
print(f'\n📋  Set this in your frontend/.env.local:')
print(f'    VITE_API_BASE={public_url}')
print(f'\n💡  Swagger docs : {public_url}/docs')
print(f'💡  Health check : {public_url}/api/health')
print('\n✅  Cell 7 complete. Server running!\n')
print('⚠️  Do NOT stop this cell — it keeps the server alive.')