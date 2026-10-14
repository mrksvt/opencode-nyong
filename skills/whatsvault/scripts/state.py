#!/usr/bin/env python3
"""Tiny pipeline state file for /whatsvault resume support.

Usage:
  python3 state.py init   [VER]        # create/reset .target/wv_state.json
  python3 state.py done   STEP        # mark step complete (pull, decompile,
                                      # analysis, fallback, arrays, build,
                                      # commit, rebuild, install)
  python3 state.py skipped STEP [why] # mark step skipped
  python3 state.py show               # print current state
"""
import json
import os
import sys
from datetime import datetime, timezone

STEPS = ['pull', 'decompile', 'analysis', 'fallback', 'arrays',
         'build', 'commit', 'rebuild', 'install']
PATH = os.path.join('.target', 'wv_state.json')


def load():
    if os.path.exists(PATH):
        with open(PATH) as f:
            return json.load(f)
    return {}


def save(st):
    os.makedirs('.target', exist_ok=True)
    with open(PATH, 'w') as f:
        json.dump(st, f, indent=1)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    st = load()
    if cmd == 'init':
        ver = sys.argv[2] if len(sys.argv) > 2 else None
        st = {'version': ver, 'started': datetime.now(timezone.utc).isoformat(),
              'steps': {}}
    elif cmd in ('done', 'skipped'):
        step = sys.argv[2]
        if step not in STEPS:
            raise SystemExit(f'step must be one of {STEPS}')
        st.setdefault('steps', {})[step] = {
            'status': cmd,
            'at': datetime.now(timezone.utc).isoformat(),
            'note': sys.argv[3] if len(sys.argv) > 3 else ''}
    elif cmd == 'show':
        pass
    else:
        raise SystemExit(__doc__)
    save(st)
    print(json.dumps(st, indent=1))


if __name__ == '__main__':
    main()
