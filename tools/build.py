#!/usr/bin/env python3
"""生成物を作り直す。

1. examples/*.lyn を catalog/template.html に埋め込み、catalog/index.html を作る
2. tools/html2lyn.py を skills/html-to-lyn/SKILL.md の同梱スクリプト欄に写す

使い方: python3 tools/build.py
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# カタログに載せる順番（ファイル名 → カタログ上の ID）
CATALOG = [('portrait', 'portrait'), ('signboard', 'signboard'), ('magazine', 'magazine'), ('newsroom', 'newsroom'),
           ('mosaic', 'mosaic'), ('nocturne-home', 'nocturne'), ('nocturne-post', 'nocturne-post')]


def build_catalog():
    template = (ROOT / 'catalog' / 'template.html').read_text(encoding='utf-8')
    blocks = []
    for file_id, catalog_id in CATALOG:
        src = (ROOT / 'examples' / f'{file_id}.lyn').read_text(encoding='utf-8')
        if '</script' in src.lower():
            raise SystemExit(f'{file_id}.lyn に </script が含まれています')
        blocks.append(f'<script type="text/plain" id="lyn-{catalog_id}">\n{src}</script>')
    page = template.replace('<!--LYN_SOURCES-->', '\n'.join(blocks))
    title_end = page.index('</title>') + len('</title>')
    style_end = page.index('</style>') + len('</style>')
    # ブラウザで単体で開けるように、head と body を付ける
    out = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + page[:style_end] + '\n</head>\n<body>\n' + page[style_end:].lstrip() + '\n</body>\n</html>\n')
    (ROOT / 'catalog' / 'index.html').write_text(out, encoding='utf-8')
    print('catalog/index.html')


def sync_skill():
    skill = ROOT / 'skills' / 'html-to-lyn' / 'SKILL.md'
    script = (ROOT / 'tools' / 'html2lyn.py').read_text(encoding='utf-8').rstrip()
    text = skill.read_text(encoding='utf-8')
    new, n = re.subn(r'(## 同梱スクリプト（html2lyn\.py）\n\n```python\n).*?(\n```)',
                     lambda m: m.group(1) + script + m.group(2), text, flags=re.S)
    if n != 1:
        raise SystemExit('SKILL.md の同梱スクリプト欄が見つかりません')
    skill.write_text(new, encoding='utf-8')
    print('skills/html-to-lyn/SKILL.md')


if __name__ == '__main__':
    build_catalog()
    sync_skill()
