import os
import pathlib
exclude = {'_site', 'output', '.git'}
text_ext = {'.py', '.html', '.htm', '.css', '.js', '.json', '.yml', '.yaml', '.xml', '.scss', '.sass'}
total = 0
files_by_ext = {}
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude]
    if pathlib.Path(root).name in exclude:
        continue
    for name in files:
        ext = pathlib.Path(name).suffix.lower()
        if ext not in text_ext:
            continue
        path = pathlib.Path(root) / name
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as f:
                count = sum(1 for _ in f)
        except Exception:
            continue
        total += count
        stats = files_by_ext.setdefault(ext, {'files': 0, 'lines': 0})
        stats['files'] += 1
        stats['lines'] += count
print(total)
for ext, stats in sorted(files_by_ext.items(), key=lambda item: item[1]['lines'], reverse=True):
    print(f"{ext}\t{stats['files']}\t{stats['lines']}")
