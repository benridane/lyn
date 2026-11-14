#!/usr/bin/env python3
"""Tailwind で書かれた HTML を LYN の下書きに機械的に変換する（AI は使わない）。

使い方: python3 html2lyn.py input.html > draft.lyn
出力は下書き。要素名・@over・コメント・不明点は、このあと人か AI が仕上げる。
"""
import re
import sys
from html.parser import HTMLParser

VOID = {'img', 'input', 'br', 'hr', 'meta', 'link', 'source'}
SKIP = {'script', 'style', 'head', 'title', 'noscript', 'svg', 'template'}
RENAME = {'h1': 'title', 'h2': 'heading', 'h3': 'heading', 'h4': 'heading', 'h5': 'heading', 'h6': 'heading',
          'p': 'text', 'a': 'link', 'span': 'text', 'ul': 'list', 'ol': 'list', 'li': 'item', 'hr': 'divider',
          'time': 'date', 'figure': 'img', 'form': 'form', 'label': 'label'}
KEEP_TAG = {'header', 'nav', 'main', 'section', 'aside', 'footer', 'article', 'button', 'img', 'input', 'textarea', 'select'}
# レイアウトとして残すクラス（これ以外は装飾として捨てる）
KEEP = re.compile(r'^(?:(?:max-)?(?:sm|md|lg|xl):)?-?(?:'
                  r'flex|flex-col|flex-row|flex-wrap|flex-1|grid|grid-cols-.+|col-span-.+|row-span-.+|gap(?:-[xy])?-.+|'
                  r'w-.+|h-.+|min-[wh]-.+|max-[wh]-.+|aspect-.+|justify-.+|items-.+|self-.+|'
                  r'absolute|relative|sticky|fixed|inset(?:-[xy])?-.+|top-.+|left-.+|right-.+|bottom-.+|z-.+|'
                  r'mx-auto|m[tb]-.+|hidden|'
                  r'border|border-[tblrxy](?:-\d)?|border-c-.+|bg-c-.+|text-c-.+|'
                  r'bg-(?:white|black|gray-\d+)(?:/\d+)?|text-(?:white|black|gray-\d+)(?:/\d+)?|'
                  r'text-(?:xs|sm|base|lg|\dxl))$')
UTILITY_LIKE = re.compile(r'^(?:[a-z]+:)*-?(?:font|text|bg|tracking|leading|shrink|grow|outline|hover|focus|border|'
                          r'p[xytblr]?|m[xytblr]?|rounded|block|inline|hidden|list|underline|object|overflow|opacity|'
                          r'shadow|transition|duration|ease|cursor|select|whitespace|truncate|uppercase|italic|sr)(?:-|$)')


class Node:
    def __init__(self, tag, cls):
        self.tag, self.cls, self.kids, self.text = tag, cls, [], ''


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Node('root', [])
        self.stack = [self.root]
        self.skip = 0
        self.colors = {}
        self.font = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and 'fonts.googleapis.com' in (a.get('href') or '') and not self.font:
            m = re.search(r'family=([^:&]+)', a['href'])
            if m:
                self.font = m.group(1).replace('+', ' ')
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip or tag in ('html', 'body', 'br', 'meta', 'link', 'source'):
            return
        n = Node(tag, (a.get('class') or '').split())
        self.stack[-1].kids.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag in VOID or tag in ('html', 'body'):
            return
        # 閉じ忘れに強くする: 同じタグまで戻る
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.skip:
            # Tailwind v3 の設定と v4 の @theme の両方から色を拾う
            for k, v in re.findall(r"['\"]?c-(base|main|accent)['\"]?\s*:\s*['\"](#[0-9a-fA-F]{3,8})", data):
                self.colors[k] = v
            for k, v in re.findall(r'--color-c-(base|main|accent)\s*:\s*(#[0-9a-fA-F]{3,8})', data):
                self.colors[k] = v
            return
        t = ' '.join(data.split())
        if t:
            self.stack[-1].text = (self.stack[-1].text + ' ' + t).strip()


def keep(n):
    return [c for c in n.cls if KEEP.match(c)]


def name(n):
    if n.tag in RENAME and n.tag not in ('span', 'a') or n.tag in KEEP_TAG:
        own = [c for c in n.cls if not KEEP.match(c) and not UTILITY_LIKE.match(c) and re.match(r'^[a-z][a-z0-9-]*$', c)]
        if n.tag in ('section', 'div') and own:
            return own[0]
        return RENAME.get(n.tag, n.tag)
    own = [c for c in n.cls if not KEEP.match(c) and not UTILITY_LIKE.match(c) and re.match(r'^[a-z][a-z0-9-]*$', c)]
    if own:
        return own[0]
    return RENAME.get(n.tag, 'box')


def simplify(n):
    """クラスも文字も持たない入れ子だけの箱を外す"""
    kids = []
    for k in n.kids:
        simplify(k)
        if k.tag in ('div', 'span') and not keep(k) and not k.text and len(k.kids) == 1 and name(k) == 'box':
            kids.append(k.kids[0])
        elif k.tag in ('div', 'span') and not keep(k) and not k.text and not k.kids:
            continue
        else:
            kids.append(k)
    n.kids = kids


def shape(n):
    """文字を無視した形。同じ形の兄弟は *N にまとめる"""
    return (name(n), tuple(keep(n)), tuple(shape(k) for k in n.kids))


def quote(t):
    return '"' + t.replace('"', '”') + '"'


def groups_of(n):
    out, i = [], 0
    while i < len(n.kids):
        j = i
        while j + 1 < len(n.kids) and shape(n.kids[j + 1]) == shape(n.kids[i]):
            j += 1
        out.append(n.kids[i:j + 1])
        i = j + 1
    return out


def text_leaves(g):
    return all(not x.kids and x.text for x in g)


def emit(n, depth, out):
    for g in groups_of(n):
        k = g[0]
        cls = keep(k)
        line = '  ' * depth + name(k) + (f'*{len(g)}' if len(g) > 1 else '')
        if cls:
            line += ' (' + ' '.join(cls) + ')'
        if len(g) == 1 and k.text:
            line += ' ' + quote(k.text)
        kg = groups_of(k) if len(g) == 1 else []
        # 子が「文字だけの同じ形の葉」の1グループなら（ナビ・タグなど）、子を書かずに文字を並べる
        if len(kg) == 1 and len(kg[0]) > 1 and text_leaves(kg[0]) and not keep(kg[0][0]) and not k.text:
            line += ' ' + ' '.join(quote(x.text) for x in kg[0])
            out.append(line)
            continue
        if len(g) > 1 and text_leaves(g):
            line += '  # ' + ' / '.join(x.text for x in g)
        out.append(line)
        emit(k, depth + 1, out)


def convert(html):
    p = Parser()
    p.feed(html)
    simplify(p.root)
    out = ['# LYN v0.7（仕様: LYN-spec.md）', '# html2lyn.py による下書き。要素名・@over・不明点を仕上げること']
    if p.colors:
        out.append('@color ' + ' '.join(f'{k}={p.colors[k]}' for k in ('base', 'main', 'accent') if k in p.colors))
    if p.font:
        out.append('@font ' + p.font)
    emit(p.root, 0, out)
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    src = open(sys.argv[1], encoding='utf-8').read() if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(convert(src))
