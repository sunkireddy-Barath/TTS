import json

with open('c:/TTS/Voice_Verge/OmniVoice_Studio.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

with open('notebook_code.py', 'w', encoding='utf-8') as f:
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            f.write(''.join(cell['source']) + '\n\n# --------\n')
