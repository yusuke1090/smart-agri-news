# スマート農業・酪農 IoT ニュース

スマート農業・酪農・畜産・IoT に関するニュースを、毎朝7時にまとめる Web サイト。

**サイト: https://yusuke1090.github.io/smart-agri-news/**

- 農業専門メディア・行政・テック系メディア・Google ニュースの RSS から記事を集める
- 「酪農・畜産」「スマート農業」「IoT・センサー」「行政・政策」に自動で分類する
- カテゴリ・キーワード・24時間以内の新着で絞り込める
- 過去30日分を表示する。サイト自身の [RSS](https://yusuke1090.github.io/smart-agri-news/feed.xml) もある
- スマホでも見やすい。ダークモード対応

## しくみ

```
毎朝 6:40（日本時間）GitHub Actions が起動
   │
   ├─ build.py が各ニュース元の RSS を取得
   │     → キーワードで関係する記事を選び、カテゴリを付ける
   │     → data/news.json に追記（30日より古いものは消す）
   │     → docs/index.html と docs/feed.xml を作る
   │
   ├─ data/ と docs/ をリポジトリにコミット
   └─ docs/ を GitHub Pages に公開
```

- サーバーも PC も不要。GitHub の無料枠だけで動く
- 実行は少し早めの 6:40 にしてある（GitHub の定期実行は混雑で遅れることがあるため）
- 毎日コミットするので、「60日間更新がないと定期実行が止まる」という GitHub の制限にもかからない

## ニュース元

| 名前 | 種類 | 載せる記事 |
| --- | --- | --- |
| 日本農業新聞・マイナビ農業・AGRI JOURNAL | 農業専門 | 酪農・スマート農業・IoT のキーワードを含むもの |
| 農林水産省 報道発表 | 行政 | 同上（「行政・政策」も付ける） |
| 農畜産業振興機構（ALIC） | 畜産・酪農 | すべて |
| IoT NEWS・MONOist・ITmedia・日刊工業新聞 | テック | 農業・畜産に関係する言葉を含むもの |
| Google ニュース | キーワード検索 | スマート農業、スマート畜産、酪農、畜産 IoT、農業 IoT、農業 AI |

ニュース元やキーワードは `build.py` の `SOURCES`・`CATEGORIES`・`AGRI_WORDS` で変えられる。

## 手元で動かす

Python 3.10 以上があれば、追加のライブラリは不要。

```sh
python3 build.py            # ニュースを取得して docs/ を作る
python3 build.py --offline  # 取得せずに、今のデータで docs/ だけ作り直す（見た目を直したとき）
xdg-open docs/index.html    # ブラウザで確認
```

## 手動で更新する

GitHub の画面で **Actions → update-news → Run workflow** を押すと、すぐに更新される。
ターミナルからなら:

```sh
gh workflow run update-news
```

## ファイル構成

```
build.py                       ニュースを集めてサイトを作るスクリプト
site/template.html             ページのひな形（デザインはここ）
data/news.json                 集めた記事（過去30日分）
docs/                          公開されるサイト（build.py が作る。手で編集しない）
.github/workflows/update.yml   毎朝の自動更新
```

## 注意

- 載せているのは、各配信元の RSS にあるタイトル・短い抜粋・リンクだけ。記事の著作権は各配信元にある
- カテゴリはキーワードによる自動分類なので、内容と合わないことがある
- ニュース元の RSS の URL が変わると、そのニュース元は取得できなくなる（サイトの一番下に取得状況が出る）
