#!/usr/bin/env python3
"""
Script to comment out lines containing '/components/' in BUILD.gn files.
This helps remove Brave component dependencies to use Chromium defaults instead.

Usage:
    python comment_components.py <BUILD.gn file path>
    python comment_components.py --all  # Process all BUILD.gn files in current directory tree
"""

import os
import sys
import argparse
import re
from pathlib import Path

def comment_components_in_file(file_path):
    """
    Comment out lines containing '/components/' in a BUILD.gn file.
    
    Args:
        file_path (str): Path to the BUILD.gn file
        
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    modified = False
    new_lines = []
    
    for line in lines:
        # Check if line contains '/components/' and is not already commented
        if '/components/' in line and not line.strip().startswith('#'):
            # Find the indentation
            indent = len(line) - len(line.lstrip())
            indented_comment = ' ' * indent + '# Commented out: removed components dependency - using Chromium defaults instead\n'
            commented_line = ' ' * indent + '# ' + line.lstrip()
            
            new_lines.append(indented_comment)
            new_lines.append(commented_line)
            modified = True
            print(f"  Commented: {line.strip()}")
        else:
            new_lines.append(line)
    
    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✓ Modified {file_path}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    else:
        print(f"- No changes needed for {file_path}")
        return False

def find_build_gn_files(directory):
    """Find all BUILD.gn files in directory tree."""
    build_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'BUILD.gn' or file.endswith('.gni'):
                build_files.append(os.path.join(root, file))
    return build_files

def main():
    parser = argparse.ArgumentParser(description='Comment out /components/ references in BUILD.gn files')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('file', nargs='?', help='Path to specific BUILD.gn file')
    group.add_argument('--all', action='store_true', help='Process all BUILD.gn files in current directory tree')
    group.add_argument('--brave-dir', action='store_true', help='Process all BUILD.gn files in src/brave directory')
    
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--backup', action='store_true', help='Create .bak backup files before modifying')
    
    args = parser.parse_args()
    
    files_to_process = []
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} does not exist")
            sys.exit(1)
        files_to_process = [args.file]
    elif args.all:
        files_to_process = find_build_gn_files('.')
    elif args.brave_dir:
        brave_dir = 'src/brave' if os.path.exists('src/brave') else '.'
        files_to_process = find_build_gn_files(brave_dir)
    
    if not files_to_process:
        print("No BUILD.gn files found")
        sys.exit(1)
    
    print(f"Found {len(files_to_process)} BUILD.gn/GNI files to process:")
    for f in files_to_process:
        print(f"  {f}")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
    
    modified_count = 0
    
    for file_path in files_to_process:
        print(f"Processing {file_path}...")
        
        if args.backup and not args.dry_run:
            try:
                backup_path = file_path + '.bak'
                with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                print(f"  Created backup: {backup_path}")
            except Exception as e:
                print(f"  Warning: Could not create backup: {e}")
        
        if not args.dry_run:
            if comment_components_in_file(file_path):
                modified_count += 1
        else:
            # For dry run, just show what would be changed
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                changes_found = False
                for i, line in enumerate(lines, 1):
                    if '/components/' in line and not line.strip().startswith('#'):
                        print(f"  Line {i}: {line.strip()}")
                        changes_found = True
                
                if changes_found:
                    modified_count += 1
                else:
                    print(f"  No changes needed")
                    
            except Exception as e:
                print(f"  Error reading file: {e}")
        
        print()
    
    if args.dry_run:
        print(f"DRY RUN COMPLETE: {modified_count} files would be modified")
    else:
        print(f"COMPLETE: Modified {modified_count} files")

if __name__ == '__main__':
    main() 