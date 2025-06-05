#!/usr/bin/env python3
"""
Script to replace all instances of '/brave/' with '/luxxle/' in the project files.
This helps fix hardcoded paths after renaming the brave directory to luxxle.
"""

import os
import re
import sys
from pathlib import Path

def should_skip_file(file_path):
    """Check if we should skip processing this file."""
    # Skip this script itself
    if file_path.name == 'replace_brave_with_luxxle.py':
        return True
    
    # Skip binary files and common non-text files
    skip_extensions = {
        '.exe', '.dll', '.so', '.dylib', '.a', '.lib', '.obj', '.o',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
        '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.mp3', '.mp4', '.avi', '.mov', '.wav', '.ogg',
        '.woff', '.woff2', '.ttf', '.otf', '.eot',
        '.pak', '.dat', '.bin', '.db', '.sqlite', '.cache'
    }
    
    if file_path.suffix.lower() in skip_extensions:
        return True
    
    # Skip hidden files and directories
    if file_path.name.startswith('.') and file_path.name not in ['.env', '.gitignore', '.gitattributes']:
        return True
    
    # Skip node_modules and other large directories
    skip_dirs = {'node_modules', '.git', 'out', 'build', '__pycache__', '.vs', '.vscode'}
    for part in file_path.parts:
        if part in skip_dirs:
            return True
    
    return False

def is_text_file(file_path):
    """Check if a file is likely a text file."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:  # Binary files often contain null bytes
                return False
        return True
    except:
        return False

def replace_brave_with_luxxle(file_path, dry_run=False):
    """Replace /brave/ with /luxxle/ in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Count replacements
        original_content = content
        
        # Replace various patterns
        patterns = [
            (r'/brave/', '/luxxle/'),
            (r'\\brave\\', r'\\luxxle\\'),  # Raw string for Windows paths
            (r'"brave"', '"luxxle"'),
            (r"'brave'", "'luxxle'"),
            (r'src/brave', 'src/luxxle'),
            (r'src\\brave', r'src\\luxxle'),  # Raw string for Windows paths
        ]
        
        total_replacements = 0
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            replacements = len(re.findall(pattern, content))
            total_replacements += replacements
            content = new_content
        
        if total_replacements > 0:
            print(f"{'[DRY RUN] ' if dry_run else ''}Found {total_replacements} replacements in: {file_path}")
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
        
        return total_replacements
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Main function."""
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print("Run without --dry-run to actually make changes")
        print("-" * 50)
    
    project_root = Path('.')
    total_files_processed = 0
    total_replacements = 0
    
    print(f"Scanning project in: {project_root.absolute()}")
    
    for file_path in project_root.rglob('*'):
        if file_path.is_file() and not should_skip_file(file_path):
            if is_text_file(file_path):
                total_files_processed += 1
                replacements = replace_brave_with_luxxle(file_path, dry_run)
                total_replacements += replacements
    
    print("-" * 50)
    print(f"Processed {total_files_processed} files")
    print(f"Made {total_replacements} total replacements")
    
    if dry_run:
        print("\nTo actually make the changes, run:")
        print("python replace_brave_with_luxxle.py")

if __name__ == '__main__':
    main() 