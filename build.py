#!/usr/bin/env python3
"""スマート農業・酪農・IoT のニュースを RSS から集めて、静的サイトを作る。

    python3 build.py            # ニュースを取得して docs/ を作り直す
    python3 build.py --offline  # 取得せず、data/news.json から docs/ だけ作り直す

標準ライブラリだけで動く（GitHub Actions でもそのまま実行できる）。
"""

import argparse
import email.utils
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "news.json"
TEMPLATE = ROOT / "site" / "template.html"
OUT = ROOT / "docs"
JST = timezone(timedelta(hours=9))
KEEP_DAYS = 30
SNIPPET_LEN = 110
UA = "smart-agri-news/1.0 (+https://github.com/yusuke1090/smart-agri-news)"

# ---------------------------------------------------------------------------
# カテゴリ（タイトルと抜粋にキーワードが含まれていれば、そのカテゴリになる）
# ---------------------------------------------------------------------------
CATEGORIES = {
    "dairy": {
        "name": "酪農・畜産",
        "words": ["酪農", "乳牛", "生乳", "牛乳", "乳業", "搾乳", "畜産", "肉牛", "和牛", "子牛",
                  "家畜", "牧場", "牧草", "飼料", "繁殖", "養豚", "養鶏", "鶏卵", "ＣＳＦ", "豚熱",
                  "口蹄疫", "鳥インフル", "乳製品", "チーズ", "バター", "ヨーグルト"],
    },
    "smart": {
        "name": "スマート農業",
        "words": ["スマート農業", "スマート畜産", "スマート酪農", "スマート農", "アグリテック",
                  "農業DX", "農業ＤＸ", "ドローン", "ロボット", "自動操舵", "自動運転", "無人",
                  "AI", "ＡＩ", "人工知能", "ICT", "ＩＣＴ", "データ", "遠隔", "衛星", "アプリ",
                  "自動化", "省力化", "精密農業", "可変施肥", "環境制御", "植物工場", "ゲノム"],
    },
    "iot": {
        "name": "IoT・センサー",
        "words": ["IoT", "ＩｏＴ", "センサ", "センシング", "ウェアラブル", "首輪", "LPWA", "LoRa",
                  "通信", "5G", "５Ｇ", "クラウド", "モニタリング", "見守り", "カメラ", "画像解析",
                  "マイコン", "Raspberry", "ラズパイ", "エッジ"],
    },
    "policy": {
        "name": "行政・政策",
        "words": ["農林水産省", "農水省", "農相", "補助金", "交付金", "予算", "法案", "制度",
                  "基本計画", "白書", "統計", "価格", "報道発表"],
    },
}

# 一般のテック系ニュースから拾うときに、農業に関係する記事かどうかを判定する言葉
AGRI_WORDS = ["農業", "農家", "農作", "農産", "農地", "営農", "圃場", "ほ場", "就農", "農機",
              "酪農", "畜産", "牛", "豚", "鶏", "牧場", "家畜", "飼料", "作物", "収穫", "栽培",
              "施設園芸", "ハウス", "果樹", "水田", "稲作", "アグリ", "JA", "ＪＡ"]

# ---------------------------------------------------------------------------
# ニュース元
#   kind = "agri"   : 農業専門メディア。CATEGORIES のどれかに当てはまる記事だけ載せる
#   kind = "gov"    : 行政。CATEGORIES に当てはまる記事を「行政・政策」つきで載せる
#   kind = "dairy"  : 畜産・酪農専門。全部載せる
#   kind = "tech"   : テック系。AGRI_WORDS を含む記事だけ載せる
#   kind = "search" : Google ニュースのキーワード検索。全部載せる
# ---------------------------------------------------------------------------
def gnews(q):
    return ("https://news.google.com/rss/search?q=" + urllib.parse.quote(q) +
            "&hl=ja&gl=JP&ceid=JP:ja")


SOURCES = [
    {"name": "日本農業新聞", "url": "https://www.agrinews.co.jp/feed", "kind": "agri"},
    {"name": "マイナビ農業", "url": "https://agri.mynavi.jp/feed/", "kind": "agri"},
    {"name": "AGRI JOURNAL", "url": "https://agrijournal.jp/feed/", "kind": "agri"},
    {"name": "農林水産省 報道発表", "url": "https://www.maff.go.jp/j/press/rss.xml", "kind": "gov"},
    {"name": "農畜産業振興機構（ALIC）", "url": "https://www.alic.go.jp/rss.xml", "kind": "dairy"},
    {"name": "IoT NEWS", "url": "https://iotnews.jp/feed", "kind": "tech"},
    {"name": "MONOist", "url": "https://rss.itmedia.co.jp/rss/2.0/monoist.xml", "kind": "tech"},
    {"name": "ITmedia", "url": "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml", "kind": "tech"},
    {"name": "日刊工業新聞", "url": "https://www.nikkan.co.jp/rss/nksrdf.rdf", "kind": "tech"},
    {"name": "Google ニュース「スマート農業」", "url": gnews("スマート農業"), "kind": "search", "cat": "smart"},
    {"name": "Google ニュース「スマート畜産」", "url": gnews("スマート畜産 OR スマート酪農"), "kind": "search", "cat": "dairy"},
    {"name": "Google ニュース「酪農」", "url": gnews("酪農"), "kind": "search", "cat": "dairy"},
    {"name": "Google ニュース「畜産 IoT」", "url": gnews("畜産 IoT OR 牛 センサー"), "kind": "search", "cat": "iot"},
    {"name": "Google ニュース「農業 IoT」", "url": gnews("農業 IoT OR 農業 センサー"), "kind": "search", "cat": "iot"},
    {"name": "Google ニュース「農業 AI」", "url": gnews("農業 AI OR 農業DX"), "kind": "search", "cat": "smart"},
]

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "rss1": "http://purl.org/rss/1.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


# ---------------------------------------------------------------------------
# 取得と解析
# ---------------------------------------------------------------------------
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, */*"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def to_utf8(raw):
    """Shift_JIS などの XML を、ElementTree が読める UTF-8 に直す。"""
    m = re.match(rb'^\s*<\?xml[^>]*encoding=["\']([\w.-]+)["\']', raw)
    enc = m.group(1).decode().lower() if m else "utf-8"
    if enc in ("utf-8", "utf8", "us-ascii"):
        return raw
    text = raw.decode(enc, errors="replace")
    text = re.sub(r'^\s*<\?xml[^>]*\?>', '<?xml version="1.0" encoding="utf-8"?>', text, count=1)
    return text.encode("utf-8")


def clean_text(s, limit=None):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s.replace("　", " ")).strip()
    if limit and len(s) > limit:
        s = s[:limit].rstrip() + "…"
    return s


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=JST)
    return d.astimezone(JST)


def parse_feed(raw):
    root = ET.fromstring(to_utf8(raw))
    items = []
    # RSS 2.0
    for it in root.iter("item"):
        src = it.find("source")
        items.append({
            "title": it.findtext("title"), "link": it.findtext("link"),
            "date": it.findtext("pubDate") or it.findtext("dc:date", namespaces=NS),
            "desc": it.findtext("description"),
            "publisher": src.text if src is not None else None,
        })
    # RSS 1.0 (RDF)
    for it in root.iter(f"{{{NS['rss1']}}}item"):
        items.append({
            "title": it.findtext("rss1:title", namespaces=NS), "link": it.findtext("rss1:link", namespaces=NS),
            "date": it.findtext("dc:date", namespaces=NS), "desc": it.findtext("rss1:description", namespaces=NS),
            "publisher": None,
        })
    # Atom
    for it in root.iter(f"{{{NS['atom']}}}entry"):
        link = it.find("atom:link", NS)
        items.append({
            "title": it.findtext("atom:title", namespaces=NS),
            "link": link.get("href") if link is not None else None,
            "date": it.findtext("atom:published", namespaces=NS) or it.findtext("atom:updated", namespaces=NS),
            "desc": it.findtext("atom:summary", namespaces=NS), "publisher": None,
        })
    return items


def categorize(text):
    return [key for key, c in CATEGORIES.items() if any(w in text for w in c["words"])]


def dedup_key(title):
    return re.sub(r"[\s\W_]+", "", title).lower()[:60]


def collect(source, now):
    raw = fetch(source["url"])
    out = []
    for it in parse_feed(raw):
        title = clean_text(it["title"])
        link = (it["link"] or "").strip()
        if not title or not link.startswith("http"):
            continue
        publisher = source["name"]
        snippet = clean_text(it["desc"], SNIPPET_LEN)
        if source["kind"] == "search":
            # Google ニュースは「タイトル - 媒体名」になっているので分ける
            publisher = clean_text(it["publisher"]) or publisher
            if publisher and title.endswith(" - " + publisher):
                title = title[: -len(" - " + publisher)]
            snippet = ""          # 説明文はタイトルの繰り返しなので使わない
        text = title + " " + snippet
        cats = categorize(text)
        kind = source["kind"]
        if kind == "agri" and not (set(cats) & {"dairy", "smart", "iot"}):
            continue
        if kind == "gov":
            if not (set(cats) & {"dairy", "smart", "iot"}):
                continue
            cats = sorted(set(cats) | {"policy"}, key=list(CATEGORIES).index)
        if kind == "dairy" and "dairy" not in cats:
            cats = ["dairy"] + cats
        if kind == "tech":
            if not any(w in text for w in AGRI_WORDS):
                continue
            if not cats:
                cats = ["iot"]
        if kind == "search" and not cats:
            cats = [source["cat"]]
        published = parse_date(it["date"]) or now
        if published > now + timedelta(hours=1):
            published = now
        out.append({
            "title": title, "link": link, "publisher": publisher, "via": source["name"],
            "snippet": snippet, "cats": cats, "published": published.isoformat(timespec="minutes"),
        })
    return out


# ---------------------------------------------------------------------------
# サイトの生成
# ---------------------------------------------------------------------------
WEEKDAYS = "月火水木金土日"


def day_label(d):
    return f"{d.month}月{d.day}日（{WEEKDAYS[d.weekday()]}）"


def render(items, statuses, now):
    groups = {}
    for it in items:
        d = datetime.fromisoformat(it["published"]).astimezone(JST)
        groups.setdefault(d.date(), []).append((d, it))

    today = now.date()
    parts = []
    for day in sorted(groups, reverse=True):
        rows = sorted(groups[day], key=lambda x: x[0], reverse=True)
        label = day_label(day) + ("・今日" if day == today else "・昨日" if day == today - timedelta(days=1) else "")
        parts.append(f'<section class="day" data-day="{day.isoformat()}">'
                     f'<h2>{html.escape(label)}<span class="count">{len(rows)}件</span></h2>')
        for d, it in rows:
            is_new = d >= now - timedelta(hours=24)
            tags = "".join(f'<span class="tag t-{c}">{html.escape(CATEGORIES[c]["name"])}</span>'
                           for c in it["cats"])
            search = (it["title"] + " " + it["publisher"] + " " + it["snippet"]).lower()
            snippet = f'<p class="snippet">{html.escape(it["snippet"])}</p>' if it["snippet"] else ""
            parts.append(
                f'<article class="item" data-cats="{" ".join(it["cats"])}" data-new="{int(is_new)}" '
                f'data-search="{html.escape(search)}">'
                f'<div class="tags">{tags}{"<span class=new>NEW</span>" if is_new else ""}</div>'
                f'<h3><a href="{html.escape(it["link"])}" target="_blank" rel="noopener">{html.escape(it["title"])}</a></h3>'
                f'{snippet}'
                f'<div class="meta">{html.escape(it["publisher"])} ・ {d.strftime("%H:%M")}</div>'
                f'</article>')
        parts.append("</section>")

    counts = {k: sum(1 for it in items if k in it["cats"]) for k in CATEGORIES}
    chips = [f'<button class="chip on" data-cat="all">すべて<span>{len(items)}</span></button>']
    chips += [f'<button class="chip" data-cat="{k}">{html.escape(c["name"])}<span>{counts[k]}</span></button>'
              for k, c in CATEGORIES.items()]
    new_count = sum(1 for it in items
                    if datetime.fromisoformat(it["published"]) >= now - timedelta(hours=24))

    src_rows = "".join(
        f'<li class="{"ok" if s["ok"] else "ng"}">{html.escape(s["name"])}'
        f'<span>{s["count"]}件{"" if s["ok"] else "（取得できませんでした）"}</span></li>'
        for s in statuses)

    page = TEMPLATE.read_text(encoding="utf-8")
    return (page
            .replace("{{UPDATED}}", now.strftime("%Y年%-m月%-d日 %H:%M"))
            .replace("{{UPDATED_ISO}}", now.isoformat(timespec="minutes"))
            .replace("{{TOTAL}}", str(len(items)))
            .replace("{{NEW}}", str(new_count))
            .replace("{{DAYS}}", str(KEEP_DAYS))
            .replace("{{CHIPS}}", "".join(chips))
            .replace("{{SOURCES}}", src_rows)
            .replace("{{ITEMS}}", "\n".join(parts) or '<p class="empty">ニュースがありません</p>'))


def build_rss(items, now):
    """このサイト自身の RSS（新しい順に50件）"""
    entries = []
    for it in items[:50]:
        d = datetime.fromisoformat(it["published"])
        cats = "、".join(CATEGORIES[c]["name"] for c in it["cats"])
        entries.append(
            "<item>"
            f"<title>{html.escape(it['title'])}</title>"
            f"<link>{html.escape(it['link'])}</link>"
            f"<guid isPermaLink=\"false\">{html.escape(it['link'])}</guid>"
            f"<pubDate>{email.utils.format_datetime(d)}</pubDate>"
            f"<description>{html.escape(it['publisher'] + '｜' + cats + ('｜' + it['snippet'] if it['snippet'] else ''))}</description>"
            "</item>")
    return ('<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0"><channel>'
            "<title>スマート農業News</title>"
            "<link>https://yusuke1090.github.io/smart-agri-news/</link>"
            "<description>スマート農業・酪農・畜産・IoT のニュースを毎朝まとめています</description>"
            "<language>ja</language>"
            f"<lastBuildDate>{email.utils.format_datetime(now)}</lastBuildDate>"
            + "".join(entries) + "</channel></rss>\n")


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="取得せずに docs/ だけ作り直す")
    args = ap.parse_args()

    now = datetime.now(JST).replace(second=0, microsecond=0)
    old = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"items": [], "sources": []}
    items = {dedup_key(it["title"]): it for it in old["items"]}
    statuses = old.get("sources", [])

    if not args.offline:
        statuses = []
        for src in SOURCES:
            try:
                got = collect(src, now)
                added = 0
                for it in got:
                    k = dedup_key(it["title"])
                    if k in items:
                        continue
                    it["first_seen"] = now.isoformat(timespec="minutes")
                    items[k] = it
                    added += 1
                statuses.append({"name": src["name"], "ok": True, "count": len(got)})
                print(f"OK  {src['name']}: {len(got)}件（新規 {added}件）")
            except Exception as e:  # noqa: BLE001  1つのニュース元が失敗しても続ける
                statuses.append({"name": src["name"], "ok": False, "count": 0})
                print(f"NG  {src['name']}: {type(e).__name__}: {e}", file=sys.stderr)

    cutoff = now - timedelta(days=KEEP_DAYS)
    kept = [it for it in items.values() if datetime.fromisoformat(it["published"]) >= cutoff]
    kept.sort(key=lambda it: it["published"], reverse=True)

    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps({"updated": now.isoformat(timespec="minutes"), "sources": statuses,
                                "items": kept}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(render(kept, statuses, now), encoding="utf-8")
    (OUT / "feed.xml").write_text(build_rss(kept, now), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"記事 {len(kept)}件で docs/ を作りました（{now:%Y-%m-%d %H:%M} JST）")


if __name__ == "__main__":
    main()
