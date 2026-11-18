// ☆ お気に入りと 🔤 訳すの履歴を、教科書と同じ Firebase（textbooks-d3862）に置いて、スマホと PC で合わせる。
// ログインは教科書と同じ（ID とパスワード、または Google）。どちらも yusuke1090.github.io のページなので、
// 教科書でログインしていれば、ここでもログインしている（ログアウトも両方いっしょ）。
//
// しくみ
// - 記録は今までどおり localStorage。合わせるのは KEYS のキーだけ
// - 1秒ごとに中身が変わったかを見て、変わっていれば users/{uid}/kv/{キー} へ書く。中身は { v: 文字列, t: 変えた時刻, dev: 端末 }
//   （教科書の記録と同じ置き場所。キーの名前で分かれていて、教科書の sync.js は textbooks- のキーしか読まない）
// - ほかの端末が書いたものは onSnapshot で受け取り、新しいほう（t が大きいほう）を使う
// - ログインする前からその端末にあった記録は、最初の1回だけ足し合わせる
import config from "./firebase-config.js";

const CDN = "https://www.gstatic.com/firebasejs/10.12.2/";
const KEYS = ["agri-news-favs", "agri-news-translate-history"];
const META = "agri-news-sync";          // { dev: 端末, uid: 最後に合わせた人, k: { キー: { t: 変えた時刻, h: 中身の印, s: 1 ならもう合わせた } } }
const ID_DOMAIN = "@textbooks.example.com";
const ls = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
};
const parse = (s, d) => { try { const v = JSON.parse(s); return v == null ? d : v; } catch (e) { return d; } };
const hash = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(36) + "." + s.length; };
const meta = parse(ls.get(META), {});
if (!meta.dev) meta.dev = Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
if (!meta.k || typeof meta.k !== "object") meta.k = {};
const dev = meta.dev;
const saveMeta = () => ls.set(META, JSON.stringify(meta));
const dirty = new Set();
let user = null, db = null, F = null, flushTimer = 0;

// この端末で変わった記録を見つける（ニュースのページ・伝言板・教科書の 🔤 のどこで変えても）
function scan() {
  let any = false;
  for (const k of KEYS) {
    const v = ls.get(k);
    if (v === null) continue;
    const h = hash(v), m = meta.k[k];
    if (m && m.h === h) continue;
    meta.k[k] = { t: Date.now(), h, s: m ? m.s : 0 };
    dirty.add(k);
    any = true;
  }
  if (any) { saveMeta(); schedule(); }
}
function setLocal(k, v, t) { ls.set(k, v); meta.k[k] = { t, h: hash(v), s: 1 }; dirty.delete(k); }
function schedule() { clearTimeout(flushTimer); flushTimer = setTimeout(flush, 1500); }
function refresh() { window.agriNewsRefresh && window.agriNewsRefresh(); }

if (config) {
  scan();
  saveMeta();
  setInterval(() => { if (!document.hidden) scan(); }, 1000);
  addEventListener("visibilitychange", () => { if (document.hidden) { scan(); flush(); } });
  addEventListener("pagehide", () => { scan(); flush(); });
  start().catch((e) => { console.warn("sync:", e); ready = true; status("err"); });
}

async function start() {
  const [{ initializeApp }, A, Fs] = await Promise.all([
    import(CDN + "firebase-app.js"), import(CDN + "firebase-auth.js"), import(CDN + "firebase-firestore.js"),
  ]);
  F = Fs;
  const app = initializeApp(config), auth = A.getAuth(app);
  db = F.getFirestore(app);
  let unsub = null;
  ui.login = (id, pw, isNew) => (isNew ? A.createUserWithEmailAndPassword : A.signInWithEmailAndPassword)(auth, id + ID_DOMAIN, pw);
  ui.google = () => A.signInWithPopup(auth, new A.GoogleAuthProvider());   // 押したその場でよぶ（iPhone でポップアップが止められないように）
  ui.logout = async () => { scan(); await flush(); await A.signOut(auth); };
  A.onAuthStateChanged(auth, async (u) => {
    if (unsub) { unsub(); unsub = null; }
    user = u;
    ready = true;
    status(u ? "sync" : "");
    if (!u) return;
    try {
      const q = F.query(F.collection(db, "users", u.uid, "kv"), F.where(F.documentId(), "in", KEYS));
      await firstSync(q);
      unsub = F.onSnapshot(q, onSnap, () => status("err"));
      status("ok");
    } catch (e) { console.warn("sync:", e); status("err"); }
  });
}

// ログインする前からこの端末にあった記録と、ほかの端末の記録を足し合わせる
function merge(k, local, remote) {
  const a = parse(local, null), b = parse(remote, null);
  if (k === "agri-news-favs" && a && b && typeof a === "object" && typeof b === "object") {
    return JSON.stringify({ ...b, ...a });
  }
  if (k === "agri-news-translate-history" && Array.isArray(a) && Array.isArray(b)) {
    const key = (x) => String((x && (x.head || x.src)) || "").toLowerCase();
    const seen = new Set(b.map(key));
    return JSON.stringify(b.concat(a.filter((x) => !seen.has(key(x)))).slice(0, 50));
  }
  return remote;
}

async function firstSync(q) {
  if (meta.uid !== user.uid) { Object.values(meta.k).forEach((m) => { m.s = 0; }); meta.uid = user.uid; }
  scan();
  const snap = await F.getDocs(q);
  const remote = {};
  snap.forEach((d) => { remote[d.id] = d.data(); });
  let changed = false;
  for (const k of KEYS) {
    const r = remote[k], local = ls.get(k), m = meta.k[k];
    if (!r) { if (local !== null) dirty.add(k); continue; }
    if (local === r.v) { setLocal(k, local, Math.max(m ? m.t : 0, r.t)); continue; }
    if (local === null || (m.s && r.t > m.t)) { setLocal(k, r.v, r.t); changed = true; continue; }
    if (!m.s) {                                    // 合わせる前からこの端末にあった記録
      const v = merge(k, local, r.v);
      setLocal(k, v, Date.now());
      if (v !== r.v) dirty.add(k);
      changed = true;
      continue;
    }
    dirty.add(k);                                  // この端末のほうが新しい
  }
  saveMeta();
  await flush();
  if (changed) refresh();
}

function onSnap(qs) {
  let changed = false;
  qs.docChanges().forEach((ch) => {
    if (ch.type === "removed") return;
    const k = ch.doc.id, d = ch.doc.data();
    if (!KEYS.includes(k) || d.dev === dev) return;   // この端末が書いたもの
    scan();
    const m = meta.k[k];
    if (m && m.t >= d.t) return;
    if (ls.get(k) !== d.v) changed = true;
    setLocal(k, d.v, d.t);
  });
  saveMeta();
  if (changed) refresh();
}

async function flush() {
  clearTimeout(flushTimer);
  if (!user || !db || !dirty.size) return;
  const keys = [...dirty], uid = user.uid;
  dirty.clear();
  const batch = F.writeBatch(db);
  keys.forEach((k) => {
    const v = ls.get(k);
    if (v !== null) batch.set(F.doc(db, "users", uid, "kv", k), { v, t: meta.k[k].t, dev });
  });
  try {
    await batch.commit();
    if (user && user.uid === uid) keys.forEach((k) => { if (meta.k[k]) meta.k[k].s = 1; });
    saveMeta();
    status("ok");
  } catch (e) { keys.forEach((k) => dirty.add(k)); status("err"); console.warn("sync:", e); }
}

// ---------- 見出しの右上のログインの欄 ----------
const ui = { login: null, google: null, logout: null };
let lastState = "", ready = false;   // ready: ログインの状態がわかってから欄を出す
const esc = (t) => String(t).replace(/[<>&"]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]));
const ERR = {
  "auth/invalid-credential": "ID かパスワードがちがいます", "auth/wrong-password": "ID かパスワードがちがいます", "auth/user-not-found": "ID かパスワードがちがいます",
  "auth/invalid-login-credentials": "ID かパスワードがちがいます", "auth/email-already-in-use": "その ID はもう使われています。ログインしてください",
  "auth/weak-password": "パスワードは6文字以上にしてください", "auth/too-many-requests": "何度もまちがえたので、しばらく待ってからためしてください",
  "auth/network-request-failed": "インターネットにつながっていません", "auth/invalid-email": "ID に使えない文字があります",
  "auth/operation-not-allowed": "このログインのしかたは、まだ Firebase でオンになっていません",
  "auth/unauthorized-domain": "このサイトが Firebase の「承認済みドメイン」にまだ入っていません", "auth/popup-blocked": "ポップアップが止められました。もう一度押してください",
};
function status(s) { lastState = s; draw(); }
function draw() {
  const el = document.getElementById("acct");
  if (!el) return;
  if (!ready) { el.innerHTML = ""; return; }
  if (!user) {
    el.innerHTML = `<button type="button" class="acct-btn" aria-expanded="false" title="スマホと PC のお気に入りを合わせる">☁<span> ログイン</span></button>`
      + `<form class="acct-menu acct-form" hidden autocomplete="on">`
      + `<p class="m">教科書と同じ ID でログインすると、スマホと PC の ☆ お気に入りと 🔤 の履歴がそろいます</p>`
      + `<label>ID<input name="loginid" autocomplete="username" autocapitalize="off" spellcheck="false" placeholder="半角の英数字（3文字以上）" required></label>`
      + `<label>パスワード<input name="loginpw" type="password" autocomplete="current-password" placeholder="6文字以上" required></label>`
      + `<p class="acct-err" hidden></p>`
      + `<div class="acct-row"><button type="submit" class="pri">ログイン</button><button type="button" class="acct-new">はじめて使う（登録）</button></div>`
      + `<p class="acct-or">または</p><button type="button" class="acct-google">Google でログイン</button>`
      + `<p class="m">ID とパスワードと Google は、別の人として記録します</p></form>`;
    const btn = el.querySelector(".acct-btn"), form = el.querySelector("form"), err = el.querySelector(".acct-err");
    btn.onclick = () => { form.hidden = !form.hidden; btn.setAttribute("aria-expanded", !form.hidden); if (!form.hidden) form.elements.loginid.focus(); };
    const go = async (isNew) => {
      const id = form.elements.loginid.value.trim().toLowerCase(), pw = form.elements.loginpw.value;
      err.hidden = true;
      if (!/^[a-z0-9][a-z0-9._-]{2,29}$/.test(id)) { err.textContent = "ID は半角の英数字（. _ - も可）で3〜30文字にしてください"; err.hidden = false; return; }
      if (pw.length < 6) { err.textContent = ERR["auth/weak-password"]; err.hidden = false; return; }
      form.querySelectorAll("button").forEach((b) => { b.disabled = true; });
      try { await ui.login(id, pw, isNew); }
      catch (e) { err.textContent = ERR[e.code] || "ログインできませんでした（" + e.code + "）"; err.hidden = false; }
      form.querySelectorAll("button").forEach((b) => { b.disabled = false; });
    };
    form.onsubmit = (e) => { e.preventDefault(); go(false); };
    el.querySelector(".acct-new").onclick = () => { form.elements.loginpw.setAttribute("autocomplete", "new-password"); go(true); };
    el.querySelector(".acct-google").onclick = () => {
      err.hidden = true;
      ui.google().catch((e) => { if (e.code === "auth/popup-closed-by-user" || e.code === "auth/cancelled-popup-request") return; err.textContent = ERR[e.code] || "ログインできませんでした（" + e.code + "）"; err.hidden = false; });
    };
    return;
  }
  const id = (user.email || "").endsWith(ID_DOMAIN) ? user.email.slice(0, -ID_DOMAIN.length) : user.email || user.displayName || "";
  const label = lastState === "err" ? "⚠<span> 同期できません</span>" : lastState === "sync" ? "☁<span> 同期中…</span>" : "☁<span> 同期</span> ✓";
  el.innerHTML = `<button type="button" class="acct-btn on${lastState === "err" ? " err" : ""}" aria-expanded="false">${label}</button>`
    + `<div class="acct-menu" hidden><p><b>${esc(id)}</b> でログイン中</p><button type="button" class="acct-out">ログアウト</button></div>`;
  const btn = el.querySelector(".acct-btn"), menu = el.querySelector(".acct-menu");
  btn.onclick = () => { menu.hidden = !menu.hidden; btn.setAttribute("aria-expanded", !menu.hidden); };
  el.querySelector(".acct-out").onclick = () => ui.logout && ui.logout();
}
if (config) {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", draw); else draw();
  document.addEventListener("click", (e) => { const el = document.getElementById("acct"); if (el && !el.contains(e.target)) { const m = el.querySelector(".acct-menu"); if (m) m.hidden = true; } });
}
