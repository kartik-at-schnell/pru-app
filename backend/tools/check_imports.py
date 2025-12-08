import ast
import os
import sys

root = os.path.abspath(os.path.dirname(__file__) + os.sep + '..')
backend_dir = root

# discover top-level names in backend (folders/files)
entries = os.listdir(backend_dir)
top_level = set()
for e in entries:
    if e.startswith('.') or e == '__pycache__' or e in ('.venv', 'venv'):
        continue
    full = os.path.join(backend_dir, e)
    if os.path.isdir(full):
        # only treat as internal package if it contains __init__.py
        if os.path.isfile(os.path.join(full, '__init__.py')):
            top_level.add(e)
    elif e.endswith('.py'):
        top_level.add(e[:-3])

# normalize
# we'll treat modules starting with any of top_level as internal

missing = []
errors = []

for dirpath, dirnames, filenames in os.walk(backend_dir):
    # skip venv and __pycache__
    if any(part in ('.venv', 'venv', '__pycache__') for part in dirpath.split(os.sep)):
        continue
    for fname in filenames:
        if not fname.endswith('.py'):
            continue
        fpath = os.path.join(dirpath, fname)
        # compute module name relative to backend_dir
        rel = os.path.relpath(fpath, backend_dir)
        mod = rel[:-3].replace(os.sep, '.')
        # if file is __init__, module should be package name
        if fname == '__init__.py':
            mod = os.path.dirname(rel).replace(os.sep, '.')
            if mod == '.':
                mod = ''
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                src = fh.read()
        except Exception as e:
            errors.append((fpath, 'read-error', str(e)))
            continue
        try:
            tree = ast.parse(src, filename=fpath)
        except Exception as e:
            errors.append((fpath, 'parse-error', str(e)))
            continue

        # determine current package parts for resolving relative imports
        # if mod == '' (top-level file), package_parts = []
        pkg_parts = mod.split('.') if mod else []
        # if file is a module (not __init__), its package is pkg_parts[:-1]
        if fname != '__init__.py' and pkg_parts:
            package_for_resolve = pkg_parts[:-1]
        else:
            package_for_resolve = pkg_parts

        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    name = alias.name
                    first = name.split('.')[0]
                    if first in top_level:
                        # resolve to file in backend_dir
                        target = os.path.join(backend_dir, *name.split('.'))
                        ok = False
                        if os.path.isfile(target + '.py') or os.path.isfile(os.path.join(target, '__init__.py')):
                            ok = True
                        if not ok:
                            missing.append((fpath, node.lineno, 'import', name))
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                module = node.module
                level = node.level
                try:
                    lineno = node.lineno
                except Exception:
                    lineno = '?'
                if level and level > 0:
                    # resolve relative imports correctly
                    base = list(package_for_resolve)
                    # Python's semantics: level=1 means current package, level=2 means one level up, etc.
                    if (level - 1) > len(base):
                        missing.append((fpath, lineno, 'relative-import-too-high', '.' * level + (module or '')))
                        return
                    # compute target base by removing (level-1) parts from the end
                    keep = len(base) - (level - 1)
                    target_base = base[:keep] if keep > 0 else []
                    if module:
                        parts = module.split('.')
                        target_parts = target_base + parts
                    else:
                        target_parts = target_base
                    name = '.'.join([p for p in target_parts if p])
                else:
                    name = module
                if not name:
                    # from . import x or from .. import x with resolved base maybe empty -> skip
                    # attempt to check that package_for_resolve itself exists
                    self.generic_visit(node)
                    return
                first = name.split('.')[0]
                if first in top_level:
                    target = os.path.join(backend_dir, *name.split('.'))
                    ok = False
                    if os.path.isfile(target + '.py') or os.path.isfile(os.path.join(target, '__init__.py')):
                        ok = True
                    if not ok:
                        missing.append((fpath, lineno, 'from', node.module or '', level, name))
                self.generic_visit(node)

        v = ImportVisitor()
        v.visit(tree)

# deduplicate missing
uniq_missing = []
seen = set()
for m in missing:
    key = tuple(m)
    if key not in seen:
        uniq_missing.append(m)
        seen.add(key)

# print report
print("Import check report for backend directory:")
print(f"Top-level names considered internal: {sorted(top_level)}")
print()
if not uniq_missing and not errors:
    print("OK: No unresolved internal imports found (static check).")
    sys.exit(0)

if errors:
    print("Errors reading/parsing files:")
    for e in errors:
        print(' -', e[0], e[1], e[2])
    print()

if uniq_missing:
    print("Unresolved internal imports found:")
    for item in uniq_missing:
        if item[2] == 'import':
            fpath, lineno, kind, name = item
            print(f" - {fpath}:{lineno}: import {name} -> no matching .py or package found")
        elif item[2] == 'from':
            fpath, lineno, kind, mod, level, name = item
            print(f" - {fpath}:{lineno}: from {'.'*level + (mod or '')} -> resolved {name} -> no matching file")
        elif item[2] == 'relative-import-too-high':
            fpath, lineno, kind, rep = item
            print(f" - {fpath}:{lineno}: relative import {rep} goes above project root (too many levels)")
    print()
    sys.exit(2)

# fallback
sys.exit(1)
