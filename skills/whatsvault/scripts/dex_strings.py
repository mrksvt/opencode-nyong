#!/usr/bin/env python3
"""Dump unique strings from all classes*.dex in a directory or from an APK.

Usage:
  python3 dex_strings.py SRC OUT
    SRC = dir containing *.dex  OR  path to a .apk (extracts classes*.dex)
    OUT = output text file (one string per line, sorted, unique)

DEX string_ids point to string_data_item: uleb128 utf16_size then MUTF-8 bytes
terminated by NUL. This parser walks the string_ids list only (fast, no full
decode). MUTF-8 is decoded loosely to UTF-8; embedded NULs split strings, which
matches how anchor literals are stored.
"""
import struct, sys, os, zipfile, tempfile, shutil


def uleb128(buf, off):
    result = 0
    shift = 0
    while True:
        b = buf[off]
        off += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, off
        shift += 7


def parse_dex(path):
    with open(path, 'rb') as f:
        buf = f.read()
    if buf[:4] != b'dex\n':
        return set()
    string_ids_size = struct.unpack_from('<I', buf, 0x38)[0]
    string_ids_off = struct.unpack_from('<I', buf, 0x3C)[0]
    out = set()
    for i in range(string_ids_size):
        data_off = struct.unpack_from('<I', buf, string_ids_off + i * 4)[0]
        try:
            _sz, start = uleb128(buf, data_off)
        except IndexError:
            continue
        end = buf.find(b'\x00', start)
        if end < 0:
            continue
        raw = buf[start:end]
        try:
            s = raw.decode('utf-8', 'replace')
        except Exception:
            continue
        out.add(s)
    return out


def collect(src):
    dex_files = []
    tmp = None
    if os.path.isfile(src) and src.lower().endswith('.apk'):
        tmp = tempfile.mkdtemp(prefix='dexstrings_')
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.startswith('classes') and n.endswith('.dex'):
                    z.extract(n, tmp)
                    dex_files.append(os.path.join(tmp, n))
    elif os.path.isdir(src):
        for root, _, files in os.walk(src):
            for fn in files:
                if fn.endswith('.dex'):
                    dex_files.append(os.path.join(root, fn))
    else:
        raise SystemExit(f'SRC must be a .apk or a dir of .dex: {src}')
    strings = set()
    for d in dex_files:
        strings |= parse_dex(d)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    return strings


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    strings = collect(src)
    with open(out, 'w', encoding='utf-8') as f:
        for s in sorted(strings):
            f.write(s + '\n')
    print(f'{len(strings)} strings -> {out}')


if __name__ == '__main__':
    main()
