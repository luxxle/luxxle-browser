#!/usr/bin/env python3
"""
Comprehensive script to replace ALL instances of '//brave/' with '//luxxle/' 
in both src/brave/ and src/luxxle/ directories.

This ensures that even files in the brave directory point to the luxxle directory,
preventing build errors when brave components try to reference other brave components.
"""

import os
import re
from pathlib import Path
import time

def should_skip_directory(dir_path):
    """Check if we should skip processing this entire directory."""
    skip_dirs = {
        'node_modules', '.git', 'out', 'build', '__pycache__', '.vs', '.vscode',
        'vendor', 'third_party', '.github', 'docs'
    }
    
    return dir_path.name in skip_dirs

def should_skip_file(file_path):
    """Check if we should skip processing this file."""
    # Skip this script itself
    if 'fix_' in file_path.name and 'brave' in file_path.name:
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
    
    # Skip hidden files (except some important ones)
    if file_path.name.startswith('.') and file_path.name not in ['.env', '.gitignore', '.gitattributes']:
        return True
    
    return False

def is_text_file(file_path):
    """Check if a file is likely a text file."""
    try:
        # For known text file extensions, don't bother checking content
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.html', '.htm', '.css', '.scss',
            '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.sh', '.bat', '.cmd', '.ps1', '.cpp', '.c', '.h', '.hpp', '.cc',
            '.cxx', '.java', '.go', '.rs', '.rb', '.php', '.pl', '.sql',
            '.gn', '.gni', '.BUILD', '.bazel', '.bzl', '.idl', '.mojom'
        }
        
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # For files without extension or unknown extensions, check content
        if file_path.suffix == '' or file_path.suffix.lower() not in text_extensions:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:  # Binary files often contain null bytes
                    return False
        return True
    except:
        return False

def replace_brave_with_luxxle(file_path, dry_run=False):
    """Replace //brave/ with //luxxle/ in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Simple string replacement for //brave/ -> //luxxle/
        # This is more reliable than regex for this specific case
        content = content.replace('//brave/', '//luxxle/')
        
        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
            
            changes = len(original_content.split('//brave/')) - 1
            print(f"{'[DRY RUN] ' if dry_run else ''}Fixed {changes} references in: {file_path}")
            return changes
        
        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def scan_directory(directory, dry_run=False):
    """Scan a directory for files to process."""
    total_files_processed = 0
    total_replacements = 0
    
    try:
        for root, dirs, files in os.walk(directory):
            root_path = Path(root)
            
            # Skip entire directories
            dirs[:] = [d for d in dirs if not should_skip_directory(root_path / d)]
            
            # Process files in current directory
            for file_name in files:
                file_path = root_path / file_name
                
                if not should_skip_file(file_path) and is_text_file(file_path):
                    total_files_processed += 1
                    if total_files_processed % 100 == 0:
                        print(f"Processed {total_files_processed} files so far...")
                    
                    replacements = replace_brave_with_luxxle(file_path, dry_run)
                    total_replacements += replacements
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return total_files_processed, total_replacements
    
    return total_files_processed, total_replacements

def main():
    """Main function."""
    import sys
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print("Run without --dry-run to actually make changes")
        print("-" * 60)
    
    # Target both brave and luxxle directories
    target_dirs = []
    
    if os.path.exists('src/brave'):
        target_dirs.append('src/brave')
        print(f"✓ Found src/brave directory")
    else:
        print("⚠ No src/brave directory found")
    
    if os.path.exists('src/luxxle'):
        target_dirs.append('src/luxxle')
        print(f"✓ Found src/luxxle directory")
    else:
        print("⚠ No src/luxxle directory found")
    
    if not target_dirs:
        print("❌ No target directories found! Make sure you're in the project root.")
        return
    
    print(f"\n🔍 Will process {len(target_dirs)} directories:")
    for dir_path in target_dirs:
        print(f"   - {os.path.abspath(dir_path)}")
    
    if not dry_run:
        response = input("\n⚠️  This will modify files. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    print(f"\n🚀 Starting {'dry run' if dry_run else 'replacement'}...")
    print("-" * 60)
    
    total_files_processed = 0
    total_replacements = 0
    
    start_time = time.time()
    
    for target_dir in target_dirs:
        print(f"\n📂 Processing directory: {target_dir}")
        files_processed, replacements = scan_directory(target_dir, dry_run)
        total_files_processed += files_processed
        total_replacements += replacements
        print(f"   ✓ {files_processed} files processed, {replacements} replacements made")
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"✅ SUMMARY:")
    print(f"   📁 Directories processed: {len(target_dirs)}")
    print(f"   📄 Files processed: {total_files_processed}")
    print(f"   🔄 Total replacements: {total_replacements}")
    print(f"   ⏱️  Time taken: {elapsed_time:.2f} seconds")
    
    if dry_run and total_replacements > 0:
        print(f"\n🎯 To actually make these {total_replacements} changes, run:")
        print("   python fix_all_brave_references.py")
    elif not dry_run and total_replacements > 0:
        print(f"\n🎉 Successfully updated {total_replacements} //brave/ references to //luxxle/!")
        print("   Now try running your build again.")
    elif total_replacements == 0:
        print("\n✨ No //brave/ references found. All clean!")

if __name__ == '__main__':
    main() 