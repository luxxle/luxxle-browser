#!/usr/bin/env python3
import os
import re
import sys

def fix_brave_imports(root_dir):
    """
    Find and comment out all lines that import from //luxxle/ directories
    in BUILD.gn files throughout the codebase.
    """
    fixed_files = []
    processed_count = 0
    
    print("Collecting BUILD.gn files...")
    build_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip the components-backup directory and brave directory
        if 'components-backup' in root or '\\luxxle\\' in root or '/luxxle/' in root:
            continue
            
        for file in files:
            if file == 'BUILD.gn':
                build_files.append(os.path.join(root, file))
    
    print(f"Found {len(build_files)} BUILD.gn files to process...")
    
    for file_path in build_files:
        processed_count += 1
        if processed_count % 10 == 0:
            print(f"Processed {processed_count}/{len(build_files)} files...")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern to match import statements from //luxxle/ directories
            # This will match lines like:
            # import("//luxxle/...") <any_following_code>
            pattern = r'^(\s*)(import\("//luxxle/[^"]*"\)[^\n]*)'
            
            # Replace with commented version
            content = re.sub(pattern, r'\1# \2', content, flags=re.MULTILINE)
            
            # Check if any changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path)
                print(f"Fixed: {file_path}")
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return fixed_files

if __name__ == "__main__":
    # Start from src directory
    src_dir = "src"
    if not os.path.exists(src_dir):
        print("src directory not found. Make sure you're running this from the project root.")
        sys.exit(1)
    
    print("Scanning for brave import statements in BUILD.gn files...")
    fixed_files = fix_brave_imports(src_dir)
    
    if fixed_files:
        print(f"\nFixed {len(fixed_files)} files:")
        for file_path in fixed_files:
            print(f"  - {file_path}")
    else:
        print("\nNo brave import statements found to fix.")
    
    print("\nDone!") 