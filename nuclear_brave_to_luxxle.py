#!/usr/bin/env python3
"""
NUCLEAR OPTION: Replace ALL brave references with luxxle
Only preserves "The Brave Authors" in copyright lines
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def should_skip_file(file_path):
    """Check if file should be skipped"""
    skip_extensions = {
        '.exe', '.dll', '.so', '.dylib', '.a', '.lib', '.obj', '.o',
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp',
        '.mp4', '.mp3', '.wav', '.avi', '.mov',
        '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.ttf', '.otf', '.woff', '.woff2',
        '.pdb', '.map', '.bin', '.dat'
    }
    
    return file_path.suffix.lower() in skip_extensions

def is_text_file(file_path):
    """Check if file is a text file"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            if not chunk:
                return True
            # Check for null bytes
            if b'\0' in chunk:
                return False
            # Check for high ratio of printable characters
            printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
            return len(chunk) > 0 and printable_chars / len(chunk) > 0.7
    except Exception:
        return False

def is_copyright_line(line):
    """Check if line contains copyright that should be preserved (except The Brave Authors)"""
    line_lower = line.lower().strip()
    
    # Only preserve these specific copyright patterns
    copyright_patterns = [
        'copyright',
        '(c)',
        '©',
        'mozilla public license',
        'apache license',
        'mit license',
        'bsd license',
        'license, v. 2.0',
        'source code form',
    ]
    
    # Check if it's a copyright line
    for pattern in copyright_patterns:
        if pattern in line_lower:
            # But still allow "The Brave Authors" to be changed
            if 'the brave authors' in line_lower:
                return False
            return True
    
    return False

def process_file(file_path):
    """Process a single file with NUCLEAR replacement"""
    if not is_text_file(file_path):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        modified_lines = []
        
        for line in lines:
            # Only preserve copyright lines (but not "The Brave Authors")
            if is_copyright_line(line):
                modified_lines.append(line)
                continue
            
            # NUCLEAR REPLACEMENT - Replace ALL instances
            modified_line = line
            
            # Replace ALL brave/Brave/BRAVE with luxxle/Luxxle/LUXXLE
            modified_line = modified_line.replace('brave', 'luxxle')
            modified_line = modified_line.replace('Brave', 'Luxxle')  
            modified_line = modified_line.replace('BRAVE', 'LUXXLE')
            
            # Fix any potential double replacements
            modified_line = modified_line.replace('luxxleluxxle', 'luxxle')
            modified_line = modified_line.replace('LuxxleLuxxle', 'Luxxle')
            modified_line = modified_line.replace('LUXXLELUXXLE', 'LUXXLE')
            
            # Fix common words that shouldn't be changed
            modified_line = modified_line.replace('luxxlely', 'bravely')
            modified_line = modified_line.replace('Luxxlely', 'Bravely')
            modified_line = modified_line.replace('luxxlery', 'bravery')
            modified_line = modified_line.replace('Luxxlery', 'Bravery')
            
            modified_lines.append(modified_line)
        
        new_content = '\n'.join(modified_lines)
        
        if new_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"NUKED: {file_path}")
            return True
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
    
    return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='NUCLEAR OPTION: Replace ALL brave references with luxxle')
    parser.add_argument('directory', nargs='?', default='src/luxxle', 
                       help='Directory to process (default: src/luxxle)')
    parser.add_argument('-y', '--yes', action='store_true', 
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    target_dir = Path(args.directory)
    
    if not target_dir.exists():
        logger.error(f"Directory not found: {target_dir}")
        return
    
    logger.info(f"NUCLEAR REPLACEMENT starting in: {target_dir}")
    logger.info("This will replace ALL 'brave' with 'luxxle' except in copyright lines")
    
    if not args.yes:
        response = input("Continue with NUCLEAR replacement? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    files_processed = 0
    files_updated = 0
    
    # Process all files recursively
    for file_path in target_dir.rglob('*'):
        if file_path.is_file() and not should_skip_file(file_path):
            files_processed += 1
            if process_file(file_path):
                files_updated += 1
            
            if files_processed % 100 == 0:
                logger.info(f"Processed {files_processed} files, updated {files_updated}")
    
    logger.info(f"NUCLEAR REPLACEMENT COMPLETE!")
    logger.info(f"Processed {files_processed} files, updated {files_updated} files")
    logger.info("Use 'git diff' to review changes.")

if __name__ == "__main__":
    main()