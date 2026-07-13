# ── Cell 2: Install OmniVoice & Dependencies ───────────────────────────────────
import subprocess, sys
# ── OmniVoice — the TTS engine ────────────────────────────────────────────────
# From PyPI (stable) — recommended
OMNIVOICE_INSTALL = 'omnivoice'
# From GitHub latest (uncomment to use):
# OMNIVOICE_INSTALL = 'git+https://github.com/k2-fsa/OmniVoice.git'
print(f'⬇️ Installing OmniVoice ({OMNIVOICE_INSTALL})…')
r = subprocess.run(
  [sys.executable, '-m', 'pip', 'install', '-q', OMNIVOICE_INSTALL],
  capture_output=True, text=True
)
print('✅  omnivoice installed.' if r.returncode == 0 else f'❌  {r.stderr[-400:]}')
# ── Rust/Cargo dependency for MossFormer2_SE_48K ────────────────────────────
print('⬇️ Installing Rust (required for MossFormer2_SE_48K)...')
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
  'noisereduce',
]
print('\n📦  Installing backend dependencies…')
failed = []
for pkg in PACKAGES:
  r = subprocess.run(
    [sys.executable, '-m', 'pip', 'install', '-q', pkg],
    capture_output=True, text=True
  )
  status = '✅' if r.returncode == 0 else '❌'
  print(f' {status}  {pkg}')
  if r.returncode != 0:
    failed.append(pkg)
if failed:
  print(f'\n⚠️  {len(failed)} failed: {failed}')
else:
  print('\n✅  All dependencies installed.')
