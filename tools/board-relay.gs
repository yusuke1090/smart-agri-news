/**
 * スマート農業News の伝言板: アカウントなしの書き込みを受け取り、GitHub の Issue（またはコメント）にする中継
 *
 * Google Apps Script のウェブアプリとして動かす（作り方は README の「アカウントなしの書き込み」）。
 * 伝言板のページ（board.html）のフォームが、ここに JSON を POST する。
 *
 * スクリプト プロパティ（プロジェクトの設定 → スクリプト プロパティ）に入れるもの:
 *   GITHUB_TOKEN  このリポジトリの Issues だけを読み書きできる fine-grained token
 *   PASSPHRASE    書き込みの合言葉
 * どちらもページには出ない（このプログラムの中だけで使う）。
 */

var REPO = "yusuke1090/smart-agri-news";
var LABEL = "伝言板";
var KINDS = ["やりたいこと", "アイデア", "質問・相談", "その他"];
var MAX = { name: 30, title: 100, content: 5000, comment: 3000 };
var MAX_POSTS_PER_HOUR = 20;      // 書き込み全体で、1時間にこれだけ
var MAX_WRONG_PER_HOUR = 30;      // 合言葉のまちがいが、1時間にこれだけ続いたら止める
var FORM_NOTE = "（伝言板のフォームから）";

function doPost(e) {
  var res;
  try {
    res = handle(JSON.parse(e.postData.contents));
  } catch (err) {
    console.error(err);
    res = { ok: false, error: "送れませんでした。時間をおいて、もう一度お試しください" };
  }
  return json(res);
}

// ブラウザで URL を開いたときに、動いているかがわかるように
function doGet() {
  return json({ ok: true, service: "smart-agri-news board relay" });
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function handle(d) {
  if (!d || typeof d !== "object") return { ok: false, error: "送信内容を読めませんでした" };
  if (d.website) return { ok: true };   // 人には見えない入力欄に何か入っている → ロボット。成功したふりをして捨てる

  var props = PropertiesService.getScriptProperties();
  var cache = CacheService.getScriptCache();
  var token = props.getProperty("GITHUB_TOKEN");
  var pass = norm(props.getProperty("PASSPHRASE"));
  if (!token || !pass) return { ok: false, error: "書き込みの準備ができていません（持ち主の設定待ち）" };

  var wrong = Number(cache.get("wrong") || 0);
  if (wrong >= MAX_WRONG_PER_HOUR) return { ok: false, error: "しばらく書き込めません。時間をおいてください" };
  if (norm(d.passphrase) !== pass) {
    cache.put("wrong", String(wrong + 1), 3600);
    return { ok: false, error: "合言葉がちがいます" };
  }
  var posts = Number(cache.get("posts") || 0);
  if (posts >= MAX_POSTS_PER_HOUR) return { ok: false, error: "書き込みが多すぎます。1時間ほどおいてください" };

  var name = oneLine(d.name, MAX.name) || "名前なし";
  var res = d.action === "comment" ? comment(token, d, name) : issue(token, d, name);
  if (res.ok) cache.put("posts", String(posts + 1), 3600);
  return res;
}

// 新しい書き込み（Issue）。GitHub の書き込みフォームと同じ形の本文にする
function issue(token, d, name) {
  var kind = KINDS.indexOf(d.kind) >= 0 ? d.kind : "その他";
  var title = oneLine(d.title, MAX.title);
  var content = text(d.content, MAX.content);
  if (!title) return { ok: false, error: "題名を書いてください" };
  if (!content) return { ok: false, error: "内容を書いてください" };
  var body = "### 種類\n\n" + kind + "\n\n### 内容\n\n" + content + "\n\n### 書いた人\n\n" + name + FORM_NOTE + "\n";
  var r = gh(token, "post", "/issues", { title: title, body: body, labels: [LABEL] });
  if (r.code !== 201) return failed(r);
  return { ok: true, number: r.data.number, url: r.data.html_url };
}

// コメント。伝言板の、開いている書き込みにだけ付けられる
function comment(token, d, name) {
  var num = parseInt(d.number, 10);
  var content = text(d.content, MAX.comment);
  if (!(num > 0)) return { ok: false, error: "どの書き込みへのコメントかわかりません" };
  if (!content) return { ok: false, error: "コメントを書いてください" };
  var t = gh(token, "get", "/issues/" + num);
  var isBoard = t.code === 200 && t.data.state === "open" && !t.data.pull_request
    && (t.data.labels || []).some(function (l) { return l.name === LABEL; });
  if (!isBoard) return { ok: false, error: "その書き込みにはコメントできません" };
  var body = content + "\n\n---\n書いた人: " + name + FORM_NOTE + "\n";
  var r = gh(token, "post", "/issues/" + num + "/comments", { body: body });
  if (r.code !== 201) return failed(r);
  return { ok: true, url: r.data.html_url };
}

function gh(token, method, path, payload) {
  var opt = {
    method: method,
    muteHttpExceptions: true,
    headers: {
      Authorization: "Bearer " + token,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    }
  };
  if (payload) { opt.contentType = "application/json"; opt.payload = JSON.stringify(payload); }
  var r = UrlFetchApp.fetch("https://api.github.com/repos/" + REPO + path, opt);
  var data = null;
  try { data = JSON.parse(r.getContentText()); } catch (e) { data = null; }
  return { code: r.getResponseCode(), data: data };
}

function failed(r) {
  console.error("GitHub " + r.code + " " + JSON.stringify(r.data));
  if (r.code === 401 || r.code === 403) return { ok: false, error: "書き込めませんでした（持ち主の GitHub の設定を確かめる必要があります）" };
  return { ok: false, error: "書き込めませんでした（GitHub " + r.code + "）。時間をおいて、もう一度お試しください" };
}

// 全角・半角のちがいや前後の空白で合言葉がずれないように
function norm(s) { return String(s == null ? "" : s).normalize("NFKC").trim(); }
function oneLine(s, max) { return String(s == null ? "" : s).replace(/[\r\n\t]+/g, " ").trim().slice(0, max); }
function text(s, max) { return String(s == null ? "" : s).replace(/\r\n?/g, "\n").trim().slice(0, max); }

// Apps Script のエディタで実行して、GitHub につながるかを確かめる（Issue は作らない）
function testGitHub() {
  var token = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  var r = gh(token, "get", "/issues?labels=" + encodeURIComponent(LABEL) + "&per_page=1");
  console.log("GitHub の応答: " + r.code + (r.code === 200 ? "（つながりました）" : " " + JSON.stringify(r.data)));
}
