# Cell 1: Environment Setup
import sys, os, subprocess

# 1. Mount Google Drive
try:
  from google.colab import drive
  drive.mount('/content/drive')
except ImportError:
  print("Not running in Colab. Skipping Drive mount.")

DRIVE_ROOT = '/content/drive/MyDrive/TTS'

# 2. Clone GitHub Repository to Google Drive
if not os.path.exists(DRIVE_ROOT):
  print(f"Cloning repository into Google Drive ({DRIVE_ROOT})...")
  os.makedirs(os.path.dirname(DRIVE_ROOT), exist_ok=True)
  result = subprocess.run(
    ['git', 'clone', 'https://github.com/sunkireddy-Barath/TTS.git', DRIVE_ROOT],
    capture_output=True, text=True
  )
  if result.returncode != 0:
    print(f"Git clone failed:\n{result.stderr}")
    raise RuntimeError("Repository clone failed.")
  print("Repository cloned successfully.")
else:
  print("Repository found in Google Drive. Pulling latest updates...")
  subprocess.run(['git', '-C', DRIVE_ROOT, 'pull'], capture_output=True, text=True)

# 3. Locate Voice_Verge project folder
DRIVE_PROJECT_PATH = os.path.join(DRIVE_ROOT, 'Voice_Verge')

if not os.path.isdir(DRIVE_PROJECT_PATH):
  raise FileNotFoundError(
    f'\nVoice_Verge not found at: {DRIVE_PROJECT_PATH}\n'
    'Make sure the repo was cloned correctly.'
  )
print(f'Project found: {DRIVE_PROJECT_PATH}')

BACKEND_DIR    = os.path.join(DRIVE_PROJECT_PATH, 'backend')
CHECKPOINT_DIR = os.path.join(DRIVE_PROJECT_PATH, 'checkpoints')
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# 4. Add backend to Python path
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# 5. Environment variables
os.environ['HF_HOME']         = CHECKPOINT_DIR
os.environ['PORT']            = '8000'
os.environ['ALLOWED_ORIGINS'] = '*'

# 5. GPU check
import torch
if torch.cuda.is_available():
  gpu  = torch.cuda.get_device_name(0)
  vram = torch.cuda.get_device_properties(0).total_memory / 1e9
  print(f'GPU: {gpu}  ({vram:.1f} GB VRAM)')
else:
  print('No GPU detected!')
  print('Go to Runtime > Change runtime type > Hardware accelerator > T4 GPU')

print(f'\nBackend  : {BACKEND_DIR}')
print(f'HF Cache : {CHECKPOINT_DIR}')
print(f'Python {sys.version.split()[0]}  |  PyTorch {torch.__version__}')
print('\nCell 1 complete.\n')


# ----


# Cell 2: Install OmniVoice & Dependencies
import subprocess, sys

# Step 0: Pin numpy BEFORE everything else to prevent binary conflict
print('Pinning numpy==1.26.4 (prevents binary conflict after restart)...')
r = subprocess.run(
  [sys.executable, '-m', 'pip', 'install', '-q', '--force-reinstall', 'numpy==1.26.4'],
  capture_output=True, text=True
)
print('numpy pinned.' if r.returncode == 0 else f'numpy pin failed: {r.stderr[-300:]}')

# Step 1: OmniVoice TTS engine
OMNIVOICE_INSTALL = 'omnivoice'
print(f'\nInstalling OmniVoice ({OMNIVOICE_INSTALL})...')
r = subprocess.run(
  [sys.executable, '-m', 'pip', 'install', '-q', OMNIVOICE_INSTALL],
  capture_output=True, text=True
)
print('omnivoice installed.' if r.returncode == 0 else f'{r.stderr[-400:]}')

# Step 2: All backend dependencies
PACKAGES = [
  'transformers>=4.40.0',
  'accelerate>=0.29.0',
  'fastapi>=0.111.0',
  'uvicorn[standard]>=0.29.0',
  'python-multipart>=0.0.9',
  'soundfile>=0.12.1',
  'pydantic>=2.7.0',
  'librosa>=0.10.0',
  'torchaudio',
  'noisereduce>=3.0.0',
  'modelscope>=1.15.0',
  'numpy<2.0.0',
]

print('\nInstalling backend dependencies...')
failed = []
for pkg in PACKAGES:
  r = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-q', pkg],
    capture_output=True, text=True
  )
  status = 'OK' if r.returncode == 0 else 'FAIL'
  print(f'  {status}  {pkg}')
  if r.returncode != 0:
    failed.append((pkg, r.stderr[-200:]))

if failed:
  print(f'\nWARNING: {len(failed)} package(s) failed:')
  for pkg, err in failed:
    print(f'   FAIL {pkg}: {err}')
else:
  print('\nAll dependencies installed.')

print('\nIMPORTANT: Now go to Runtime > Restart session')
print('   Then run Cell 3 ONLY (skip Cells 1 & 2).\n')
print('Cell 2 complete.\n')


# ----


# Cell 3: Verify OmniVoice Import
import subprocess, sys, os
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

# Pre-flight: numpy binary compatibility check
def _check_and_fix_numpy():
  try:
    import numpy as np
    _ = np.zeros(1)
    print(f'numpy {np.__version__} OK')
    return True
  except ValueError as ve:
    if 'numpy.dtype size changed' in str(ve) or 'numpy' in str(ve).lower():
      print('\nnumpy binary conflict -- force-reinstalling numpy==1.26.4...')
      subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-q', '--force-reinstall', 'numpy==1.26.4'],
        check=True
      )
      print('numpy reinstalled. Restarting runtime...')
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
  raise SystemExit('Runtime restart triggered -- re-run Cell 3 after restart.')

# OmniVoice import test
try:
  from omnivoice import OmniVoice
  print(f'OmniVoice importable: {OmniVoice}')
except ValueError as ve:
  if 'numpy.dtype size changed' in str(ve) or 'numpy' in str(ve).lower():
    print('\nnumpy conflict STILL present.')
    print('Try: Runtime > Disconnect and delete runtime, then re-run all cells.')
  else:
    raise
except ImportError as e:
  print(f'OmniVoice import failed: {e}')
  print('Run Cell 2 first, then restart.')

# Backend module verification
required = [
  'omnivoice_engine.py', 'emotion_engine.py', 'expression_engine.py',
  'tag_parser.py', 'language_router.py', 'voice_design.py',
  'voice_clone.py', 'audio_verifier.py', 'noise_reduction.py', 'main.py',
]
print(f'\nBackend module check ({BACKEND_DIR}):')
missing = []
for f in required:
  path = os.path.join(BACKEND_DIR, f)
  if os.path.isfile(path):
    size = os.path.getsize(path)
    print(f'  OK  {f:<35} {size:>8,} bytes')
  else:
    print(f'  MISSING  {f}')
    missing.append(f)

if missing:
  print(f'\nWARNING: {len(missing)} backend file(s) missing: {missing}')
else:
  print('\nAll backend modules found.  Cell 3 complete.')


# ----


# Cell 4: Download OmniVoice Model
import os, subprocess, sys

os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'hf_transfer'], check=True)
print('hf_transfer enabled (faster parallel download)')

# Attempt to load HF_TOKEN from Colab Secrets to prevent rate limiting
try:
  from google.colab import userdata
  hf_token = userdata.get('HF_TOKEN')
  if hf_token:
    os.environ['HF_TOKEN'] = hf_token
    print('✅ HF_TOKEN applied from Colab Secrets (Bypassing rate limits)')
except Exception:
  print('⚠️ No HF_TOKEN found in Colab Secrets. You may experience slow downloads.')

from huggingface_hub import snapshot_download

MODEL_ID       = 'k2-fsa/OmniVoice'
CHECKPOINT_DIR = '/content/TTS/Voice_Verge/checkpoints'
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.environ['HF_HOME'] = CHECKPOINT_DIR

model_marker = os.path.join(CHECKPOINT_DIR, 'hub', 'models--k2-fsa--OmniVoice')
if os.path.isdir(model_marker):
  print(f'\nOmniVoice already cached at: {model_marker}')
  print('Skipping download (delete the folder to force re-download).')
else:
  print(f'\nDownloading {MODEL_ID} -> {CHECKPOINT_DIR}')
  print('hf_transfer active -- 3-5x faster. May still take 5-15 minutes...\n')
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
    print(f'Total size: {total_gb:.2f} GB')
  except Exception as e:
    print(f'\nhf_transfer failed or rate-limited: {e}')
    print('Falling back to standard HuggingFace downloader (more stable)...')
    os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'
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
      print(f'Total size: {total_gb:.2f} GB')
    except Exception as e2:
      print(f'\nDownload completely failed: {e2}')
      raise

print('\nCell 4 complete.')


# ----


# Cell 5: Load OmniVoice Model
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

print(f'Loading OmniVoice on {device} ({dtype})...')
print('First load: 1-3 min | Subsequent: ~30s')
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
  print(f'Device  : {engine.device}')
  print(f'Loaded  : {engine.loaded}')

  if torch.cuda.is_available():
    used  = torch.cuda.memory_allocated() / 1e9
    total = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f'VRAM    : {used:.2f} GB used / {total:.1f} GB total')

  print('\nCell 5 complete.')

except KeyboardInterrupt:
  print('\n\nModel loading interrupted! Run Cell 5 again.')
except Exception as e:
  import traceback
  print(f'\nFailed to load model: {e}')
  traceback.print_exc()
  raise


# ----


# Cell 6: Test Audio Pipeline
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
  raise RuntimeError('Engine not loaded! Run Cell 5 first.')

vd = VoiceDesignService(engine)
vc = VoiceCloneService(engine)

def play(wav_bytes):
  arr, sr = sf.read(io.BytesIO(wav_bytes))
  dur = len(arr) / sr
  note = '  [WARNING: very short]' if dur < 0.5 else ''
  print(f'   Duration: {dur:.2f}s{note}')
  display(Audio(arr, rate=sr))

def run(label, fn):
  print(f'\n{label}')
  try:
    t0 = time.time()
    result = fn()
    print(f'   Generated in {time.time()-t0:.2f}s')
    play(result)
    return result
  except Exception as e:
    import traceback
    print(f'   FAILED: {e}')
    traceback.print_exc()
    return None

# =============================================================================
# VOICE DESIGN TESTS
# =============================================================================
print('\n' + '='*60)
print('VOICE DESIGN TESTS')
print('='*60)

# V1: Emotion only
print('\n-- V1: Emotion Only ------------------------------------------')

w_v1 = run('V1 | Female, Happy, en-US:', lambda: vd.generate(
  "Hello! This is a version one test with a female voice.",
  'en-US', 'female', 25, 'happy', 'none', version=1
))

# V2: Emotion + Expression dropdown
print('\n-- V2: Emotion + Expression Dropdown -------------------------')

w_v2_giggle = run('V2 | Female, Neutral + GIGGLE, en-GB:', lambda: vd.generate(
  "I just won the match today.",
  'en-GB', 'female', 28, 'neutral', 'giggle', version=2
))

w_v2_sigh = run('V2 | Female, Neutral + SIGH, en-US:', lambda: vd.generate(
  "That was a long day at work.",
  'en-US', 'female', 30, 'neutral', 'sigh', version=2
))

w_v2_sigh_male = run('V2 | Male, Neutral + SIGH, en-US:', lambda: vd.generate(
  "That was a long day at work.",
  'en-US', 'male', 32, 'neutral', 'sigh', version=2
))

w_v2_surprise = run('V2 | Female, Neutral + SURPRISE, en-US:', lambda: vd.generate(
  "I cannot believe what just happened.",
  'en-US', 'female', 28, 'neutral', 'surprise', version=2
))

w_v2_surprise_male = run('V2 | Male, Neutral + SURPRISE, en-US:', lambda: vd.generate(
  "I cannot believe what just happened.",
  'en-US', 'male', 32, 'neutral', 'surprise', version=2
))

w_v2_dissatisfaction = run('V2 | Male, Neutral + DISSATISFACTION, en-US:', lambda: vd.generate(
  "This is not what I expected at all.",
  'en-US', 'male', 35, 'neutral', 'dissatisfaction', version=2
))

w_v2_question = run('V2 | Female, Neutral + QUESTION, en-US:', lambda: vd.generate(
  "You are going to the party tonight.",
  'en-US', 'female', 25, 'neutral', 'question', version=2
))

w_v2_laughter = run('V2 | Female, Happy + LAUGHTER, en-US:', lambda: vd.generate(
  "That joke was absolutely hilarious.",
  'en-US', 'female', 28, 'happy', 'laughter', version=2
))

# V2: Multi-language expressions
print('\n-- V2: Multi-Language Expression Tests -----------------------')

run('V2 | Hindi + SIGH, female:', lambda: vd.generate(
  "\u0906\u091c \u0915\u093e \u0926\u093f\u0928 \u092c\u0939\u0941\u0924 \u0925\u0915\u093e\u0928\u0947 \u0935\u093e\u0932\u093e \u0925\u093e\u0964",
  'hi', 'female', 30, 'neutral', 'sigh', version=2
))

run('V2 | Spanish + GIGGLE, female:', lambda: vd.generate(
  "Eso fue muy gracioso y divertido.",
  'es', 'female', 25, 'neutral', 'giggle', version=2
))

run('V2 | Japanese + SURPRISE, female:', lambda: vd.generate(
  "\u305d\u308c\u306f\u4fe1\u3058\u3089\u308c\u306a\u3044\u3053\u3068\u3067\u3059\u3002",
  'ja', 'female', 28, 'neutral', 'surprise', version=2
))

# V3: Inline emotion tags
print('\n-- V3: Inline Emotion Tags -----------------------------------')

w_v3_emotion = run('V3 | Male, Multi-Emotion Inline Tags, en-US:', lambda: vd.generate(
  "<angry>Get out of here!</angry> <calm>Just kidding, you can stay.</calm>",
  'en-US', 'male', 30, 'neutral', 'none', version=3
))

run('V3 | Female, Happy then Whisper, en-US:', lambda: vd.generate(
  "<happy>I won the lottery today!</happy> <whisper>But please do not tell anyone.</whisper>",
  'en-US', 'female', 28, 'neutral', 'none', version=3
))

# V3: Inline expression tags
print('\n-- V3: Inline Expression Tags --------------------------------')

run('V3 | Female + inline sigh tag, en-US:', lambda: vd.generate(
  "After all that work. <sigh> I need some rest now.",
  'en-US', 'female', 30, 'neutral', 'none', version=3
))

run('V3 | Male + inline sigh tag, en-US:', lambda: vd.generate(
  "After all that work. <sigh> I need some rest now.",
  'en-US', 'male', 32, 'neutral', 'none', version=3
))

run('V3 | Female + inline laugh tag, en-US:', lambda: vd.generate(
  "He told the funniest joke. <laugh> I could not stop.",
  'en-US', 'female', 28, 'neutral', 'none', version=3
))

run('V3 | Female + inline surprise tag, en-US:', lambda: vd.generate(
  "Wait, you got promoted already? <surprise> That is incredible news.",
  'en-US', 'female', 25, 'neutral', 'none', version=3
))

# =============================================================================
# VOICE CLONING TESTS  (reference = w_v2_giggle or w_v1 fallback)
# =============================================================================
print('\n' + '='*60)
print('VOICE CLONING TESTS')
print('='*60)

ref_audio = w_v2_giggle or w_v1
if ref_audio is None:
  print('No reference audio available -- skipping clone tests.')
else:
  # VC-V1: Emotion speed only
  print('\n-- VC-V1: Emotion Only --------------------------------------')

  run('VC-V1 | Sad, en-US:', lambda: vc.generate(
    "Hello, I am testing voice cloning now.",
    'en-US', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='sad', expression='none', version=1
  ))

  # VC-V2: Emotion + Expression dropdown
  print('\n-- VC-V2: Emotion + Expression Dropdown ----------------------')

  run('VC-V2 | Neutral + SIGH, en-US:', lambda: vc.generate(
    "I can sigh like this.",
    'en-US', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='neutral', expression='sigh', version=2
  ))

  run('VC-V2 | Neutral + GIGGLE, en-US:', lambda: vc.generate(
    "That story you told was really funny.",
    'en-US', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='neutral', expression='giggle', version=2
  ))

  run('VC-V2 | Neutral + SURPRISE, en-US:', lambda: vc.generate(
    "I had no idea this was going to happen.",
    'en-US', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='neutral', expression='surprise', version=2
  ))

  run('VC-V2 | Hindi + SIGH:', lambda: vc.generate(
    "\u092c\u0939\u0941\u0924 \u0925\u0915\u093e\u0928 \u0939\u094b \u0917\u0908 \u0906\u091c\u0964",
    'hi', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='neutral', expression='sigh', version=2
  ))

  # VC-V3: Inline tags
  print('\n-- VC-V3: Inline Tags ----------------------------------------')

  run('VC-V3 | Happy + Whisper inline, en-US:', lambda: vc.generate(
    "<happy>I am so happy!</happy> <whisper>But keep it a secret.</whisper>",
    'en-US', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='neutral', expression='none', version=3
  ))

  run('VC-V3 | Inline sigh tag, en-US:', lambda: vc.generate(
    "After all that effort. <sigh> Let us move on.",
    'en-US', reference_audio_bytes=ref_audio,
    gender='female', age=28, emotion='neutral', expression='none', version=3
  ))

print('\nCell 6 complete.\n')


# ----


# Cell 7: Launch Backend (FastAPI + Cloudflare Tunnel)
import sys, os, time, subprocess, threading, re, urllib.request

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
  sys.path.insert(0, BACKEND_DIR)

PORT = 8000

# 1. Install cloudflared (free, no token required)
print('Installing cloudflared...')
subprocess.run(['pip', 'install', '-q', 'cloudflared'], check=True)
print('cloudflared ready.')

# 2. Start uvicorn server in background process
print(f'\nStarting FastAPI server on port {PORT}...')
server_proc = subprocess.Popen(
  [sys.executable, '-m', 'uvicorn', 'main:app',
   '--host', '0.0.0.0', '--port', str(PORT), '--log-level', 'warning'],
  cwd=BACKEND_DIR
)

# 3. Wait until server is ready
for i in range(60):
  try:
    urllib.request.urlopen(f'http://localhost:{PORT}/api/health', timeout=2)
    print(f'Server ready on port {PORT}')
    break
  except Exception:
    time.sleep(1)
    if i % 10 == 9:
      print(f'   Still waiting... ({i+1}s)')
    if i == 59:
      print('Server taking longer than expected. Proceeding anyway...')

# 4. Open Cloudflare tunnel (free, no account needed)
tunnel_url = None

def _run_tunnel():
  global tunnel_url
  proc = subprocess.Popen(
    ['cloudflared', 'tunnel', '--url', f'http://localhost:{PORT}'],
    stderr=subprocess.PIPE, text=True
  )
  for line in proc.stderr:
    m = re.search(r'https://[\w-]+\.trycloudflare\.com', line)
    if m:
      tunnel_url = m.group(0)
      print(f'\nCloudflare tunnel active!')
      print(f'Public URL : {tunnel_url}')
      print(f'\nSet this in your frontend/.env.local:')
      print(f'VITE_API_BASE={tunnel_url}')
      print(f'\nSwagger docs : {tunnel_url}/docs')
      print(f'Health check : {tunnel_url}/api/health')
      print('\nCell 7 complete. Server running!')
      print('Do NOT stop this cell -- it keeps the server alive.')
      break

tunnel_thread = threading.Thread(target=_run_tunnel, daemon=True)
tunnel_thread.start()
time.sleep(8)
if not tunnel_url:
  print('Tunnel URL not yet detected -- check output above in a moment.')