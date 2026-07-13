import os
import re

# Emojis commonly used in the codebase
EMOJIS = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

def remove_emojis_from_file(filepath):
  with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

  original = content
  for emoji in EMOJIS:
    content = content.replace(emoji + '  ', '')
    content = content.replace(emoji + ' ', '')
    content = content.replace(emoji, '')
    
  # Extra cleanup for weird spaces left by emojis
  content = content.replace(" ", " ")

  if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
    print(f"Removed emojis from {filepath}")

def process_directory(directory):
  for root, _, files in os.walk(directory):
    for file in files:
    if file.endswith('.py') or file.endswith('.ipynb') or file.endswith('.md'):
      filepath = os.path.join(root, file)
      remove_emojis_from_file(filepath)

if __name__ == "__main__":
  process_directory(r"c:\TTS\Voice_Verge")
