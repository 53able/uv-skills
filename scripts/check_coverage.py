#!/usr/bin/env python3
"""Validate the frozen official page inventory and local guidance mappings."""
import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree

def check(root):
    manifest = json.loads((root / 'docs/coverage/coverage.json').read_text())
    inventory = {e.text for e in ElementTree.parse(root / 'docs/coverage/sitemap.xml').iter() if e.tag.endswith('loc')}
    pages = manifest['pages']
    urls = [p['url'] for p in pages]
    assert len(urls) == len(set(urls)), 'Duplicate source URLs'
    assert set(urls) == inventory, 'Inventory differs from frozen official sitemap'
    covered = 0
    for page in pages:
        if not page.get('reference'):
            continue
        filename, anchor = page['reference'].split('#')
        path = (root / 'skills/uv' / filename).resolve()
        assert path.is_relative_to(root.resolve()), 'Reference escapes skill'
        text = path.read_text()
        marker = f'<a id="{anchor}"></a>'
        assert text.count(marker) == 1, f'Missing/duplicate anchor: {page["url"]}'
        section = text.split(marker, 1)[1].split('<a id=', 1)[0]
        assert len(section.replace(page['url'], '').strip()) >= 100, f'Empty guidance: {page["url"]}'
        assert re.fullmatch('[a-f0-9]{64}', page['source_sha256']), 'Missing source fingerprint'
        covered += 1
    percent = covered / len(inventory) * 100
    assert percent >= 85, f'Coverage below target: {percent:.2f}%'
    print(f'Page guidance coverage: {covered}/{len(inventory)} = {percent:.2f}% (target >=85%)')
    print('Inventory, unique anchors and nonempty guidance passed. Semantic correctness requires review.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    check(parser.parse_args().repo)
