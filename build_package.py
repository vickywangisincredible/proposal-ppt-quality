#!/usr/bin/env python3
"""Build the portable skill archive and a plain instruction attachment."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib
import re

ROOT = Path(__file__).resolve().parent
VERSION = '1.1.0'

def build():
    source = ROOT / 'SKILL.md'
    text = source.read_text(encoding='utf-8')
    assert text.startswith('---\nname: proposal-ppt-quality\n'), 'Unexpected skill metadata'
    assert not re.search(r'(?:/Users/|/private/tmp/|[A-Z]:\\Users\\)', text), 'Local path in skill'
    assert not re.search(r'\]\((?!https?://)[^)]+\)', text), 'Unresolved relative resource link'
    body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
    dist = ROOT
    dist.mkdir(exist_ok=True)
    plain = dist / 'PPT优化通用指令.md'
    plain.write_text(body, encoding='utf-8')
    archive = dist / f'proposal-ppt-quality-v{VERSION}.zip'
    entries = {
        'proposal-ppt-quality/SKILL.md': source.read_bytes(),
        'proposal-ppt-quality/LICENSE': (ROOT / 'LICENSE').read_bytes(),
    }
    with ZipFile(archive, 'w', ZIP_DEFLATED) as zip_out:
        for name, data in entries.items():
            info = ZipInfo(name, date_time=(2026, 11, 11, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zip_out.writestr(info, data)
    with ZipFile(archive) as zip_in:
        assert zip_in.testzip() is None, 'Archive corruption'
        assert set(zip_in.namelist()) == set(entries)
        for name, data in entries.items():
            assert zip_in.read(name) == data, name
    (dist / 'SHA256SUMS').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n'
        for p in [archive, plain]
    ), encoding='utf-8')
    print(f'Built and checked v{VERSION}: {len(entries)} ZIP entries.')

if __name__ == '__main__':
    build()
