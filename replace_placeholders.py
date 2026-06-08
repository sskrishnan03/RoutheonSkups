import os
import re

path = 'templates'
for root, dirs, files in os.walk(path):
    for f in files:
        if f.endswith('.html'):
            file_path = os.path.join(root, f)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = re.sub(
                r'https://via\.placeholder\.com[^\"\']*',
                'https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?auto=format&fit=crop&w=600&q=80',
                content
            )
            
            if new_content != content:
                print(f"Updated {file_path}")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
