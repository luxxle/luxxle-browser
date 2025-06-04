#!/usr/bin/env python3
"""
Script to fix malformed assignments created by the incomplete assignments fixer.
Handles patterns like:
1. variable = [] followed by dangling values
2. String assignments converted to arrays incorrectly
3. Incomplete assignments with expressions on next lines
"""

import os
import re
import sys
from pathlib import Path

def fix_malformed_assignments_in_file(file_path):
    """Fix malformed assignments in a GNI file."""
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
        
        # Pattern 1: Empty array followed by dangling value
        # variable = [
        # ]
        #     actual_value
        if (re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\[\s*$', line) and 
            i + 1 < len(lines) and 
            lines[i + 1].strip() == ']' and
            i + 2 < len(lines)):
            
            # Check if next line after ] has a dangling value
            dangling_line = lines[i + 2].strip()
            if (dangling_line and 
                not dangling_line.startswith('#') and
                not dangling_line.startswith('if') and
                not dangling_line.startswith('foreach') and
                not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', dangling_line)):
                
                # Extract variable name and indentation
                match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\[\s*$', line)
                if match:
                    indent = match.group(1)
                    var_name = match.group(2)
                    
                    # Check if the dangling value looks like an array or string
                    if dangling_line.startswith('[') or dangling_line.startswith('"'):
                        # It's an array or string - assign directly
                        new_lines.append(f"{indent}{var_name} = {dangling_line}\n")
                    else:
                        # It's a string without quotes - add quotes
                        new_lines.append(f"{indent}{var_name} = \"{dangling_line}\"\n")
                    
                    # Skip the empty array lines and dangling value
                    i += 3
                    modified = True
                    print(f"  Fixed malformed array assignment: {var_name}")
                    continue
        
        # Pattern 2: Comment about array followed by empty array and dangling value
        # # Initialize as empty array since Brave components have been removed
        # variable = [
        # ]
        #     actual_value
        if (line.strip().startswith('# Initialize as empty array since Brave components have been removed') and
            i + 1 < len(lines) and
            re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\[\s*$', lines[i + 1]) and
            i + 2 < len(lines) and
            lines[i + 2].strip() == ']' and
            i + 3 < len(lines)):
            
            # Check if next line after ] has a dangling value
            dangling_line = lines[i + 3].strip()
            if (dangling_line and 
                not dangling_line.startswith('#') and
                not dangling_line.startswith('if') and
                not dangling_line.startswith('foreach') and
                not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', dangling_line)):
                
                # Extract variable info from assignment line
                assignment_line = lines[i + 1]
                match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\[\s*$', assignment_line)
                if match:
                    indent = match.group(1)
                    var_name = match.group(2)
                    
                    # Check if dangling value looks like it should be in an array
                    if (dangling_line.startswith('"') or 
                        dangling_line.startswith('[')):
                        # Single value or array - assign directly  
                        if dangling_line.startswith('['):
                            new_lines.append(f"{indent}{var_name} = {dangling_line}\n")
                        else:
                            # Single quoted value, put in array
                            new_lines.append(f"{indent}{var_name} = [ {dangling_line} ]\n")
                    else:
                        # Unquoted value - could be variable reference or needs quotes
                        if (any(char in dangling_line for char in ['+', '(', ')', '$', '/']) or
                            dangling_line.replace('_', '').replace('.', '').isalnum()):
                            # Looks like an expression or variable reference
                            new_lines.append(f"{indent}{var_name} = {dangling_line}\n")
                        else:
                            # Plain text, add quotes
                            new_lines.append(f"{indent}{var_name} = \"{dangling_line}\"\n")
                    
                    # Skip the comment, empty array lines, and dangling value
                    i += 4
                    modified = True
                    print(f"  Fixed malformed commented array assignment: {var_name}")
                    continue
        
        # Pattern 3: Look for expressions that are not assignments (dangling expressions)
        stripped = line.strip()
        if (stripped and 
            not stripped.startswith('#') and 
            not stripped.startswith('if') and
            not stripped.startswith('foreach') and
            not stripped.startswith('declare_args') and
            not stripped.startswith('}') and
            not stripped.startswith('{') and
            not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*[=+]', stripped) and
            i > 0):
            
            # Check if previous line was an incomplete assignment or empty array
            prev_line = lines[i - 1].strip()
            if (prev_line == ']' and i > 1):
                # Look back for the variable assignment
                for j in range(i - 2, max(0, i - 5), -1):
                    check_line = lines[j]
                    if re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\[\s*$', check_line):
                        # This is a dangling value from an empty array - already handled above
                        break
            elif re.match(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*$', prev_line):
                # Previous line is incomplete assignment, this line is the value
                match = re.match(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*$', prev_line)
                if match:
                    indent = match.group(1)
                    var_name = match.group(2)
                    
                    # Replace the previous incomplete line and current dangling line
                    new_lines.pop()  # Remove the incomplete assignment we just added
                    
                    # Format the value properly
                    if stripped.startswith('[') or stripped.startswith('"'):
                        new_lines.append(f"{indent}{var_name} = {stripped}\n")
                    else:
                        # Assume it's a string literal if not array or quoted
                        new_lines.append(f"{indent}{var_name} = \"{stripped}\"\n")
                    
                    i += 1
                    modified = True
                    print(f"  Fixed dangling expression for: {var_name}")
                    continue
        
        new_lines.append(line)
        i += 1
    
    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✓ Fixed malformed assignments in {file_path}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    else:
        print(f"- No malformed assignments found in {file_path}")
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
        print("Usage: python fix_malformed_assignments.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        sys.exit(1)
    
    gni_files = find_gni_files(directory)
    print(f"Found {len(gni_files)} GNI files to check for malformed assignments")
    
    modified_count = 0
    for file_path in gni_files:
        print(f"Checking {file_path}...")
        if fix_malformed_assignments_in_file(file_path):
            modified_count += 1
    
    print(f"\nCOMPLETE: Fixed malformed assignments in {modified_count} files")

if __name__ == '__main__':
    main() 