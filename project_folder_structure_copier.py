import os
import sys
from pathlib import Path
import fnmatch
import io
import pyperclip

def should_ignore(path, ignore_patterns):
    if '.git' in path.split(os.sep):
        return True
    
    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            if path.startswith(pattern) or path.startswith('./' + pattern):
                return True
        elif fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    return False

def read_gitignore(root_path):
    gitignore_path = os.path.join(root_path, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

def generate_directory_structure(startpath, ignore_patterns):
    output = io.StringIO()
    for root, dirs, files in os.walk(startpath, topdown=True):
        level = root.replace(startpath, '').count(os.sep)
        indent = '|   ' * (level - 1) + '+-- '
        rel_path = os.path.relpath(root, startpath)
        
        if rel_path == '.':
            print(os.path.basename(startpath) + '/', file=output)
        elif not should_ignore(rel_path, ignore_patterns):
            print(f'{indent}{os.path.basename(root)}/', file=output)
        else:
            dirs[:] = []  # Don't recurse into ignored directories
            continue
        
        subindent = '|   ' * level + '+-- '
        for f in files:
            file_path = os.path.join(rel_path, f)
            if not should_ignore(file_path, ignore_patterns):
                print(f'{subindent}{f}', file=output)
        
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(rel_path, d), ignore_patterns)]
    
    return output.getvalue()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <path_to_project>")
        sys.exit(1)

    project_path = sys.argv[1]
    if not os.path.exists(project_path):
        print(f"The specified path does not exist: {project_path}")
        sys.exit(1)

    ignore_patterns = read_gitignore(project_path)
    structure = generate_directory_structure(project_path, ignore_patterns)
    
    try:
        print(structure)  # Try to print to console
    except UnicodeEncodeError:
        print(structure.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    
    pyperclip.copy(structure)  # Copy to clipboard
    print("\nDirectory structure has been copied to clipboard.")