#!/usr/bin/env python3
"""伝言板の「やりたいこと」「アイデア」のうち、関連する事業をまだ調べていない書き込みを出す。

    python3 tools/board_unresearched.py          # まだ調べていないものの番号・題名・本文
    python3 tools/board_unresearched.py --all    # 調べたものも含めて全部

調べた結果は site/board-research.json に、Issue 番号をキーにして書く（書き方は README の「伝言板の調べもの」）。
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = "yusuke1090/smart-agri-news"
KINDS = ("やりたいこと", "アイデア")
RESEARCH = Path(__file__).resolve().parent.parent / "site" / "board-research.json"


def kind_of(body):
    m = re.search(r"^###\s*種類\s*\n+([^\n]+)", body or "", re.M)
    return m.group(1).strip() if m else "その他"


def main():
    url = (f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100&labels="
           + urllib.parse.quote("伝言板"))
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "smart-agri-news-board"})
    with urllib.request.urlopen(req, timeout=20) as r:
        issues = [i for i in json.load(r) if "pull_request" not in i]
    done = json.loads(RESEARCH.read_text(encoding="utf-8")).get("items", {}) if RESEARCH.exists() else {}
    show_all = "--all" in sys.argv
    todo = 0
    for i in sorted(issues, key=lambda x: x["number"]):
        kind = kind_of(i["body"])
        if kind not in KINDS:
            continue
        checked = done.get(str(i["number"]), {}).get("checked")
        if checked and not show_all:
            continue
        todo += 0 if checked else 1
        print(f"=== #{i['number']} [{kind}] {i['title']}" + (f"（{checked} 調べ済み）" if checked else "（まだ）"))
        print((i["body"] or "").strip(), "\n")
    if not show_all:
        print(f"まだ調べていないもの: {todo}件")


if __name__ == "__main__":
    main()
