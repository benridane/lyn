---
name: html-to-lyn
description: HTMLファイルやWebページのURLを、レイアウト記法LYN（.lyn）に変換するときに使う。Tailwindで書かれたHTMLは同梱スクリプトで下書きを作って仕上げ、それ以外は描画して読み取る。
---

# HTMLをLYNに変換する

HTMLから、構造と最小限の見た目だけを残したLYNファイルを作る。HTML→LYNは装飾を捨てる一方通行の変換なので、元に戻すことは目的にしない。

## 最初に

- 会話・プロジェクト・作業フォルダに `LYN-spec.md` があれば、必ず先に読む。規則はそちらが正。以下の「仕上げ」は、その要点を変換作業の順に並べたもの。
- 仕様書が見つからなければ、その旨を伝えたうえで、この手順の規則で書く。

## 手順

### 1. HTMLを用意する

- ファイルならそのまま使う。URLなら生のHTMLを1回だけ取得する。
- 先に、ページに埋め込まれたデータがないか確かめる（`<script id="__NEXT_DATA__">`、`window.INITIAL_STATE=` など）。テーマの設定値（配色・フォント・ナビ・テーマ名）が入っていれば、HTMLの見た目より確かなので、そちらを優先して使う。
- JavaScriptで中身を作るページ（取得したHTMLの本文がほぼ空）は、ヘッドレスブラウザで描画したあとのHTMLを使う。

### 2. 下書きを作る

**Tailwindで書かれたHTML**（`class` に `flex`・`grid`・`w-`・`gap-` などが並ぶ）は、下の「同梱スクリプト」を `html2lyn.py` として書き出して実行する。

```
python3 html2lyn.py input.html > draft.lyn
```

スクリプトがやること：入れ子をインデントにする、レイアウトのクラスだけ残して装飾を捨てる、同じ形の兄弟を `*N` にまとめる、ナビのような文字だけの並びを親の行に `"A" "B"` で並べる、クラスも文字もない入れ子の箱を外す、Tailwind設定から `@color`、Google Fontsから `@font` を拾う。

**Tailwind以外のHTML**（独自のクラス名）は、クラスからレイアウトが読めない。ヘッドレスブラウザで描画し、各要素の `getComputedStyle` と位置から、Tailwindのクラスに置き換えて下書きを手で作る。

- `display`・`flex-direction`・`gap`・`grid-template-columns` → `flex` `flex-col` `gap-*` `grid-cols-*`
- 幅は親に対する割合（`w-1/3`・`w-[70%]`）、高さは画面に対する割合か縦横比（`h-[40vh]`・`aspect-[3/1]`）
- `position: absolute` の要素は、親に対する位置を割合で
- 中身のない入れ子の `div` は省く
- 精度はTailwindの場合より下がる。迷った箇所は「不明」として残す（仕上げの規則9）

### 3. 仕上げる（機械にはできない部分）

下書きの上から順に、次を当てはめる。

1. **名前**：`box` を役割の名前にする（`hero`・`cover`・`card`・`news`・`profile-card` など）。HTMLの意味タグ（header・nav・main・aside・footer）はそのまま。
2. **画像**：写真やアイコンの箱は `cover`・`img`・`thumb`・`icon` などにし、何の写真かをコメントで書く。
3. **重なり**：兄弟どうしが `absolute` で重なっていれば `@over 対象:辺 量` に置き換える。量は「自分のサイズ（その方向の幅か高さ）に対する割合」で計算し直し、同じ方向の位置クラス（例：`left-…`）は消す。親の内側に子を重ねる場合（写真の上の文字など）は、親 `relative`・子 `absolute` のまま残す。
4. **差し込み枠**：CMSが中身を入れる場所（記事本文など）は、中身を並べずに `slot "名前"` にする。
5. **装飾を消す**：残すのはレイアウト・区切り線・文字サイズ・配色だけ。影・角丸・字間・ホバーなどは消す。
6. **配色**：有彩色は `@color base=… main=… accent=…` の3色にまとめ、`bg-c-main`・`text-c-base`・`border-c-accent` で指す。白・黒・グレーはTailwindの色のままでよい。Tailwindの有彩色（`bg-blue-500` など）が残っていたら、3色のどれかに寄せる。
7. **寸法**：pxの固定値は、比率（`w-[70%]`・`h-[40vh]`・`aspect-[3/2]`）に直す。
8. **省略記法**：`>` は子1つ、`:` は子を並べる。`:` は子がすべて同じ並びのときだけ使い、縦横が混ざるならインデントで書く。
9. **不明**：HTMLから判断できないことは推測で書かず、`# 不明：…` とコメントする。
10. **1ファイル1ページ**：最上位の要素は1つだけ。別のページは別ファイルにする。
11. **先頭**：1行目は `# LYN v0.7（仕様: LYN-spec.md）`（仕様書のバージョンに合わせる）。下書きの説明コメントは消す。

### 4. 確かめる

- 描画できる環境なら、LYNを仕様どおりにHTMLへ戻して描画し、元のページと並べて比べる。構造・配色・重なりのずれがあれば直す。
- 元のHTMLとLYNの**文字数**（バイト数ではない）を数えて報告する。

## 渡すもの

- `.lyn` ファイル
- 短い報告：元HTMLとLYNの文字数、推測で補ったところ、「不明」として残したところ

## 同梱スクリプト（html2lyn.py）

```python
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
```
