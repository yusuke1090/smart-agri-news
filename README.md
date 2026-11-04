# スマート農業News

国内外のスマート農業・酪農・畜産・IoT に関するニュースと、アフリカの農業ニュースを、毎朝7時にまとめる Web サイト。

**サイト: https://yusuke1090.github.io/smart-agri-news/**

- 国内外の農業専門メディア・行政・テック系メディア・Google ニュースの RSS から記事を集める
- 各記事に **無料の AI（Ollama + Gemma）が作った日本語のまとめ**を付ける。英語の記事はタイトルも日本語に訳す
- 「酪農・畜産」「スマート農業」「IoT・センサー」「行政・政策」に自動で分類する
- 「🗾 日本」「🌏 海外」のタブで分かれている（記事の舞台で AI が判定）。その中で「日本語の記事」「英語の記事」に分けられる
- 海外のタブは「🌍 アフリカ」「アフリカ以外」にも分けられる。アフリカはスマート農業に限らず農業全般の記事を載せる（カテゴリ「農業全般」）
- 英語の記事は英語の練習にも使えるように、英語のタイトル・英語の説明文・やさしい英語のまとめ（In short）と、日本語訳のタイトル・日本語のまとめを並べて表示する
- ☆ でお気に入りに追加でき、「★ お気に入り」タブで後から見られる（見ているブラウザに保存。30日を過ぎて一覧から消えた記事も残る）
- カテゴリ・キーワード・24時間以内の新着で絞り込める
- 過去30日分を表示する。サイト自身の [RSS](https://yusuke1090.github.io/smart-agri-news/feed.xml) もある
- スマホでも見やすい。ダークモード対応
- [📝 伝言板](https://yusuke1090.github.io/smart-agri-news/board.html) で、将来やりたいこと・アイデア・相談を書き込める

## しくみ

```
毎朝 6:00（日本時間）GitHub Actions が起動
   │
   ├─ build.py が各ニュース元の RSS を取得
   │     → キーワードで関係する記事を選び、カテゴリを付ける
   │     → RSS に説明文がない記事は、記事ページの紹介文（og:description）で補う
   │     → Ollama（Gemma）で、新しい記事の日本語まとめ・訳タイトル・やさしい英語のまとめ・日本／アフリカ／海外の判定を作る
   │     → data/news.json に追記（30日より古いものは消す）
   │     → docs/index.html と docs/feed.xml を作る
   │
   ├─ data/ と docs/ をリポジトリにコミット
   └─ docs/ を GitHub Pages に公開
```

- サーバーも PC も不要。GitHub の無料枠だけで動く
- 実行は早めの 6:00 にしてある（AI を CPU で動かすので時間がかかるのと、GitHub の定期実行は混雑で遅れることがあるため）
- 毎日コミットするので、「60日間更新がないと定期実行が止まる」という GitHub の制限にもかからない

## ニュース元

| 名前 | 種類 | 載せる記事 |
| --- | --- | --- |
| 日本農業新聞・マイナビ農業・AGRI JOURNAL | 農業専門 | 酪農・スマート農業・IoT のキーワードを含むもの |
| 農林水産省 報道発表 | 行政 | 同上（「行政・政策」も付ける） |
| 農畜産業振興機構（ALIC） | 畜産・酪農 | すべて |
| IoT NEWS・MONOist・ITmedia・日刊工業新聞 | テック | 農業・畜産に関係する言葉を含むもの |
| Google ニュース | キーワード検索 | スマート農業、スマート畜産、酪農、畜産 IoT、農業 IoT、農業 AI |
| AgFunderNews・Future Farming・PrecisionAg・DairyReporter（海外） | 専門 | すべて |
| Farm Progress・Agriland・FeedNavigator（海外） | 農業全般 | 酪農・スマート農業・IoT のキーワードを含むもの |
| Google News（英語） | キーワード検索 | smart farming / agtech、dairy technology / precision livestock、agriculture IoT / farm sensors |
| AllAfrica・Kilimo News・Smart Farmer Kenya・FarmBiz Africa・Farmers Review Africa（アフリカ） | 農業 | すべて |
| TechCabal・Disrupt Africa（アフリカ） | テック | 農業に関係する言葉を含むもの |
| Google News（ケニア・タンザニア・アフリカ） | キーワード検索 | 農業・酪農・畜産・アグリテック |

ニュース元やキーワードは `build.py` の `SOURCES`・`CATEGORIES`・`AGRI_WORDS` で変えられる。

## AI のまとめ（Ollama + Gemma）

- GitHub Actions の中で [Ollama](https://ollama.com) を入れ、無料のモデル `gemma4:e4b` でまとめを作る。API キーやサブスクリプションは不要
- モデルは Actions のキャッシュに保存するので、毎回はダウンロードしない
- 渡すのは記事のタイトル・説明文・配信元だけ。記事の本文は読まない
- 1回に8件ずつ、1回の実行で最大150件まとめる。残りは次の回に回る。一度まとめた記事はやり直さない（失敗した記事は2回まで試す）
- Ollama が使えないときは、まとめなしでサイトだけ更新される（RSS の説明文を表示）
- Google ニュース経由の記事は説明文がないので、タイトルから分かる範囲の短いまとめになる

環境変数で変えられること:

| 変数 | 既定 | 意味 |
| --- | --- | --- |
| `SUMMARY_BACKEND` | `ollama` | `claude` にすると Claude Code（`claude -p`）を使う |
| `OLLAMA_MODEL` | `gemma4:e4b` | Ollama のモデル |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama の場所 |
| `SUMMARY_MAX_PER_RUN` | `300`（Actions では `150`） | 1回の実行でまとめる記事の上限 |
| `SUMMARY_MODEL` | `haiku` | Claude Code を使うときのモデル |

## 伝言板

- 書き込みは GitHub の Issues に保存する。ラベル「伝言板」が付いた、開いている Issue が [board.html](https://yusuke1090.github.io/smart-agri-news/board.html) に出る
- ページは開くたびに GitHub の API から読み込むので、書き込みはすぐに反映される（サイトの作り直しは不要）
- 書き込むには GitHub のアカウントが必要。「＋ 書き込む」から専用のフォーム（`.github/ISSUE_TEMPLATE/board.yml`）が開き、ラベルは自動で付く
- 編集は GitHub の Issue の画面で行う。自分の書き込みは本人が直せる。リポジトリの持ち主はすべての書き込みを直せる・消せる
- Issue を Close すると伝言板から消える。Issues は公開なので、書き込みは誰でも読める

## 手元で動かす

Python 3.10 以上があれば、追加のライブラリは不要。

```sh
python3 build.py            # ニュースを取得して docs/ を作る
ollama pull gemma4:e4b       # 初回だけ。まとめ用のモデルを入れる
python3 build.py --summarize  # さらに Ollama でまとめを作る
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
site/board.html                伝言板のページ（そのまま docs/ にコピーされる）
data/news.json                 集めた記事（過去30日分）
docs/                          公開されるサイト（build.py が作る。手で編集しない）
.github/workflows/update.yml   毎朝の自動更新
```

## 注意

- 載せているのは、タイトル・短い抜粋（または AI のまとめ）・リンクだけ。記事の著作権は各配信元にある
- AI のまとめは誤りを含むことがある（サイトにもその旨を書いている）
- カテゴリはキーワードによる自動分類なので、内容と合わないことがある
- ニュース元の RSS の URL が変わると、そのニュース元は取得できなくなる（サイトの一番下に取得状況が出る）
