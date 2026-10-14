#!/usr/bin/env python3
"""Update supported_versions arrays in WhatsVault arrays.xml.

Usage:
  python3 update_arrays.py ARRAYS_XML VERSION
    VERSION e.g. 2.26.36.87  ->  inserts <item>2.26.36.xx</item>
                                  into supported_versions_wpp AND _business
Idempotent: existing prefix entries are never duplicated.
"""
import re
import sys

ARR_RE = re.compile(
    r'(<string-array name="supported_versions_(?:wpp|business)">)(.*?)(</string-array>)',
    re.S)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    path, version = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+', version):
        raise SystemExit(f'bad VERSION {version!r}, want x.x.x.x like 2.26.36.87')
    prefix = '.'.join(version.split('.')[:3])
    entry = f'{prefix}.xx'

    xml = open(path, encoding='utf-8').read()

    def patch(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)
        if re.search(r'<item>%s</item>' % re.escape(entry), body):
            return m.group(0)
        # insert entry after the highest existing 2.26.*.xx (numeric order)
        items = re.findall(r'<item>([\d.]+\.xx)</item>', body)
        if items:
            top = max(items, key=lambda s: [int(x) for x in s[:-3].split('.')])
            body = body.replace(
                f'<item>{top}</item>',
                f'<item>{top}</item>\n        <item>{entry}</item>', 1)
        else:
            body = body.rstrip() + f'\n        <item>{entry}</item>\n    '
        return head + body + tail

    new_xml, n = ARR_RE.subn(patch, xml)
    open(path, 'w', encoding='utf-8').write(new_xml)
    print(f'{entry}: patched in {n} array(s) at {path}')


if __name__ == '__main__':
    main()
