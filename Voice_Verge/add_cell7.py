import json

notebook_path = r'c:\TTS\Voice_Verge\OmniVoice_Studio.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cell7_code = """# ── Cell 7: Launch Backend (FastAPI + Cloudflare Tunnel) ────────────────────
import sys, os, time, subprocess, threading, urllib.request

BACKEND_DIR = '/content/TTS/Voice_Verge/backend'
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

print("🚀 Starting FastAPI server on port 8000...")

# Start FastAPI server in the background
server_process = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd=BACKEND_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

def print_logs():
    for line in server_process.stdout:
        # Filter out noisy uvicorn logs, keep only important backend logs
        if "OmniVoice" in line or "Health" in line or "ERROR" in line:
            print(f"  {line.strip()}")

threading.Thread(target=print_logs, daemon=True).start()

# Give the server a few seconds to boot up
time.sleep(5)

print("\\n🌐 Downloading Cloudflare Tunnel...")
subprocess.run(['wget', '-q', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64', '-O', '/content/cloudflared'])
os.chmod('/content/cloudflared', 0o755)

print("🌐 Creating Cloudflare tunnel (this takes about 5 seconds)...")
tunnel_process = subprocess.Popen(
    ['/content/cloudflared', 'tunnel', '--url', 'http://127.0.0.1:8000'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

public_url = None
for line in tunnel_process.stdout:
    if "https://" in line and "trycloudflare.com" in line:
        # Extract the URL from the cloudflared log
        parts = line.split("https://")
        for part in parts:
            if "trycloudflare.com" in part:
                public_url = "https://" + part.split("trycloudflare.com")[0] + "trycloudflare.com"
                break
    if public_url:
        break

if not public_url:
    print("❌ Failed to create tunnel. Please restart the cell.")
else:
    print("\\n═════════════════════════════════════════════════════════════════════════════════")
    print("  🎉 OMNIVOICE STUDIO BACKEND IS LIVE!")
    print("═════════════════════════════════════════════════════════════════════════════════")
    print(f"  PUBLIC URL  : {public_url}")
    print("═════════════════════════════════════════════════════════════════════════════════\\n")

    print("📋 Copy this into frontend/.env.local :\\n")
    print(f"  VITE_API_BASE={public_url}\\n")
    print("\\n⏳ Server running. Keep this cell active.")
    print(" Runtime → Interrupt execution to stop.")

try:
    tunnel_process.wait()
except KeyboardInterrupt:
    print("\\n\\n⏹️ Stopping server...")
    server_process.terminate()
    tunnel_process.terminate()
"""

# Check if Cell 7 already exists by looking for "FastAPI" or "Cloudflare Tunnel" in the last few cells
already_exists = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'Cloudflare Tunnel' in "".join(cell.get('source', [])):
        already_exists = True
        break

if not already_exists:
    # Append the markdown header
    nb['cells'].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "## 🚀 Cell 7 — Launch Backend (FastAPI + Cloudflare Tunnel)\n",
            "\n",
            "Start the FastAPI server and create a public HTTPS tunnel.\n",
            "\n",
            "> After the tunnel URL appears, paste it into `frontend/.env.local`:\n",
            "> ```\n",
            "> VITE_API_BASE=https://xxxx.trycloudflare.com\n",
            "> ```\n",
            "> Then run `npm install && npm run dev` in the `frontend/` folder.\n",
            ">\n",
            "> **Keep this cell running** — interrupting it stops the backend.\n"
        ]
    })
    
    # Append the code cell
    # Split the code content correctly for Jupyter (keep newlines)
    source_lines = [line + '\n' for line in cell7_code.split('\n')]
    if source_lines:
        source_lines[-1] = source_lines[-1].rstrip('\n')
        
    nb['cells'].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines
    })

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated with Cell 7.")
