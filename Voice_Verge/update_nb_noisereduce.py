import json

notebook_path = r'c:\TTS\Voice_Verge\OmniVoice_Studio.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') != 'code':
        continue
        
    source = cell.get('source', [])
    new_source = []
    
    for line in source:
        if "'deepfilternet'," in line:
            new_source.append("  'noisereduce',\n")
        else:
            new_source.append(line)
        
    cell['source'] = new_source

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook fixed.")
