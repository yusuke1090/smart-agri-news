/* スマート農業News: 英単語・英文を訳す（右下の「🔤 訳す」と、文字を選んだときに出るボタン）
 *
 * 単語: 意味は英和辞書 EJDict（パブリックドメイン。dict/a.json〜z.json）、
 *       例文は Tatoeba（人が訳した英文と和文。CC BY 2.0 FR）。なければページの記事の英文を機械翻訳する
 * 文章: Chrome の翻訳機能（PC の中で訳す）、使えないときは無料の MyMemory で訳す
 * 履歴: このブラウザに新しい順で 50 件（localStorage）
 */
(function () {
  "use strict";
  var HISTORY_KEY = "agri-news-translate-history";
  var HISTORY_MAX = 50;
  var MM_BYTES = 450;          // MyMemory は 1回 500 バイトまで
  var MAX_CHARS = 3000;
  var SENSES_SHOWN = 5;
  var JA_RE = /[぀-ヿ㐀-鿿ｦ-ﾟ]/;
  var WORD_RE = /^[A-Za-z][A-Za-z'\-]*$/;
  var DICT_URL = (document.currentScript && document.currentScript.src || location.href).replace(/[^/]*$/, "") + "dict/";

  var css = [
    ".tr-fab { position: fixed; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); z-index: 20;",
    "  font: inherit; font-size: 14px; font-weight: 700; padding: 10px 18px; border-radius: 999px; cursor: pointer;",
    "  border: 0; background: var(--accent, #2e7d32); color: #fff; box-shadow: 0 4px 14px rgba(0,0,0,.28); }",
    ".tr-panel { position: fixed; right: 16px; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); z-index: 21;",
    "  width: min(420px, calc(100vw - 32px)); max-height: min(80vh, 700px); display: flex; flex-direction: column;",
    "  background: var(--panel, #fff); color: var(--text, #1e2a1c); border: 1px solid var(--border, #dde3d6);",
    "  border-radius: 14px; box-shadow: 0 10px 34px rgba(0,0,0,.32); font-size: 14px; line-height: 1.6; }",
    ".tr-panel button, .tr-chip { font: inherit; cursor: pointer; }",
    ".tr-top { display: flex; align-items: flex-start; gap: 6px; padding: 10px 8px 10px 12px; border-bottom: 1px solid var(--border, #dde3d6); }",
    ".tr-in { flex: 1; min-width: 0; font: inherit; font-size: 15px; padding: 6px 10px; border-radius: 8px; resize: none;",
    "  border: 1px solid var(--border, #dde3d6); background: var(--bg, #f5f7f2); color: var(--text, #1e2a1c);",
    "  height: 36px; max-height: 120px; overflow-y: auto; }",
    ".tr-in:focus { outline: 2px solid var(--accent, #2e7d32); outline-offset: -1px; }",
    ".tr-go { font-size: 14px; font-weight: 700; padding: 0 16px; height: 36px; border-radius: 8px; border: 0;",
    "  background: var(--accent, #2e7d32); color: #fff; flex: none; }",
    ".tr-go:disabled { opacity: .6; cursor: default; }",
    ".tr-x { flex: none; border: 0; background: none; color: var(--muted, #66735f); font-size: 18px; width: 36px; height: 36px; border-radius: 50%; }",
    ".tr-x:hover { background: var(--bg, #f5f7f2); }",
    ".tr-body { overflow: auto; padding: 4px 16px 12px; }",
    ".tr-out { padding: 10px 0 12px; border-bottom: 1px solid var(--border, #dde3d6); }",
    ".tr-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }",
    ".tr-word { font-size: 22px; font-weight: 700; font-family: Georgia, 'Times New Roman', serif; }",
    ".tr-from { color: var(--muted, #66735f); font-size: 14px; }",
    ".tr-ipa { color: var(--muted, #66735f); font-size: 13.5px; }",
    ".tr-say { border: 0; background: none; padding: 0 2px; font-size: 15px; line-height: 1; opacity: .75; }",
    ".tr-say:hover { opacity: 1; }",
    ".tr-senses { margin: 6px 0 0; padding-left: 1.4em; }",
    ".tr-senses li { margin: 1px 0; }",
    ".tr-senses b { color: var(--text, #1e2a1c); }",
    ".tr-more { border: 0; background: none; padding: 0; margin: 2px 0 0 1.4em; color: var(--muted, #66735f); font-size: 12.5px; text-decoration: underline; }",
    ".tr-label { display: flex; justify-content: space-between; margin: 12px 0 2px; font-size: 12px; font-weight: 700; color: var(--accent, #2e7d32); }",
    ".tr-label a { font-weight: normal; color: var(--muted, #66735f); text-decoration: none; }",
    ".tr-ex { margin: 6px 0 0; }",
    ".tr-ex-en { font-family: Georgia, 'Times New Roman', serif; font-size: 14.5px; }",
    ".tr-ex-en b { color: var(--accent, #2e7d32); }",
    ".tr-ex-ja { font-size: 13px; color: var(--muted, #66735f); }",
    ".tr-text { font-size: 16px; white-space: pre-wrap; overflow-wrap: anywhere; }",
    ".tr-err { color: var(--new, var(--warn, #d84315)); }",
    ".tr-wait { color: var(--muted, #66735f); }",
    ".tr-hist-head { display: flex; justify-content: space-between; align-items: baseline; margin: 12px 0 2px; font-size: 12px; color: var(--muted, #66735f); }",
    ".tr-hist-head button { border: 0; background: none; padding: 0; color: var(--muted, #66735f); font-size: 12px; text-decoration: underline; }",
    ".tr-hist { list-style: none; margin: 0; padding: 0; }",
    ".tr-hist li { display: flex; align-items: center; border-top: 1px solid var(--border, #dde3d6); }",
    ".tr-h-go { flex: 1; min-width: 0; display: flex; gap: 10px; align-items: baseline; text-align: left; border: 0; background: none;",
    "  color: inherit; padding: 6px 4px; border-radius: 6px; }",
    ".tr-h-go:hover { background: var(--bg, #f5f7f2); }",
    ".tr-h-src { flex: none; max-width: 55%; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
    ".tr-h-dst { flex: 1; min-width: 0; font-size: 13px; color: var(--muted, #66735f); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }",
    ".tr-h-del { flex: none; border: 0; background: none; color: var(--muted, #66735f); padding: 4px 8px; font-size: 12px; }",
    ".tr-chip { position: fixed; z-index: 22; font-size: 13px; font-weight: 700; padding: 5px 12px; border-radius: 999px;",
    "  border: 0; background: var(--accent, #2e7d32); color: #fff; box-shadow: 0 3px 10px rgba(0,0,0,.3); }",
    ".tr-panel[hidden], .tr-chip[hidden], .tr-fab[hidden], .tr-panel [hidden] { display: none !important; }",
    "@media (max-width: 600px) {",
    "  .tr-panel { left: 0; right: 0; bottom: 0; width: auto; max-height: 85vh; border-radius: 16px 16px 0 0;",
    "    padding-bottom: env(safe-area-inset-bottom, 0px); }",
    "  .tr-in { font-size: 16px; }",
    "}"
  ].join("\n");

  var html =
    '<button type="button" class="tr-fab" id="tr-fab" aria-haspopup="dialog" aria-controls="tr-panel">🔤 訳す</button>' +
    '<section class="tr-panel" id="tr-panel" role="dialog" aria-label="訳す" hidden>' +
    '  <div class="tr-top">' +
    '    <textarea class="tr-in" id="tr-in" rows="1" maxlength="' + MAX_CHARS + '" placeholder="英単語・英文" aria-label="訳す言葉"></textarea>' +
    '    <button type="button" class="tr-go" id="tr-go">訳す</button>' +
    '    <button type="button" class="tr-x" id="tr-close" aria-label="閉じる">✕</button>' +
    '  </div>' +
    '  <div class="tr-body">' +
    '    <div class="tr-out" id="tr-out" hidden aria-live="polite"></div>' +
    '    <div class="tr-hist-head" id="tr-hist-head"><span>履歴</span><button type="button" id="tr-hist-clear">すべて消す</button></div>' +
    '    <ul class="tr-hist" id="tr-hist"></ul>' +
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
  var fab = $("tr-fab"), panel = $("tr-panel"), input = $("tr-in"), goBtn = $("tr-go"), out = $("tr-out"), chip = $("tr-chip");
  var busy = false, current = null;

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function speak(text) {
    var s = window.speechSynthesis;
    if (!s || !text) return;
    s.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    u.rate = 0.9;
    s.speak(u);
  }
  var canSpeak = "speechSynthesis" in window;
  function sayBtn(text) {
    return canSpeak ? '<button type="button" class="tr-say" data-say="' + esc(text) + '" aria-label="読み上げる">🔊</button>' : "";
  }

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
    var key = (entry.head || entry.src).toLowerCase();
    var h = loadHistory().filter(function (x) { return (x.head || x.src).toLowerCase() !== key; });
    h.unshift(entry);
    saveHistory(h);
    renderHistory();
  }
  function plain(s) { return String(s || "").replace(/[『』]/g, ""); }
  function renderHistory() {
    var h = loadHistory();
    $("tr-hist-head").hidden = !h.length;
    $("tr-hist").innerHTML = h.map(function (x, i) {
      var dst = x.kind === "word" ? (x.senses || []).slice(0, 3).map(plain).join(" / ") || x.mt || "" : x.dst;
      return '<li><button type="button" class="tr-h-go" data-i="' + i + '"><span class="tr-h-src">' + esc(x.head || x.src) +
        '</span><span class="tr-h-dst">' + esc(dst) + '</span></button>' +
        '<button type="button" class="tr-h-del" data-del="' + i + '" aria-label="消す">✕</button></li>';
    }).join("");
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
    fitInput();
    x.kind === "word" ? showWord(x) : showText(x);
    panel.querySelector(".tr-body").scrollTop = 0;
  });
  $("tr-hist-clear").addEventListener("click", function () {
    if (!confirm("履歴をすべて消しますか？")) return;
    saveHistory([]);
    renderHistory();
  });

  // ---------- 辞書（EJDict） ----------
  var dictCache = {};
  function dictPart(letter) {
    if (!dictCache[letter]) {
      dictCache[letter] = fetch(DICT_URL + letter + ".json").then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      }).catch(function (e) { delete dictCache[letter]; throw e; });
    }
    return dictCache[letter];
  }
  function lookup(word) {
    var w = word.toLowerCase();
    if (!/^[a-z]/.test(w)) return Promise.resolve(null);
    return dictPart(w[0]).then(function (d) { return d[w] || null; });
  }
  // 活用した形（aimed, studies, running …）から、元の形の候補を作る
  function baseForms(w) {
    var c = [];
    function add(x) { if (x && x.length > 1 && x !== w && c.indexOf(x) < 0) c.push(x); }
    var m;
    if (/ies$/.test(w)) add(w.slice(0, -3) + "y");
    if (/ied$/.test(w)) add(w.slice(0, -3) + "y");
    if ((m = w.match(/^(.*?)([^aeiou])\2(ed|ing|er|est)$/))) add(m[1] + m[2]);
    if (/ed$/.test(w)) { add(w.slice(0, -2)); add(w.slice(0, -1)); }
    if (/ing$/.test(w)) { add(w.slice(0, -3)); add(w.slice(0, -3) + "e"); }
    if (/(s|x|z|ch|sh)es$/.test(w)) add(w.slice(0, -2));
    if (/s$/.test(w) && !/ss$/.test(w)) add(w.slice(0, -1));
    if (/ier$/.test(w)) add(w.slice(0, -3) + "y");
    if (/iest$/.test(w)) add(w.slice(0, -4) + "y");
    if (/er$/.test(w)) { add(w.slice(0, -2)); add(w.slice(0, -1)); }
    if (/est$/.test(w)) { add(w.slice(0, -3)); add(w.slice(0, -2)); }
    if (/ily$/.test(w)) add(w.slice(0, -3) + "y");
    if (/ly$/.test(w)) add(w.slice(0, -2));
    return c;
  }
  var IRREGULAR_RE = /^([a-z]+)の(過去分詞|過去|現在分詞|複数形?|比較級|最上級)/;
  // 単語の意味を探す。見出し語（元の形）と、意味の一覧を返す
  function findWord(word) {
    var w = word.toLowerCase();
    return lookup(w).then(function (m) {
      var irr = m && m.match(IRREGULAR_RE);
      if (irr) {                                         // went → go の過去
        return lookup(irr[1]).then(function (m2) {
          return m2 ? { head: irr[1], form: irr[2], senses: splitSenses(m2) } : { head: w, senses: splitSenses(m) };
        });
      }
      if (m) return { head: w, senses: splitSenses(m) };
      var cands = baseForms(w), i = 0;
      function next() {
        if (i >= cands.length) return null;
        var c = cands[i++];
        return lookup(c).then(function (m2) { return m2 ? { head: c, senses: splitSenses(m2) } : next(); });
      }
      return next();
    });
  }
  // 画面に出す意味は短くする: 〈銃など〉の・〈物〉を のような補足を消し、1行に訳語を3つまで
  function shortSense(s) {
    var items = s.replace(/〈[^〉]*〉[のをにがでと]?/g, "").split(/[,;，；]/).map(function (t) {
      return t.replace(/^[のをにがでと、\s]+/, "").trim();
    }).filter(function (t, i, a) { return t && t !== "『』" && a.indexOf(t) === i; });
    return items.slice(0, 3).join(", ");
  }
  function splitSenses(m) {
    return m.split(" / ").map(function (s) { return shortSense(s.replace(/\(…[^)]*\)/g, "").replace(/^[…\s,]+/, "")); })
      .filter(function (s, i, a) { return s && a.indexOf(s) === i; });
  }
  function formsOf(word, head) {          // 例文で太字にする形
    var f = [word.toLowerCase(), head];
    var stem = head.replace(/e$/, ""), y = head.replace(/y$/, "i");
    [head + "s", head + "es", head + "ed", head + "d", head + "ing", stem + "ing", y + "es", y + "ed",
     head + head.slice(-1) + "ed", head + head.slice(-1) + "ing"].forEach(function (x) { if (f.indexOf(x) < 0) f.push(x); });
    return f;
  }
  function formsRe(forms) {
    return new RegExp("\\b(" + forms.map(function (x) { return x.replace(/[-']/g, "\\$&"); }).join("|") + ")\\b", "i");
  }

  // ---------- 例文 ----------
  // Tatoeba: 人が訳した英文と和文。出てくる言葉が同じ単語（または活用した形）のものだけ使う
  function tatoeba(word, head) {
    var url = "https://api.tatoeba.org/unstable/sentences?lang=eng&q=" + encodeURIComponent(word) +
      "&trans:lang=jpn&sort=relevance&limit=30";
    var exact = new RegExp("\\b" + word.replace(/[-']/g, "\\$&") + "\\b", "i"), re = formsRe(formsOf(word, head));
    return timeoutFetch(url, 10000).then(function (r) { return r.json(); }).then(function (d) {
      return (d.data || []).map(function (s) {
        var tr = s.translations || [];
        var flat = tr.length && Array.isArray(tr[0]) ? [].concat.apply([], tr) : tr;
        var ja = flat.filter(function (t) { return t.lang === "jpn" && !t.is_unapproved; })
          .sort(function (a, b) { return (b.is_direct ? 1 : 0) - (a.is_direct ? 1 : 0); })[0];
        return ja && re.test(s.text) ? { en: s.text, ja: ja.text, score: (exact.test(s.text) ? 0 : 1000) + Math.abs(s.text.length - 45) } : null;
      }).filter(Boolean).sort(function (a, b) { return a.score - b.score; }).slice(0, 2)
        .map(function (x) { return { en: x.en, ja: x.ja, src: "tatoeba" }; });
    }).catch(function () { return []; });
  }
  // ページの記事の英文から1つ選んで、機械翻訳する（Tatoeba にないとき）
  function fromArticles(word, head) {
    var re = formsRe(formsOf(word, head)), best = null;
    document.querySelectorAll(".en-desc, .en-sum, .item h3 a").forEach(function (el) {
      (el.textContent.replace(/^In short:?\s*/, "").match(/[^.!?]+[.!?]/g) || []).forEach(function (s) {
        s = s.trim();
        if (s.length < 30 || s.length > 180 || !re.test(s) || /…$/.test(s)) return;
        var score = Math.abs(s.length - 90);
        if (!best || score < best.score) best = { en: s, score: score };
      });
    });
    if (!best) return Promise.resolve([]);
    return machine(best.en, "en", "ja").then(function (r) { return [{ en: best.en, ja: r.dst, src: "news" }]; },
                                               function () { return []; });
  }

  function phonetic(head) {
    return timeoutFetch("https://api.dictionaryapi.dev/api/v2/entries/en/" + encodeURIComponent(head), 8000)
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (d) {
        var e = d[0] || {};
        var p = e.phonetic || ((e.phonetics || []).filter(function (x) { return x.text; })[0] || {}).text || "";
        return p;
      }).catch(function () { return ""; });
  }

  // ---------- 機械翻訳（文章） ----------
  var chromeTr = {}, chromeWait = {}, chromeFailed = {};
  function chromeTranslator(from, to) {
    var key = from + "-" + to, T = window.Translator;
    if (!T || typeof T.availability !== "function" || chromeFailed[key]) return Promise.resolve(null);
    if (chromeTr[key]) return Promise.resolve(chromeTr[key]);
    if (chromeWait[key]) return Promise.resolve(null);
    return Promise.resolve().then(function () {
      return T.availability({ sourceLanguage: from, targetLanguage: to });
    }).then(function (a) {
      if (a === "unavailable") { chromeFailed[key] = true; return null; }
      var p = T.create({ sourceLanguage: from, targetLanguage: to })
        .then(function (t) { chromeTr[key] = t; delete chromeWait[key]; return t; },
              function () { chromeFailed[key] = true; delete chromeWait[key]; return null; });
      if (a === "available") return p;
      chromeWait[key] = p;       // 初回のダウンロード中は MyMemory で訳す
      return null;
    }, function () { chromeFailed[key] = true; return null; });
  }
  function timeoutFetch(url, ms) {
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, ms) : 0;
    return fetch(url, ctrl ? { signal: ctrl.signal } : {}).then(function (r) { clearTimeout(timer); return r; },
      function (e) { clearTimeout(timer); throw e; });
  }
  function utf8Len(s) { return new TextEncoder().encode(s).length; }
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
    var url = "https://api.mymemory.translated.net/get?q=" + encodeURIComponent(q.trim()) + "&langpair=" + from + "%7C" + to;
    return timeoutFetch(url, 15000).then(function (r) {
      return r.json().catch(function () { throw new Error("訳せませんでした"); });
    }, function () {
      throw new Error("ネットにつながりません");
    }).then(function (d) {
      var status = +d.responseStatus;
      if (status === 429 || d.quotaFinished) throw new Error("今日の翻訳の上限に達しました");
      if (status !== 200 || !d.responseData) throw new Error("訳せませんでした");
      return decodeEntities(d.responseData.translatedText || "");
    });
  }
  function myMemory(text, from, to) {
    var outLines = [], chain = Promise.resolve();
    text.split(/\n/).forEach(function (line, i) {
      chain = chain.then(function () {
        if (!line.trim()) { outLines[i] = ""; return; }
        var done = [], c = Promise.resolve();
        chunks(line).forEach(function (p, k) {
          c = c.then(function () { return myMemoryOne(p, from, to).then(function (t) { done[k] = t.trim(); }); });
        });
        return c.then(function () { outLines[i] = done.join(to === "ja" ? "" : " "); });
      });
    });
    return chain.then(function () { return outLines.join("\n").trim(); });
  }
  function machine(text, from, to) {
    return Promise.resolve().then(function () { return chromeTranslator(from, to); }).then(function (t) {
      return t ? t.translate(text).then(function (r) { return { dst: r, engine: "chrome" }; }, function () { return null; }) : null;
    }).then(function (r) {
      return r || myMemory(text, from, to).then(function (dst) { return { dst: dst, engine: "mymemory" }; });
    });
  }

  // ---------- 表示 ----------
  function bold(s) { return esc(s).replace(/『([^』]*)』/g, "<b>$1</b>"); }
  function showWord(x) {
    current = x;
    out.hidden = false;
    var senses = x.senses || [];
    var h = '<div class="tr-head">' +
      (x.src.toLowerCase() !== x.head ? '<span class="tr-from">' + esc(x.src) + ' →</span>' : "") +
      '<span class="tr-word">' + esc(x.head) + '</span>' +
      (x.form ? '<span class="tr-from">（' + esc(x.form) + '）</span>' : "") +
      (x.ipa ? '<span class="tr-ipa">' + esc(x.ipa) + '</span>' : "") + sayBtn(x.head) + '</div>';
    if (senses.length) {
      h += '<ol class="tr-senses">' + senses.map(function (s, i) {
        return '<li' + (i >= SENSES_SHOWN ? " hidden" : "") + '>' + bold(s) + '</li>';
      }).join("") + '</ol>';
      if (senses.length > SENSES_SHOWN) h += '<button type="button" class="tr-more" id="tr-more">ほか ' + (senses.length - SENSES_SHOWN) + ' 件</button>';
    } else if (x.mt) {
      h += '<div class="tr-text">' + esc(x.mt) + '</div>';
    }
    if (x.examples === undefined) {
      h += '<div class="tr-label"><span>例文</span></div><div class="tr-wait">…</div>';
    } else if (x.examples.length) {
      var tatoeba = x.examples.some(function (e) { return e.src === "tatoeba"; });
      var re = formsRe(formsOf(x.src, x.head));
      h += '<div class="tr-label"><span>例文</span>' +
        (tatoeba ? '<a href="https://tatoeba.org/ja" target="_blank" rel="noopener">Tatoeba</a>' : "") + '</div>' +
        x.examples.map(function (e) {
          return '<div class="tr-ex"><div class="tr-ex-en">' + esc(e.en).replace(re, "<b>$1</b>") + " " + sayBtn(e.en) +
            '</div><div class="tr-ex-ja">' + esc(e.ja) + '</div></div>';
        }).join("");
    }
    out.innerHTML = h;
  }
  function showText(x) {
    current = x;
    out.hidden = false;
    var en = x.from === "en" ? x.src : x.dst;
    out.innerHTML = '<div class="tr-text" lang="' + esc(x.to || "ja") + '">' + esc(x.dst) + '</div>' +
      (en && canSpeak ? '<div style="margin-top:4px">' + sayBtn(en) + '</div>' : "");
  }
  function showError(msg) {
    current = null;
    out.hidden = false;
    out.innerHTML = '<div class="tr-err">' + esc(msg) + '</div>';
  }
  out.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.say) speak(b.dataset.say);
    if (b.id === "tr-more") {
      out.querySelectorAll(".tr-senses li[hidden]").forEach(function (li) { li.hidden = false; });
      b.remove();
    }
  });

  // ---------- 訳す ----------
  function run(text) {
    text = (text || "").trim().slice(0, MAX_CHARS);
    if (!text || busy) return;
    busy = true;
    goBtn.disabled = true;
    var done = function () { busy = false; goBtn.disabled = false; };
    var isWord = !JA_RE.test(text) && (WORD_RE.test(text) || text.split(/\s+/).length <= 3);
    var p = isWord ? runWord(text) : Promise.resolve(false);
    p.then(function (shown) {
      if (shown) return;
      var ja = JA_RE.test(text), from = ja ? "ja" : "en", to = ja ? "en" : "ja";
      out.hidden = false;
      out.innerHTML = '<div class="tr-wait">…</div>';
      return machine(text, from, to).then(function (r) {
        var x = { kind: "text", src: text, dst: r.dst, from: from, to: to, at: Date.now() };
        showText(x);
        addHistory(x);
      });
    }).catch(function (e) { showError(e.message || "訳せませんでした"); }).then(done);
  }
  // 単語なら辞書で引く。辞書にない 1 語は、機械翻訳した意味と例文を出す。辞書にない語句は文章として訳す（false）
  function runWord(text) {
    var single = WORD_RE.test(text);
    return findWord(text).catch(function () { return null; }).then(function (f) {
      if (!f && !single) return false;
      var x = { kind: "word", src: text, head: f ? f.head : text.toLowerCase(), form: f && f.form, senses: f ? f.senses : [], at: Date.now() };
      var mt = f ? Promise.resolve() : machine(text, "en", "ja").then(function (r) { x.mt = r.dst; });
      return mt.then(function () {
        showWord(x);
        return Promise.all([phonetic(x.head), tatoeba(text, x.head)]);
      }).then(function (r) {
        x.ipa = r[0];
        return r[1].length ? r[1] : fromArticles(text, x.head);
      }).then(function (ex) {
        x.examples = ex;
        if (current === x) showWord(x);
        addHistory(x);
        return true;
      });
    });
  }

  // ---------- 開く・閉じる・入力 ----------
  function fitInput() {
    input.style.height = "36px";
    input.style.height = Math.min(input.scrollHeight + 2, 120) + "px";
  }
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
  fab.addEventListener("click", function () { openPanel(); input.focus(); input.select(); });
  $("tr-close").addEventListener("click", closePanel);
  goBtn.addEventListener("click", function () { run(input.value); });
  input.addEventListener("input", fitInput);
  input.addEventListener("keydown", function (e) {      // Enter で訳す（Shift + Enter で改行）
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing && e.keyCode !== 229) { e.preventDefault(); run(input.value); }
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
    // ページが自分で「🔤 訳す」を出すとき（教科書のページなど、<html data-no-tr-chip>）は出さない
    if (document.documentElement.hasAttribute("data-no-tr-chip")) { chip.hidden = true; return; }
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
  chip.addEventListener("mousedown", function (e) { e.preventDefault(); });
  chip.addEventListener("click", function () {
    var s = selectedText();
    chip.hidden = true;
    if (!s) return;
    openPanel();
    input.value = s.text;
    fitInput();
    run(s.text);
  });

  // ほかのページ（教科書など）から、文字を渡して訳す: window.agriTranslate("rumination")
  window.agriTranslate = function (text) {
    if (!text) return;
    openPanel();
    input.value = text;
    fitInput();
    run(text);
  };
})();
