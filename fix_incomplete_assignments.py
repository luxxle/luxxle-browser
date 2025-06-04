#!/usr/bin/env python3
"""
Script to fix incomplete assignments in GNI files.
Finds lines that end with = and have their values commented out, then provides empty arrays.
"""

import os
import re
import sys
from pathlib import Path

def fix_incomplete_assignments_in_file(file_path):
    """Fix incomplete assignments in a GNI file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False
    
    modified = False
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for incomplete assignment pattern: variable_name =
        if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*$', line):
            # Check if next lines are comments that contain the original value
            next_lines_comments = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('#'):
                next_lines_comments.append(lines[j])
                j += 1
            
            # Extract variable name and indentation
            match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*$', line)
            if match:
                indent = match.group(1)
                var_name = match.group(2)
                
                # Create fixed assignment with empty array
                new_lines.append(f"{indent}# Initialize as empty array since Brave components have been removed\n")
                new_lines.append(f"{indent}{var_name} = [\n")
                
                # Add the commented out original values inside the array
                for comment_line in next_lines_comments:
                    # Adjust indentation for inside the array
                    content = comment_line.strip()
                    if content.startswith('# [') and content.endswith(']'):
                        # Handle case where whole array was commented: # [ "value" ]
                        array_content = content[3:-2].strip()  # Remove # [ and ]
                        if array_content:
                            new_lines.append(f"{indent}  # {array_content}\n")
                    elif content.startswith('#'):
                        new_lines.append(f"{indent}  {content}\n")
                    else:
                        new_lines.append(f"{indent}  # {content}\n")
                
                new_lines.append(f"{indent}]\n")
                
                # Skip the original line and comment lines
                i = j
                modified = True
                print(f"  Fixed incomplete assignment: {var_name}")
                continue
        
        new_lines.append(line)
        i += 1
    
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
        print(f"- No incomplete assignments found in {file_path}")
        return False

def find_gni_files(directory):
    """Find all .gni files in directory tree."""
    gni_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.gni'):
                gni_files.append(os.path.join(root, file))
    return gni_files

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_incomplete_assignments.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        sys.exit(1)
    
    gni_files = find_gni_files(directory)
    print(f"Found {len(gni_files)} GNI files to check")
    
    modified_count = 0
    for file_path in gni_files:
        print(f"Checking {file_path}...")
        if fix_incomplete_assignments_in_file(file_path):
            modified_count += 1
    
    print(f"\nCOMPLETE: Fixed incomplete assignments in {modified_count} files")

if __name__ == '__main__':
    main() 