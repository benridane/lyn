# LYN

インデントの木構造でレイアウトを書くテキスト記法です。Pug風のインデント、Tailwindのクラス、Emmetの `*N` を組み合わせ、AIが既に知っている記法だけで構成しています。

```lyn
# LYN v0.7（仕様: LYN-spec.md）
@color base=#ffffff main=#f08000
page (w-4/5 mx-auto bg-c-base)
  hero (relative aspect-[3/1])
    cover (absolute right-0 w-[70%] h-full)  # カバー写真
    title-box (absolute top-[6%] w-1/3 h-[70%] bg-c-main text-c-base) @over cover:left 10%
      title (text-4xl) "サイト名"
  main (grid grid-cols-[2fr_1fr] gap-12 max-md:grid-cols-1)
    slot "本文"
    aside (flex flex-col gap-6)
```

画面の構造と最小限の見た目（3色とフォント）だけを書き、細かい見た目は実装側に任せます。画面キャプチャより少ない量で、構造・配色・重なりを正確にAIへ伝えられます。

**[LYN Playground](https://benridane.github.io/lyn/)** で、例を図にして見たり、LYNを書いてその場で描いたりできます。

## ファイル

| パス | 内容 |
| --- | --- |
| `LYN-spec.md` | 仕様。AIに常駐させて使うため、最小限に保つ |
| `CHANGELOG.md` | 仕様の変更履歴 |
| `examples/` | レイアウトの例（7つ） |
| `tools/html2lyn.py` | Tailwindで書かれたHTMLからLYNの下書きを作るスクリプト |
| `skills/html-to-lyn/` | HTMLをLYNに変換するためのスキル |
| `playground/` | LYNから見取り図を描くページのひな形 |
| `docs/` | GitHub Pagesで公開するPlayground（`index.html` は生成物） |

## 使い方

仕様書（`LYN-spec.md`）をプロジェクトのナレッジやシステムプロンプトに置き、LYNファイルだけをAIに渡します。

HTMLからLYNの下書きを作るには:

```sh
python3 tools/html2lyn.py page.html > page.lyn
```

## 生成物の更新

`examples/` や `tools/html2lyn.py` を変えたら、次を実行してPlaygroundとスキルを作り直します。

```sh
python3 tools/build.py
```

- `docs/index.html` に `examples/` のLYNを埋め込みます
- `skills/html-to-lyn/SKILL.md` の同梱スクリプトを `tools/html2lyn.py` と同じ内容にします

## ライセンス

MIT（`LICENSE` を参照）
