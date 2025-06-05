#!/usr/bin/env python3
"""
Simple script to replace //brave/ with //luxxle/ in all text files in the luxxle directory.
"""

import os
import re
from pathlib import Path

def replace_in_file(file_path):
    """Replace //brave/ with //luxxle/ in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Simple string replacement for //brave/ -> //luxxle/
        content = content.replace('//brave/', '//luxxle/')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
            
            changes = len(original_content.split('//brave/')) - 1
            print(f"Fixed {changes} references in: {file_path}")
            return changes
        
        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def is_text_file(file_path):
    """Check if file is a text file we should process."""
    text_extensions = {
        '.gn', '.gni', '.py', '.js', '.ts', '.cc', '.cpp', '.h', '.hpp', 
        '.txt', '.md', '.json', '.yaml', '.yml', '.toml'
    }
    
    return file_path.suffix.lower() in text_extensions

def main():
    """Main function."""
    total_replacements = 0
    
    luxxle_dir = Path('src/luxxle')
    if not luxxle_dir.exists():
        print("Error: src/luxxle directory not found!")
        return
    
    print("Fixing //brave/ references in luxxle directory...")
    
    for root, dirs, files in os.walk(luxxle_dir):
        # Skip some directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'out', 'build']]
        
        for file_name in files:
            file_path = Path(root) / file_name
            
            if is_text_file(file_path):
                replacements = replace_in_file(file_path)
                total_replacements += replacements
    
    print(f"\nDone! Made {total_replacements} total replacements.")

if __name__ == '__main__':
    main() 