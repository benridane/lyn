# LYN v0.7

インデントの木構造でレイアウトを書くテキスト記法。
Pug風インデント + Tailwindクラス + Emmetの`*N`を組み合わせ、AIが既に知っている記法だけで構成する。

## 基本方針

- **書いてあることは厳密に守る。**
- **書いていないことは常識的な値で補う。**（余白・行間・縦揃え・文字の太さなど）
- ルールの解釈に迷ったら、この仕様書の「例」を優先する。

## ファイルの形

```lyn
# LYN v0.7（仕様: LYN-spec.md）
@color base=#ffffff main=#f08000
@font Josefin Sans
page (...)
  ...
```

- 1行目：バージョンと仕様書名だけを書く
- 続けて `@color`・`@font`（どちらも省略可）
- そのあとにレイアウト本体。**1ファイルに書くのは1ページだけ**（ルール15）

## ルール

1. **入れ子**：2スペースのインデント
2. **要素名**：HTMLの意味タグ、または一般的な部品名（card、button、input など）
3. **書き順**：`要素名 (クラス) "テキスト" @over ...`
4. **レイアウト**：`( )`内にTailwindクラス。装飾は書かない（区切り線 `border` は可）
5. **寸法**：比率で書く。幅は `w-3/5`・`w-[70%]`、高さは `h-[40vh]`・`aspect-[3/1]`
6. **繰り返し**：`*N`（数が不定なら `*n`。変換時は3件程度で仮置き）
7. **子要素の省略**：`>` は子1つ。`:` の後は子を並べて書く。ただし子が全て同じ並びの時だけ使い、縦横が混ざるときはインデントで書く
8. **配色**：`@color base=#xxxxxx main=#xxxxxx accent=#xxxxxx`。使わない色は省略可。指定は `bg-c-main`・`text-c-base`・`border-c-accent`
   - 白・黒・グレーの無彩色は `@color` に入れず、Tailwindの色をそのまま使ってよい（例：`bg-black`・`text-white`・`bg-gray-100`・`text-black/60`）
   - 有彩色（青・赤・オレンジなど）は必ず `@color` の3色から選ぶ。`bg-blue-500` のようなTailwindの有彩色は使わない
9. **重なり**：`@over 対象:辺 量`
   - 辺：top / bottom / left / right
   - 量：自分のサイズ（その方向の幅または高さ）に対する割合
   - `@over` を付けた側が常に手前（z-index）
   - 同じ方向の位置クラス（例：`left-0`）は併記しない。別方向（例：`top-[6%]`）は可
   - `@over` は**兄弟要素どうし**の重なりに使う。親の内側に子を重ねる場合（写真の上のラベルや文字など）は、親に `relative`、子に `absolute bottom-0` などを書く
10. **コメント**：`#` 以降は意図の補足
11. **未指定の補完**：書かれていない余白・行間・縦揃え・文字の太さは、一般的なWebデザインの値で補う。書かれているクラスは変更・削除しない
12. **画像の仮置き**：画像（cover、img、thumb、icon など）はグレーの背景色を付けた枠で仮置きする。`<img src="">` のような壊れた画像にしない
13. **差し込み枠（slot）**：`slot "名前"` は、中身が外から入る場所（記事本文など）。変換するときは、名前を書いたグレーの枠を1つだけ置く。コメントに件数などが書いてあっても、中身を推測して並べない
14. **フォント**：`@font フォント名` でサイト全体のフォントを指定する。省略したら一般的なフォントで補う
15. **1ファイル＝1ページ**：最上位の要素（ルート）は1つだけ。別のページ（トップと記事ページなど）は別のファイルに書く。ヘッダーやフッターが同じでも、それぞれのファイルに書く
16. **不明な点**：元のデータからわからないことは、推測で書かずに `# 不明：…` とコメントで書く。変換するときは、最も単純な配置（重ねない・上から順に並べる・左右に分けない）にし、変換結果の報告で不明点として挙げる

## 例

### `@over` の計算

```lyn
hero (relative aspect-[3/1])
  cover (absolute right-0 w-[70%] h-full)
  title-box (absolute top-[6%] w-1/3 h-[70%]) @over cover:left 10%
```

- cover の左辺はヒーローの 30% の位置
- title-box の幅は 1/3（33.3%）。その 10% = 3.3% をカバーに重ねる
- title-box の右辺 = 30% + 3.3% = 33.3% → 左辺 = 0%
- 結果：`left-0 z-10`

```lyn
cover (relative w-full h-[40vh])
profile (flex flex-col items-center)
  site-icon (w-24 h-24) @over cover:bottom 50%
```

- site-icon の高さ 96px の 50% = 48px をカバー下端に重ねる
- site-icon が profile の最初の子なので、profile に `-mt-12 relative z-10` を付ける

### 親の内側での重なり（`@over` を使わない）

```lyn
card (relative aspect-[3/2])
  img (w-full h-full)
  label (absolute top-0 left-0 bg-c-accent text-white) "カテゴリ"
  caption (absolute bottom-0 inset-x-0 p-2 text-white) "記事タイトル"
```

### 差し込み枠と不明な点

```lyn
keyvisual (w-full)
  cover (w-full)
  body (flex flex-col items-center)  # 不明：文字がカバーに重なるか
    title "サイト名"
main (flex flex-col)
  slot "本文"  # 固定ページの本文。インポーターが入れる
```

- `body` は不明なので、カバーに重ねず、カバーの下に並べる
- `slot "本文"` は「本文」と書いたグレーの枠を1つ置くだけにする

### `:` の使い方

```lyn
# OK：子が全て横並び
item*3 (flex gap-4): date, title

# NG：日付とタイトルは縦、サムネイルは横
item*n (flex justify-between): date, title, thumb

# 正しい書き方：縦横が混ざるならインデント
item*n (flex justify-between)
  meta (flex flex-col): date, title
  thumb (w-1/4)
```
