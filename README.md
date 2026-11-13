# スマート農業News

国内外のスマート農業・酪農・畜産・IoT に関するニュースと、アフリカの農業ニュースを、毎朝7時にまとめる Web サイト。

**サイト: https://yusuke1090.github.io/smart-agri-news/**

- 国内外の農業専門メディア・行政・テック系メディア・Google ニュースの RSS から記事を集める
- 新しい記事には、配信元の説明文を表示する。AI のまとめは自動では作らない（手元で作ることはできる。下の「AI のまとめ」を参照）
- 「酪農・畜産」「スマート農業」「IoT・センサー」「行政・政策」に自動で分類する
- 「🗾 日本」「🌏 海外」のタブで分かれている（記事の舞台をキーワードで判定）。その中で「日本語の記事」「英語の記事」に分けられる
- 海外のタブは「🌍 アフリカ」「アフリカ以外」にも分けられる。アフリカはスマート農業に限らず農業全般の記事を載せる（カテゴリ「農業全般」）
- 英語の記事は英語の練習にも使えるように、英語のタイトル・英語の説明文・やさしい英語のまとめ（In short）と、日本語訳のタイトル・日本語のまとめを並べて表示する
- ☆ でお気に入りに追加でき、「★ お気に入り」タブで後から見られる（見ているブラウザに保存。30日を過ぎて一覧から消えた記事も残る）
- カテゴリ・キーワード・24時間以内の新着で絞り込める
- 過去30日分を表示する。サイト自身の [RSS](https://yusuke1090.github.io/smart-agri-news/feed.xml) もある
- スマホでも見やすい。ダークモード対応
- [📝 伝言板](https://yusuke1090.github.io/smart-agri-news/board.html) で、将来やりたいこと・アイデア・相談を書き込める（合言葉でアカウントなしでも書ける）。「やりたいこと」「アイデア」には、似たことをしている会社・製品を調べた「🔎 関連する事業」を付ける
- 右下の「🔤 訳す」で、英単語や英文を日本語に訳せる（日本語を入れると英語に）。ページの英文を選ぶと出る「🔤 訳す」からも訳せる。調べたものは履歴に 50 件まで残る
- 見出しの 🐄 か、タブの「🐄 教科書」を押すと、[🐄 牛の教科書](https://yusuke1090.github.io/textbooks/?b=cow)（乳牛のからだ・繁殖・エサ・乳房炎・血乳・スマート酪農など 13章と付録。教科書のリポジトリ textbooks にある）が開く。日本語と英語を切り替えられる

## しくみ

```
毎朝 6:40（日本時間）GitHub Actions が起動
   │
   ├─ build.py が各ニュース元の RSS を取得
   │     → キーワードで関係する記事を選び、カテゴリを付ける
   │     → RSS に説明文がない記事は、記事ページの紹介文（og:description）で補う
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
| AgFunderNews・Future Farming・PrecisionAg・DairyReporter（海外） | 専門 | すべて |
| Farm Progress・Agriland・FeedNavigator（海外） | 農業全般 | 酪農・スマート農業・IoT のキーワードを含むもの |
| Google News（英語） | キーワード検索 | smart farming / agtech、dairy technology / precision livestock、agriculture IoT / farm sensors |
| AllAfrica・Kilimo News・Smart Farmer Kenya・FarmBiz Africa・Farmers Review Africa（アフリカ） | 農業 | すべて |
| TechCabal・Disrupt Africa（アフリカ） | テック | 農業に関係する言葉を含むもの |
| Google News（ケニア・タンザニア・アフリカ） | キーワード検索 | 農業・酪農・畜産・アグリテック |

ニュース元やキーワードは `build.py` の `SOURCES`・`CATEGORIES`・`AGRI_WORDS` で変えられる。

## AI のまとめ（手元で作るときだけ）

- 毎朝の自動更新では、AI のまとめは作らない（GitHub の無料のサーバーでは時間がかかりすぎるため）
- 手元の PC で `python3 build.py --summarize` を動かすと、[Ollama](https://ollama.com) の無料のモデル `gemma4:e4b` でまとめを作れる。作ったまとめは push すればサイトに出る
- 渡すのは記事のタイトル・説明文・配信元だけ。記事の本文は読まない
- 1回に8件ずつ、1回の実行で最大300件まとめる。残りは次の回に回る。一度まとめた記事はやり直さない（失敗した記事は2回まで試す）
- Ollama が使えないときは、まとめなしでサイトだけ更新される（RSS の説明文を表示）
- Google ニュース経由の記事は説明文がないので、タイトルから分かる範囲の短いまとめになる

環境変数で変えられること:

| 変数 | 既定 | 意味 |
| --- | --- | --- |
| `SUMMARY_BACKEND` | `ollama` | `claude` にすると Claude Code（`claude -p`）を使う |
| `OLLAMA_MODEL` | `gemma4:e4b` | Ollama のモデル |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama の場所 |
| `SUMMARY_MAX_PER_RUN` | `300` | 1回の実行でまとめる記事の上限 |
| `SUMMARY_MODEL` | `haiku` | Claude Code を使うときのモデル |

## 訳す（🔤）

- `site/translate.js` に全部ある。`build.py` が `docs/` にコピーし（英和辞書の `site/dict/` も）、ニュースのページと伝言板の両方で読み込む
- 右下の「🔤 訳す」か、ページの英文を選ぶと出る「🔤 訳す」で使う。Enter で訳す（Shift + Enter で改行）
- **単語**は単語帳のように、意味と例文を出す
  - 意味: 英和辞書 [EJDict](https://github.com/kujirahand/EJDict)（パブリックドメイン）。`aimed → aim`・`went → go` のように元の形で引く。画面では補足〈…〉を消し、1行に訳語を3つまで、5行まで（残りは「ほか N 件」）
  - 例文: [Tatoeba](https://tatoeba.org/)（人が訳した英文と和文、CC BY 2.0 FR）から、同じ単語（活用した形も）を含むものを2つ。なければページの記事の英文から1つ選んで機械翻訳する
  - 発音記号: [Free Dictionary API](https://dictionaryapi.dev/)（取れないときは出さない）。🔊 で読み上げ
  - 辞書にない単語（sustainable など）は、意味を機械翻訳で出す
- **文章**は訳だけを出す。Chrome では Chrome の翻訳機能（[Translator API](https://developer.chrome.com/docs/ai/translator-api)。PC の中で訳す）、使えないとき（iPhone の Safari など）や初回の準備中は無料の [MyMemory](https://mymemory.translated.net/doc/spec.php)（1回 500 バイトまでなので文の区切りで分けて送る。1日の上限あり）。日本語を入れると英語に訳す
- 履歴は、見ているブラウザの `localStorage`（`agri-news-translate-history`）に新しい順で 50 件まで。意味と例文ごと残すので、押すと問い合わせずに出る
- 英和辞書のデータ（`site/dict/a.json`〜`z.json`、約 4MB）は `tools/make_dict.py` で作る:

```sh
git clone --depth 1 https://github.com/kujirahand/EJDict.git /tmp/EJDict
python3 tools/make_dict.py /tmp/EJDict
```

## 牛の教科書（🐄）

- 牛の教科書は、教科書をまとめたリポジトリ [textbooks](https://github.com/yusuke1090/textbooks) に移った（2026-11-13）。本文・図・用語集はそちらの `books/cow/` で直す
- このサイトからは、見出しの 🐄・タブの「🐄 教科書」・ページの一番下のリンクで、[Web の教科書](https://yusuke1090.github.io/textbooks/?b=cow) を開く
- 前の `cow.html` は、教科書への移動の案内だけを残している（`cow.html#ch=9&lang=en` のような古いリンクも、同じ章のまま移る。読んでいた所の記録も引き継ぐ）
- 教科書のページは、このサイトの「🔤 訳す」（`translate.js`）を読み込んで使う。教科書のページでは選んだ文字の下に「🔤 訳す」を出さず（`<html data-no-tr-chip>`）、付箋・線のボタンの並びから `window.agriTranslate(文字)` で訳す

## 伝言板

- 書き込みは GitHub の Issues に保存する。ラベル「伝言板」が付いた、開いている Issue が [board.html](https://yusuke1090.github.io/smart-agri-news/board.html) に出る
- ページは開くたびに GitHub の API から読み込むので、書き込みはすぐに反映される（サイトの作り直しは不要）
- 書き込み方は2つ。**合言葉を知っていればアカウントなし**でページの中から書ける（下の「アカウントなしの書き込み」。中継の準備ができるまでは出ない）。GitHub のアカウントがあれば「＋ 書き込む」から専用のフォーム（`.github/ISSUE_TEMPLATE/board.yml`）でも書け、ラベルは自動で付く
- 編集は GitHub の Issue の画面で行う。GitHub で書いたものは本人が直せる。リポジトリの持ち主はすべての書き込みを直せる・消せる
- Issue を Close すると伝言板から消える。Issues は公開なので、書き込みは誰でも読める

### 🔎 関連する事業（伝言板の調べもの）

- 「やりたいこと」「アイデア」の書き込みには、似たことをしている会社・製品を調べた結果を付ける。`site/board-research.json`（キーは Issue 番号）を board.html が読み、書き込みの下に「🔎 関連する事業」として折りたたんで出す（まだのものは「まだ調べていません」と出る）
- 調べるのは、頼まれたときに Claude Code で行う（費用なし）。Claude Code に「伝言板を調べて」と頼むと、次の手順で行う
  1. `python3 tools/board_unresearched.py` で、まだ調べていない書き込みを出す（`--all` で全部）
  2. ウェブで調べ、**出典のページを開いて確かめられたことだけ**を書く（料金・年・数字は特に）
  3. `site/board-research.json` に足して push する（Actions がサイトを作り直す）
- JSON の形: `checked`（調べた日）、`summary`（全体のまとめ）、`companies`（`product`・`company`・`country`・`what`・`model`（売り方・料金）・`url`（出典））、`points`（わかったこと・差をつけられそうな所）

### アカウントなしの書き込み

ページのフォーム → **Google Apps Script の中継**（`tools/board-relay.gs`）→ GitHub の Issue・コメント、という流れ。中継が持ち主の GitHub のトークンで書くので、書く人はアカウントが要らない。トークンと合言葉は中継の中だけにあり、ページには出ない。

- フォームからの書き込みは持ち主のアカウントで作られ、本文の「### 書いた人」（コメントは最後の「書いた人: 〜」）に名前が入る。伝言板では「名前（フォーム）」と出る
- 荒らし対策: 合言葉（中継で確かめる）、人には見えない入力欄（ロボットよけ）、全体で 1時間に 20件まで、合言葉のまちがいが 1時間に 30回で止める。コメントは伝言板の開いている書き込みにだけ付けられる
- 名前と合言葉は、書いた人のブラウザに覚えておく（`localStorage` の `board-name`・`board-pass`）

準備（最初の1回。持ち主が行う）:

1. **GitHub でトークンを作る**: Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token
   - Repository access: **Only select repositories** → `smart-agri-news`
   - Permissions: **Issues** を **Read and write**（ほかは要らない）
   - 期限（Expiration）は 1年など。切れたら作り直して、下の `GITHUB_TOKEN` を差し替える
2. **Apps Script を作る**: [script.google.com](https://script.google.com) → 新しいプロジェクト → `tools/board-relay.gs` の中身を全部貼り付けて保存（名前は「伝言板の中継」など）
3. **秘密の値を入れる**: 左の ⚙「プロジェクトの設定」→ 一番下の「スクリプト プロパティ」に2つ足す
   - `GITHUB_TOKEN`: 1. のトークン
   - `PASSPHRASE`: 合言葉（書いてほしい人に伝える）
4. **つながるか確かめる**: エディタで関数 `testGitHub` を選んで「実行」→ 初回は Google アカウントの承認 → 実行ログに「つながりました」
5. **公開する**: 「デプロイ」→「新しいデプロイ」→ 種類 **ウェブアプリ** → 次のユーザーとして実行: **自分**、アクセスできるユーザー: **全員** → デプロイ → 出てきた URL（`https://script.google.com/macros/s/…/exec`）をコピー
6. **ページにつなぐ**: `site/board.html` の `var RELAY_URL = "";` に 5. の URL を入れて push（Claude Code に URL を伝えてもよい）

- 合言葉を変えるときは、スクリプト プロパティの `PASSPHRASE` を変えるだけ（デプロイし直さなくてよい）
- `board-relay.gs` を直したときは「デプロイを管理」→ 鉛筆 → バージョン「新しいバージョン」→ デプロイ（URL は変わらない）
- やめるときは「デプロイを管理」でアーカイブし、GitHub のトークンを削除する

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
site/cow.html                  牛の教科書への移動の案内（教科書は textbooks のリポジトリに移った）
site/board-research.json       伝言板の「🔎 関連する事業」（Issue 番号ごとの調べた結果）
tools/board-relay.gs           アカウントなしの書き込みの中継（Google Apps Script に貼って使う）
tools/board_unresearched.py    まだ「関連する事業」を調べていない伝言板の書き込みを出す
data/news.json                 集めた記事（過去30日分）
docs/                          公開されるサイト（build.py が作る。手で編集しない）
.github/workflows/update.yml   毎朝の自動更新
```

## 注意

- 載せているのは、タイトル・短い抜粋（または AI のまとめ）・リンクだけ。記事の著作権は各配信元にある
- AI のまとめは誤りを含むことがある（サイトにもその旨を書いている）
- カテゴリはキーワードによる自動分類なので、内容と合わないことがある
- ニュース元の RSS の URL が変わると、そのニュース元は取得できなくなる（サイトの一番下に取得状況が出る）
