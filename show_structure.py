"""Show project structure"""
from pathlib import Path

def show_tree(path, prefix="", max_depth=4, current_depth=0, ignore_dirs={'.git', '__pycache__', '.pytest_cache', '.venv', 'venv', 'node_modules', 'saved_models'}):
    if current_depth > max_depth:
        return
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        dirs = [x for x in items if x.is_dir() and x.name not in ignore_dirs]
        files = [x for x in items if x.is_file()]
        
        # Show files first
        for file in files:
            size_kb = file.stat().st_size / 1024
            size_str = f"{size_kb:.1f}KB" if size_kb > 0 else "0KB"
            print(f"{prefix}├─ {file.name:40s} ({size_str})")
        
        # Then directories
        for i, dir in enumerate(dirs):
            is_last = (i == len(dirs) - 1)
            print(f"{prefix}├─ {dir.name}/")
            new_prefix = prefix + ("   " if is_last else "│  ")
            show_tree(dir, new_prefix, max_depth, current_depth + 1, ignore_dirs)
    except PermissionError:
        pass

root = Path('c:/Projects/forecasting-system')
print(f"Project Structure: {root.name}/")
print("=" * 70)
show_tree(root)
print("=" * 70)

files = list(root.rglob('*'))
print(f"\nTotal files: {sum(1 for f in files if f.is_file())}")
print(f"Total directories: {sum(1 for f in files if f.is_dir())}")
print(f"\nPython files: {len(list(root.rglob('*.py')))}")
print(f"Documentation files: {len(list(root.rglob('*.md')))}")
print(f"Configuration files: {len(list(root.rglob('*.txt')))}")
