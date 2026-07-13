import json
import re

notebook_path = r'c:\TTS\Voice_Verge\OmniVoice_Studio.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') != 'code':
        continue
        
    source = cell.get('source', [])
    new_source = []
    
    # We will process line by line or modify the whole string
    text = "".join(source)
    
    # 1. Replace Google Drive Mount with Git Clone
    if 'from google.colab import drive' in text:
        text = re.sub(
            r'from google\.colab import drive\n\n# ── 1\. Mount Google Drive ──────────────────────────────────────────────────────\ndrive\.mount\(\'/content/drive\'\)\n\n# ── 2\. Locate Voice_Verge project folder ───────────────────────────────────────\nDRIVE_PROJECT_PATH = \'/content/drive/MyDrive/Voice_Verge\'',
            '# ── 1. Clone GitHub Repository ────────────────────────────────────────────────\nif not os.path.exists(\'/content/TTS\'):\n    print(" Cloning repository...")\n    subprocess.run([\'git\', \'clone\', \'https://github.com/sunkireddy-Barath/TTS.git\', \'/content/TTS\'])\nelse:\n    print(" Repository already cloned.")\n\n# ── 2. Locate Voice_Verge project folder ───────────────────────────────────────\nDRIVE_PROJECT_PATH = \'/content/TTS/Voice_Verge\'',
            text
        )

    # 2. Replace dependencies (clearvoice -> deepfilternet)
    if "'clearvoice'," in text:
        text = text.replace("'clearvoice',", "'deepfilternet',")
        
    # 3. Replace all other occurrences of the hardcoded paths
    text = text.replace('/content/drive/MyDrive/Voice_Verge', '/content/TTS/Voice_Verge')
    
    # Ensure source is a list of lines as Jupyter expects
    lines = text.split('\n')
    cell['source'] = [line + '\n' for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])
    
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
