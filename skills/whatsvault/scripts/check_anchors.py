#!/usr/bin/env python3
"""Diff WhatsVault string literals vs a WhatsApp string pool.

Usage:
  python3 check_anchors.py UNOBFUSCATOR_KT NEW_POOL [BASELINE_POOL]

Classifies every quoted literal in the Kotlin file:
  OK            whole-entry present in NEW pool
  OK-CONTAINS   substring of NEW pool entries (DexKit default mode is Contains,
                so most finders are fine; still eyeball the printed line)
  REGRESSION    present in BASELINE pool but gone from NEW  -> needs fallback
  DEAD          absent from BOTH pools (stale pre-existing anchor, not a
                new-version problem; leave it unless its feature matters)
  NO-BASELINE   absent from NEW and no baseline given -> manual review

Exit codes: 0 = clean, 2 = REGRESSION found, 3 = literals need manual review
(NO-BASELINE without clean baseline). Ignores pure-hex, short (<3), and
numeric .toLong() constants.
"""
import re
import sys


def load(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return set(line.rstrip('\n') for line in f)


STRING_RE = re.compile(r'"((?:[^"\\\n]|\\.)+)"')


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    kt, newp = sys.argv[1], sys.argv[2]
    basep = sys.argv[3] if len(sys.argv) > 3 else None

    new = load(newp)
    base = load(basep) if basep else None
    new_blob = '\x00'.join(new)
    base_blob = '\x00'.join(base) if base is not None else None

    seen = {}
    with open(kt, encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            for m in STRING_RE.finditer(line):
                s = m.group(1)
                if s not in seen:
                    seen[s] = i

    stats = {'OK': 0, 'OK-CONTAINS': 0, 'REGRESSION': 0, 'DEAD': 0,
             'NO-BASELINE': 0}
    suspects = []
    for s, ln in sorted(seen.items(), key=lambda kv: kv[1]):
        if len(s) < 3:
            continue
        if re.fullmatch(r'[0-9a-fA-FxX.]+', s):   # hex masks, numbers
            continue
        if re.fullmatch(r'\d+', s):
            continue
        if s in new:
            stats['OK'] += 1
            continue
        if s in new_blob:
            stats['OK-CONTAINS'] += 1
            continue
        in_base = base is not None and (s in base or s in base_blob)
        if in_base:
            stats['REGRESSION'] += 1
            suspects.append((ln, 'REGRESSION', s))
        elif base is not None:
            stats['DEAD'] += 1
        else:
            stats['NO-BASELINE'] += 1
            suspects.append((ln, 'NO-BASELINE', s))

    print(f'{len(seen)} literals. ' + ' '.join(
        f'{k}={v}' for k, v in stats.items()))
    if suspects:
        print('\n=== SUSPECT (open UNOBFUSCATOR_KT at line, inspect call site; '
              'if it is inside addUsingString/usingStrings it needs a '
              'fallback anchor) ===')
        for ln, kind, s in suspects:
            print(f'{kind:11} {kt}:{ln}  {s[:80]!r}')
    sys.exit(2 if stats['REGRESSION'] else (3 if stats['NO-BASELINE'] else 0))


if __name__ == '__main__':
    main()
