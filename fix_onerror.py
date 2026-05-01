import os
import re

path = 'templates'
for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith('.html'):
            file_path = os.path.join(root, f)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace onerror="this.src=..." with onerror="this.onerror=null; this.src=..."
            new_content = re.sub(
                r'onerror\s*=\s*(["\'])this\.src=([^\1]+?)\1',
                r'onerror=\1this.onerror=null; this.src=\2\1',
                content
            )
            
            if new_content != content:
                print(f"Updated {file_path}")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
