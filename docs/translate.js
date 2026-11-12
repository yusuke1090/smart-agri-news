/* スマート農業News: 英単語や英文を訳す（右下の「🔤 訳す」と、文字を選んだときに出るボタン）
 *
 * - Chrome の翻訳機能（Translator API）が使えれば、それで訳す。PC の中で訳すので、文章は外に送られない
 * - 使えないとき（iPhone の Safari など）や準備中は、無料の翻訳サービス MyMemory で訳す
 * - 調べたものは、このブラウザに新しい順で 50 件まで残す（localStorage）
 * - 日本語を入れると、英語に訳す
 */
(function () {
  "use strict";
  var HISTORY_KEY = "agri-news-translate-history";
  var HISTORY_MAX = 50;
  var MM_BYTES = 450;          // MyMemory は 1回 500 バイトまで。余裕をみて文の区切りで分ける
  var MAX_CHARS = 3000;
  var JA_RE = /[぀-ヿ㐀-鿿ｦ-ﾟ]/;

  var css = [
    ".tr-fab { position: fixed; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); z-index: 20;",
    "  font: inherit; font-size: 14px; font-weight: 700; padding: 10px 18px; border-radius: 999px; cursor: pointer;",
    "  border: 0; background: var(--accent, #2e7d32); color: #fff; box-shadow: 0 4px 14px rgba(0,0,0,.28); }",
    ".tr-fab:hover { filter: brightness(1.08); }",
    ".tr-panel { position: fixed; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); z-index: 21;",
    "  width: min(420px, calc(100vw - 32px)); max-height: min(78vh, 680px); display: flex; flex-direction: column;",
    "  background: var(--panel, #fff); color: var(--text, #1e2a1c); border: 1px solid var(--border, #dde3d6);",
    "  border-radius: 14px; box-shadow: 0 10px 34px rgba(0,0,0,.32); font-size: 14px; line-height: 1.6; }",
    ".tr-head { display: flex; align-items: center; gap: 8px; padding: 10px 12px 8px 16px; border-bottom: 1px solid var(--border, #dde3d6); }",
    ".tr-head b { font-size: 15px; }",
    ".tr-grow { flex: 1; }",
    ".tr-panel button, .tr-chip { font: inherit; cursor: pointer; }",
    ".tr-btn { font-size: 13px; padding: 4px 12px; border-radius: 8px; border: 1px solid var(--border, #dde3d6);",
    "  background: var(--bg, #f5f7f2); color: var(--text, #1e2a1c); text-decoration: none; display: inline-block; }",
    ".tr-btn:hover { border-color: var(--accent, #2e7d32); }",
    ".tr-primary { background: var(--accent, #2e7d32); border-color: var(--accent, #2e7d32); color: #fff; font-weight: 700; padding: 5px 20px; }",
    ".tr-primary:disabled { opacity: .6; cursor: default; }",
    ".tr-x { border: 0; background: none; color: var(--muted, #66735f); font-size: 18px; width: 34px; height: 34px; border-radius: 50%; }",
    ".tr-x:hover { background: var(--bg, #f5f7f2); }",
    ".tr-body { overflow: auto; padding: 12px 16px 14px; }",
    ".tr-in { width: 100%; box-sizing: border-box; font: inherit; font-size: 15px; padding: 8px 10px; border-radius: 8px; resize: vertical;",
    "  border: 1px solid var(--border, #dde3d6); background: var(--bg, #f5f7f2); color: var(--text, #1e2a1c); min-height: 70px; }",
    ".tr-in:focus { outline: 2px solid var(--accent, #2e7d32); outline-offset: -1px; }",
    ".tr-row { display: flex; align-items: center; gap: 8px; margin-top: 8px; flex-wrap: wrap; }",
    ".tr-hint { font-size: 12px; color: var(--muted, #66735f); }",
    ".tr-out { margin-top: 12px; padding: 10px 12px; border-radius: 10px; background: var(--bg, #f5f7f2); border: 1px solid var(--border, #dde3d6); }",
    ".tr-dir { font-size: 11.5px; font-weight: 700; color: var(--accent, #2e7d32); letter-spacing: .03em; }",
    ".tr-result { margin-top: 2px; font-size: 16px; white-space: pre-wrap; overflow-wrap: anywhere; }",
    ".tr-result.err { font-size: 14px; color: var(--new, var(--warn, #d84315)); }",
    ".tr-tools { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }",
    ".tr-tools .tr-btn { font-size: 12.5px; padding: 3px 10px; background: var(--panel, #fff); }",
    ".tr-engine { margin-top: 6px; font-size: 11.5px; color: var(--muted, #66735f); }",
    ".tr-hist-head { display: flex; align-items: baseline; gap: 8px; margin: 16px 0 4px; }",
    ".tr-hist-head b { font-size: 13.5px; }",
    ".tr-count { font-size: 12px; color: var(--muted, #66735f); }",
    ".tr-hist { list-style: none; margin: 0; padding: 0; }",
    ".tr-hist li { display: flex; align-items: stretch; border-top: 1px solid var(--border, #dde3d6); }",
    ".tr-hist .tr-h-go { flex: 1; min-width: 0; text-align: left; border: 0; background: none; color: inherit; padding: 6px 4px; border-radius: 6px; }",
    ".tr-hist .tr-h-go:hover { background: var(--bg, #f5f7f2); }",
    ".tr-h-src, .tr-h-dst { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; overflow-wrap: anywhere; }",
    ".tr-h-src { font-size: 14px; font-weight: 600; }",
    ".tr-h-dst { font-size: 13px; color: var(--muted, #66735f); }",
    ".tr-hist .tr-h-del { border: 0; background: none; color: var(--muted, #66735f); padding: 0 10px; font-size: 13px; }",
    ".tr-hist .tr-h-del:hover { color: var(--new, var(--warn, #d84315)); }",
    ".tr-empty { color: var(--muted, #66735f); font-size: 13px; padding: 6px 2px; }",
    ".tr-note { margin: 12px 0 0; font-size: 11.5px; color: var(--muted, #66735f); line-height: 1.6; }",
    ".tr-chip { position: fixed; z-index: 22; font-size: 13px; font-weight: 700; padding: 5px 12px; border-radius: 999px;",
    "  border: 0; background: var(--accent, #2e7d32); color: #fff; box-shadow: 0 3px 10px rgba(0,0,0,.3); }",
    ".tr-panel[hidden], .tr-chip[hidden], .tr-out[hidden], .tr-fab[hidden], .tr-tools [hidden] { display: none !important; }",
    "@media (max-width: 600px) {",
    "  .tr-panel { left: 0; right: 0; bottom: 0; width: auto; max-height: 85vh; border-radius: 16px 16px 0 0;",
    "    padding-bottom: env(safe-area-inset-bottom, 0px); }",
    "  .tr-in { font-size: 16px; }",
    "  .tr-hint { display: none; }",
    "}"
  ].join("\n");

  var html =
    '<button type="button" class="tr-fab" id="tr-fab" aria-haspopup="dialog" aria-controls="tr-panel" title="英単語や英文を日本語に訳す">🔤 訳す</button>' +
    '<section class="tr-panel" id="tr-panel" role="dialog" aria-label="英語を訳す" hidden>' +
    '  <div class="tr-head"><b>🔤 英語を訳す</b><span class="tr-grow"></span>' +
    '    <button type="button" class="tr-x" id="tr-close" aria-label="閉じる" title="閉じる（Esc）">✕</button></div>' +
    '  <div class="tr-body">' +
    '    <textarea class="tr-in" id="tr-in" rows="3" maxlength="' + MAX_CHARS + '" aria-label="訳したい英単語や英文"' +
    '      placeholder="英単語や英文を入れる（日本語なら英語に訳します）"></textarea>' +
    '    <div class="tr-row"><button type="button" class="tr-btn tr-primary" id="tr-go">訳す</button>' +
    '      <span class="tr-hint">Ctrl + Enter でも訳せます</span><span class="tr-grow"></span>' +
    '      <button type="button" class="tr-btn" id="tr-clear">クリア</button></div>' +
    '    <div class="tr-out" id="tr-out" hidden aria-live="polite">' +
    '      <div class="tr-dir" id="tr-dir"></div>' +
    '      <div class="tr-result" id="tr-result"></div>' +
    '      <div class="tr-tools">' +
    '        <button type="button" class="tr-btn" id="tr-speak">🔊 英語を聞く</button>' +
    '        <button type="button" class="tr-btn" id="tr-copy">コピー</button>' +
    '        <a class="tr-btn" id="tr-dict" target="_blank" rel="noopener">Weblio 辞書</a>' +
    '        <a class="tr-btn" id="tr-google" target="_blank" rel="noopener">Google 翻訳</a>' +
    '      </div>' +
    '      <div class="tr-engine" id="tr-engine"></div>' +
    '    </div>' +
    '    <div class="tr-hist-head"><b>履歴</b><span class="tr-count" id="tr-count"></span><span class="tr-grow"></span>' +
    '      <button type="button" class="tr-btn" id="tr-hist-clear">すべて消す</button></div>' +
    '    <ul class="tr-hist" id="tr-hist"></ul>' +
    '    <p class="tr-note">ページの英文を選ぶと出る「🔤 訳す」からも訳せます。機械翻訳なので、まちがえることがあります。' +
    '      Chrome では Chrome の翻訳機能（PC の中で訳す）を使い、使えないときは無料の翻訳サービス MyMemory に文章を送って訳します' +
    '      （MyMemory は1日に訳せる量に上限があります）。履歴はこのブラウザだけに残ります。</p>' +
    '  </div>' +
    '</section>' +
    '<button type="button" class="tr-chip" id="tr-chip" hidden>🔤 訳す</button>';

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);
  var box = document.createElement("div");
  box.innerHTML = html;
  while (box.firstChild) document.body.appendChild(box.firstChild);

  function $(id) { return document.getElementById(id); }
  var fab = $("tr-fab"), panel = $("tr-panel"), input = $("tr-in"), goBtn = $("tr-go"), out = $("tr-out");
  var resultEl = $("tr-result"), dirEl = $("tr-dir"), engineEl = $("tr-engine"), chip = $("tr-chip");
  var current = null;     // 表示している結果
  var busy = false;

  // ---------- 履歴 ----------
  function loadHistory() {
    try {
      var h = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
      return Array.isArray(h) ? h : [];
    } catch (e) { return []; }
  }
  function saveHistory(h) {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(h.slice(0, HISTORY_MAX))); } catch (e) {}
  }
  function addHistory(entry) {
    var h = loadHistory().filter(function (x) { return !(x.src === entry.src && x.from === entry.from); });
    h.unshift(entry);
    saveHistory(h);
    renderHistory();
  }
  function fmtTime(ms) {
    var d = new Date(ms);
    return (d.getMonth() + 1) + "/" + d.getDate() + " " + d.getHours() + ":" + ("0" + d.getMinutes()).slice(-2);
  }
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function renderHistory() {
    var h = loadHistory();
    $("tr-count").textContent = h.length ? h.length + " / " + HISTORY_MAX + " 件" : "";
    $("tr-hist-clear").hidden = !h.length;
    $("tr-hist").innerHTML = h.length ? h.map(function (x, i) {
      return '<li><button type="button" class="tr-h-go" data-i="' + i + '" title="' + esc(fmtTime(x.at)) + '">' +
        '<span class="tr-h-src">' + esc(x.src) + '</span><span class="tr-h-dst">' + esc(x.dst) + '</span></button>' +
        '<button type="button" class="tr-h-del" data-del="' + i + '" aria-label="この履歴を消す" title="消す">✕</button></li>';
    }).join("") : '<li class="tr-empty">まだありません。訳したものが、新しい順に ' + HISTORY_MAX + ' 件まで残ります</li>';
  }
  $("tr-hist").addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    var h = loadHistory();
    if (b.dataset.del !== undefined) {
      h.splice(+b.dataset.del, 1);
      saveHistory(h);
      renderHistory();
      return;
    }
    var x = h[+b.dataset.i];
    if (!x) return;
    input.value = x.src;
    show(x, "履歴から表示（" + fmtTime(x.at) + " に " + engineName(x.engine) + "で訳したもの）");
  });
  $("tr-hist-clear").addEventListener("click", function () {
    if (!confirm("履歴をすべて消しますか？")) return;
    saveHistory([]);
    renderHistory();
  });

  // ---------- 訳す ----------
  function direction(text) { return JA_RE.test(text) ? { from: "ja", to: "en" } : { from: "en", to: "ja" }; }
  function engineName(e) { return e === "chrome" ? "Chrome の翻訳機能" : "MyMemory"; }

  // Chrome の翻訳機能。すぐ使えるときだけ返す。準備（ダウンロード）が要るときは、裏で始めて null を返す
  var chromeTr = {}, chromeWait = {}, chromeFailed = {}, chromeProgress = {};
  function chromeTranslator(from, to) {
    var key = from + "-" + to;
    var T = window.Translator;
    if (!T || typeof T.availability !== "function" || chromeFailed[key]) return Promise.resolve(null);
    if (chromeTr[key]) return Promise.resolve(chromeTr[key]);
    if (chromeWait[key]) return Promise.resolve(null);
    return Promise.resolve().then(function () {
      return T.availability({ sourceLanguage: from, targetLanguage: to });
    }).then(function (a) {
      if (a === "unavailable") { chromeFailed[key] = true; return null; }
      var p = T.create({
        sourceLanguage: from, targetLanguage: to,
        monitor: function (m) {
          m.addEventListener("downloadprogress", function (ev) { chromeProgress[key] = ev.loaded; });
        }
      }).then(function (t) { chromeTr[key] = t; delete chromeWait[key]; return t; },
              function () { chromeFailed[key] = true; delete chromeWait[key]; return null; });
      if (a === "available") return p;
      chromeWait[key] = p;
      return null;
    }, function () { chromeFailed[key] = true; return null; });
  }

  function utf8Len(s) { return new TextEncoder().encode(s).length; }
  // MyMemory に送る大きさに分ける（文の区切り → 単語の区切り → 文字）
  function chunks(line) {
    var parts = line.match(/[^.!?。！？]+[.!?。！？]*\s*/g) || [line];
    var res = [], cur = "";
    parts.forEach(function (p) {
      if (cur && utf8Len(cur + p) > MM_BYTES) { res.push(cur); cur = ""; }
      while (utf8Len(p) > MM_BYTES) {
        var n = p.length;
        while (n > 1 && utf8Len(p.slice(0, n)) > MM_BYTES) n = Math.floor(n * 0.9);
        var sp = p.lastIndexOf(" ", n);
        if (sp > n * 0.5) n = sp + 1;
        res.push(p.slice(0, n));
        p = p.slice(n);
      }
      cur += p;
    });
    if (cur.trim()) res.push(cur);
    return res;
  }
  function decodeEntities(s) {
    var t = document.createElement("textarea");
    t.innerHTML = s;
    return t.value;
  }
  function myMemoryOne(q, from, to) {
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 15000) : 0;
    var url = "https://api.mymemory.translated.net/get?q=" + encodeURIComponent(q.trim()) +
      "&langpair=" + from + "%7C" + to;
    return fetch(url, ctrl ? { signal: ctrl.signal } : {}).then(function (r) {
      clearTimeout(timer);
      return r.json().catch(function () { throw new Error("翻訳サービスの返事が読めません（" + r.status + "）"); });
    }, function () {
      clearTimeout(timer);
      throw new Error("翻訳サービスにつながりません。ネットの接続を確かめてください");
    }).then(function (d) {
      var status = +d.responseStatus;
      if (status === 429 || d.quotaFinished) throw new Error("今日 MyMemory で訳せる量を使い切りました。下の「Google 翻訳」から訳せます");
      if (status !== 200 || !d.responseData) throw new Error("訳せませんでした（" + (d.responseDetails || status) + "）");
      return decodeEntities(d.responseData.translatedText || "");
    });
  }
  function myMemory(text, from, to) {
    var lines = text.split(/\n/);
    var outLines = [];
    var chain = Promise.resolve();
    lines.forEach(function (line, i) {
      chain = chain.then(function () {
        if (!line.trim()) { outLines[i] = ""; return; }
        var parts = chunks(line), done = [];
        var c = Promise.resolve();
        parts.forEach(function (p, k) {
          c = c.then(function () { return myMemoryOne(p, from, to).then(function (t) { done[k] = t.trim(); }); });
        });
        return c.then(function () { outLines[i] = done.join(to === "ja" ? "" : " "); });
      });
    });
    return chain.then(function () { return outLines.join("\n").trim(); });
  }

  function translate(text) {
    text = (text || "").trim();
    if (!text || busy) return;
    if (text.length > MAX_CHARS) text = text.slice(0, MAX_CHARS);
    var d = direction(text);
    busy = true;
    goBtn.disabled = true;
    goBtn.textContent = "訳しています…";
    Promise.resolve().then(function () { return chromeTranslator(d.from, d.to); }).then(function (t) {
      if (t) return t.translate(text).then(function (r) { return { dst: r, engine: "chrome" }; },
                                          function () { return null; });
      return null;
    }).then(function (r) {
      return r || myMemory(text, d.from, d.to).then(function (dst) { return { dst: dst, engine: "mymemory" }; });
    }).then(function (r) {
      var entry = { src: text, dst: r.dst, from: d.from, to: d.to, engine: r.engine, at: Date.now() };
      addHistory(entry);
      var note = "";
      if (r.engine === "chrome") note = "Chrome の翻訳機能で訳しました（PC の中で訳すので、文章は外に送られません）";
      else {
        note = "MyMemory（無料の翻訳サービス）で訳しました";
        if (chromeWait[d.from + "-" + d.to]) {
          var pr = chromeProgress[d.from + "-" + d.to];
          note += "。Chrome の翻訳機能を準備しています" + (pr ? "（" + Math.round(pr * 100) + "%）" : "") +
            "。準備ができたら、次からは PC の中で訳します";
        }
      }
      show(entry, note);
    }, function (err) {
      showError(text, d, err.message || String(err));
    }).then(function () {
      busy = false;
      goBtn.disabled = false;
      goBtn.textContent = "訳す";
    });
  }

  function englishSide(x) { return x.from === "en" ? x.src : x.dst; }
  function setLinks(x) {
    var src = x.src;
    var short = x.from === "en" ? src.split(/\s+/).length <= 4 && src.length <= 60 : src.length <= 15;
    var dict = $("tr-dict");
    dict.hidden = !short;
    dict.href = "https://ejje.weblio.jp/content/" + encodeURIComponent(src);
    $("tr-google").href = "https://translate.google.com/?sl=" + x.from + "&tl=" + x.to + "&text=" +
      encodeURIComponent(src) + "&op=translate";
  }
  function show(x, note) {
    current = x;
    out.hidden = false;
    dirEl.textContent = x.from === "en" ? "英語 → 日本語" : "日本語 → 英語";
    resultEl.className = "tr-result";
    resultEl.lang = x.to;
    resultEl.textContent = x.dst || "（訳が空でした）";
    engineEl.textContent = note || "";
    $("tr-speak").hidden = !("speechSynthesis" in window) || !englishSide(x);
    $("tr-copy").hidden = false;
    setLinks(x);
  }
  function showError(text, d, msg) {
    current = null;
    out.hidden = false;
    dirEl.textContent = d.from === "en" ? "英語 → 日本語" : "日本語 → 英語";
    resultEl.className = "tr-result err";
    resultEl.textContent = msg;
    engineEl.textContent = "";
    $("tr-speak").hidden = true;
    $("tr-copy").hidden = true;
    setLinks({ src: text, from: d.from, to: d.to });
  }

  $("tr-speak").addEventListener("click", function () {
    if (!current) return;
    var s = window.speechSynthesis;
    if (s.speaking) { s.cancel(); return; }
    var u = new SpeechSynthesisUtterance(englishSide(current));
    u.lang = "en-US";
    u.rate = 0.9;
    s.speak(u);
  });
  $("tr-copy").addEventListener("click", function () {
    if (!current) return;
    var b = this;
    var done = function () { b.textContent = "コピーしました"; setTimeout(function () { b.textContent = "コピー"; }, 1500); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(current.dst).then(done, function () {});
  });

  // ---------- 開く・閉じる ----------
  function openPanel() {
    panel.hidden = false;
    fab.hidden = true;
    renderHistory();
  }
  function closePanel() {
    panel.hidden = true;
    fab.hidden = false;
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    fab.focus();
  }
  fab.addEventListener("click", function () { openPanel(); input.focus(); });
  $("tr-close").addEventListener("click", closePanel);
  goBtn.addEventListener("click", function () { translate(input.value); });
  $("tr-clear").addEventListener("click", function () {
    input.value = "";
    out.hidden = true;
    current = null;
    input.focus();
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); translate(input.value); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) closePanel();
  });

  // ---------- ページの文字を選んだら「🔤 訳す」を出す ----------
  function selectedText() {
    var sel = window.getSelection();
    if (!sel || !sel.rangeCount || sel.isCollapsed) return null;
    var a = document.activeElement;
    if (a && (a.tagName === "INPUT" || a.tagName === "TEXTAREA")) return null;
    if (panel.contains(sel.anchorNode) || panel.contains(sel.focusNode)) return null;
    var text = sel.toString().trim();
    if (!text || text.length > MAX_CHARS) return null;
    return { text: text, rect: sel.getRangeAt(0).getBoundingClientRect() };
  }
  function placeChip() {
    var s = selectedText();
    if (!s || (!s.rect.width && !s.rect.height)) { chip.hidden = true; return; }
    chip.hidden = false;
    var w = chip.offsetWidth, h = chip.offsetHeight;
    var left = Math.max(8, Math.min(s.rect.left + s.rect.width / 2 - w / 2, window.innerWidth - w - 8));
    var top = s.rect.bottom + 12;                          // 下に出す（スマホは上にコピーなどのメニューが出るため）
    if (top + h > window.innerHeight - 8) top = Math.max(8, s.rect.top - h - 12);
    chip.style.left = left + "px";
    chip.style.top = top + "px";
  }
  var selTimer = 0;
  document.addEventListener("selectionchange", function () {
    clearTimeout(selTimer);
    selTimer = setTimeout(placeChip, 250);
  });
  window.addEventListener("scroll", function () { if (!chip.hidden) placeChip(); }, { passive: true });
  chip.addEventListener("mousedown", function (e) { e.preventDefault(); });   // 選んだ文字を消さない
  chip.addEventListener("click", function () {
    var s = selectedText();
    chip.hidden = true;
    if (!s) return;
    openPanel();
    input.value = s.text;
    translate(s.text);
  });

  renderHistory();
})();
