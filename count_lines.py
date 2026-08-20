import os
import pathlib
exclude = {'_site', 'output', '.git'}
files_by_ext = {}
total = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude]
    if pathlib.Path(root).name in exclude:
        continue
    for name in files:
        path = pathlib.Path(root) / name
        try:
            with path.open('rb') as f:
                count = sum(1 for _ in f)
        except Exception:
            continue
        total += count
        ext = path.suffix.lower() or '(none)'
        stats = files_by_ext.setdefault(ext, {'files': 0, 'lines': 0})
        stats['files'] += 1
        stats['lines'] += count
print(total)
for ext, stats in sorted(files_by_ext.items(), key=lambda item: item[1]['lines'], reverse=True):
    print(f"{ext}\t{stats['files']}\t{stats['lines']}")
