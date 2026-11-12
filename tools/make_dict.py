#!/usr/bin/env python3
"""英和辞書 EJDict（パブリックドメイン）から、サイトの「🔤 訳す」で使う辞書データを作る。

    git clone --depth 1 https://github.com/kujirahand/EJDict.git /tmp/EJDict
    python3 tools/make_dict.py /tmp/EJDict

site/dict/a.json 〜 z.json（{"単語": "意味1 / 意味2 / …"}）を作る。
意味は、文法の注記《…》・数えられるかの印〈C〉〈U〉・品詞の印{名} を消し、古い意味やまれな意味は外す。
大事な訳語に付いている『』は残す（画面では太字にする）。
"""

import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "site" / "dict"
DROP = re.compile(r"《(古|まれ|方)》")          # 古い意味・まれな意味・方言は外す


def clean(meaning):
    senses = []
    for s in meaning.split(" / "):
        if DROP.search(s):
            continue
        s = re.sub(r"《[^》]*》", "", s)            # 文法の注記
        s = re.sub(r"〈[CUV]〉", "", s)             # 数えられるか
        s = re.sub(r"\{[^}]*\}", "", s)             # 品詞の印
        s = re.sub(r"\s+", " ", s).strip(" ,;、")
        if s and s not in senses:
            senses.append(s)
    return " / ".join(senses)


def main():
    src = Path(sys.argv[1]) / "src"
    words = {}
    for f in sorted(src.glob("*.txt")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if "\t" not in line:
                continue
            keys, meaning = line.split("\t", 1)
            meaning = clean(meaning)
            if not meaning:
                continue
            for k in keys.split(","):
                k = k.strip()
                key = k.lower()
                if not re.match(r"^[a-z]", key):
                    continue
                if k != key and k[:1].isupper():      # May（5月）と may のように、大文字の言葉は印を付ける
                    meaning_k = f"({k}) {meaning}"
                else:
                    meaning_k = meaning
                words[key] = words[key] + " / " + meaning_k if key in words else meaning_k
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for letter in "abcdefghijklmnopqrstuvwxyz":
        part = {k: v for k, v in sorted(words.items()) if k[0] == letter}
        body = json.dumps(part, ensure_ascii=False, separators=(",", ":"))
        (OUT / f"{letter}.json").write_text(body, encoding="utf-8")
        total += len(body.encode())
    print(f"{len(words)} 語、{total / 1e6:.1f} MB を {OUT} に書きました")


if __name__ == "__main__":
    main()
