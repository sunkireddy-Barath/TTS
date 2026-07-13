import os
import re

EMOJIS = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]

def remove_emojis_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for emoji in EMOJIS:
        # Strip out the emojis, leaving any neighboring spaces alone
        # so we don't mess up python indentation
        content = content.replace(emoji, '')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Removed emojis from {filepath}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                remove_emojis_from_file(filepath)

if __name__ == "__main__":
    process_directory(r"c:\TTS\Voice_Verge")
