import shutil, base64

shutil.make_archive('backend', 'zip', 'c:/TTS/Voice_Verge/backend')
b64 = base64.b64encode(open('backend.zip', 'rb').read()).decode('utf-8')

code = f"""import base64, zipfile, os

b64_data = '{b64}'
os.makedirs('/content/TTS/Voice_Verge/backend', exist_ok=True)
with open('backend.zip', 'wb') as f:
    f.write(base64.b64decode(b64_data))
with zipfile.ZipFile('backend.zip', 'r') as z:
    z.extractall('/content/TTS/Voice_Verge/backend')
print('✅ Backend files patched successfully!')
"""

with open('colab_patch.py', 'w', encoding='utf-8') as f:
    f.write(code)
