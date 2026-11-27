#!/usr/bin/env python3
"""伝言板の書き込みに貼る図を作る（site/board-img/ に SVG を書く）。

    python3 tools/make_board_figures.py

書き込みには ![説明](https://yusuke1090.github.io/smart-agri-news/board-img/<名前>.svg) で貼る。
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "site" / "board-img"
FONT = "'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP','Noto Sans CJK JP',sans-serif"

# 色: 僕・きみ・2人・渡航・節目
ME = ("#e3eefb", "#1d4a7a")
YOU = ("#fde9d6", "#7a3f0c")
BOTH = ("#edf1e8", "#2f3a2c")
TRIP = ("#efe8fb", "#4b2f8f")
GOAL = ("#2e7d32", "#ffffff")


def text_w(s, size):
    """文字の幅のおおよそ（全角は1文字ぶん、半角は0.55）"""
    return sum(size if ord(c) > 0x2e7f else size * 0.55 for c in s)


def roadmap():
    W, L, R = 520, 52, 508          # 図の幅、中身の左右
    mid = (L + R) // 2
    CH, GAP, FS = 38, 8, 19         # チップの高さ・間・文字
    periods = [
        ("2026年12月〜2027年3月", "決める・聞く",
         ["試す牧場を決める", "酪農家20軒に聞く", "カラスを見分けるAI"], ["撃退器の試作0号", "首輪0号（IMU記録）"],
         [(BOTH, "2人の決まりを紙にして署名")]),
        ("2027年4月〜9月", "牧場で試す",
         ["確かさを数字にする", "分娩・妊娠の記録"], ["撃退器の試作1号", "首輪の試作1号"],
         [(TRIP, "8月 タンザニアへ（1回目）")]),
        ("2027年10月〜2028年3月", "冬を越す試験",
         ["3牧場で効果を測る", "分娩前後の兆しを探す"], ["首輪を10頭に", "量産の基板を決める"],
         [(BOTH, "3月 結果を見て、先に売る物を決める")]),
        ("2028年4月〜10月", "売る準備",
         ["モニター10牧場", "事業計画書・公庫", "8月 勤め方を決める"], ["量産前の10〜20台", "取扱説明書"],
         [(TRIP, "8月 タンザニアへ（2回目）・覚え書き")]),
        ("GOAL", "2028年11月 会社を作る・撃退器を売る"),
        ("2028年12月〜2029年11月", "広げる",
         ["首輪を売る（秋）", "タンザニアの手続き"], ["日本の製造・修理"], []),
        ("GOAL", "2029年11月 僕がタンザニアへ・支所を開く"),
    ]
    out, y = [], 0

    def chip(x, y, w, color, label, size=FS, bold=False, h=CH):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h // 2 if h < 44 else 12}" fill="{color[0]}"/>')
        out.append(f'<text x="{x + 14}" y="{y + h / 2 + size * 0.36:.0f}" font-size="{size}" fill="{color[1]}"'
                   + (' font-weight="700"' if bold else "") + f'>{escape(label)}</text>')
        assert text_w(label, size) + 28 <= w, f"長すぎる: {label}"

    # 見出しと、色の説明
    out.append(f'<text x="24" y="50" font-size="28" font-weight="700" fill="#1e2a1c">2年で会社、3年でタンザニア</text>')
    out.append(f'<text x="24" y="82" font-size="18" fill="#66735f">2026年12月 → 2029年11月</text>')
    x = 24
    for color, label in ((ME, "僕  機械学習・ソフト・営業"), (YOU, "きみ  回路・ハード")):
        w = text_w(label, 17) + 28
        chip(x, 100, w, color, label, 17, True, 32)
        x += w + 10
    y = 160
    rail_top = y
    for p in periods:
        if p[0] == "GOAL":
            out.append(f'<circle cx="30" cy="{y + 24}" r="11" fill="{GOAL[0]}"/>')
            chip(L, y, R - L, GOAL, p[1], 20, True, 48)
            y += 48 + 22
            continue
        when, name, me, you, extra = p
        out.append(f'<circle cx="30" cy="{y + 12}" r="8" fill="#fff" stroke="#66735f" stroke-width="3"/>')
        out.append(f'<text x="{L}" y="{y + 19}" font-size="20" font-weight="700" fill="#1e2a1c">{escape(when)}'
                   f'<tspan dx="12" font-weight="400" fill="#66735f">{escape(name)}</tspan></text>')
        y += 34
        for i, label in enumerate(me):
            chip(L, y + i * (CH + GAP), mid - L - 6, ME, label)
        for i, label in enumerate(you):
            chip(mid + 6, y + i * (CH + GAP), R - mid - 6, YOU, label)
        y += max(len(me), len(you)) * (CH + GAP)
        for color, label in extra:
            chip(L, y, R - L, color, label, FS, True)
            y += CH + GAP
        y += 18
    H = y + 6
    rail = f'<line x1="30" y1="{rail_top + 12}" x2="30" y2="{H - 60}" stroke="#c9d3c0" stroke-width="3"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">'
           f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="#ffffff" stroke="#dde3d6" stroke-width="2"/>'
           + rail + "".join(out) + "</svg>\n")
    return svg


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "7-roadmap.svg").write_text(roadmap(), encoding="utf-8")
    print("site/board-img/7-roadmap.svg")


if __name__ == "__main__":
    main()
