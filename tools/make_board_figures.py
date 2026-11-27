#!/usr/bin/env python3
"""伝言板の書き込みに貼る図を作る（site/board-img/ に SVG を書く）。

    python3 tools/make_board_figures.py

書き込みには ![説明](https://yusuke1090.github.io/smart-agri-news/board-img/<名前>.svg) で貼る。
横に長い図（幅が高さの3倍より大きい）は、伝言板では縮めずに横に送って見る形で出る。
"""
from pathlib import Path
from xml.sax.saxutils import escape

import roadmap7

OUT = Path(__file__).resolve().parent.parent / "site" / "board-img"
FONT = "'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP','Noto Sans CJK JP',sans-serif"

# 色（背景, 文字）: 僕・A・2人・渡航・節目
ME = ("#dbe9fa", "#1d4a7a")
YOU = ("#fde3cc", "#7a3f0c")
BOTH = ("#e6ebe0", "#2f3a2c")
TRIP = ("#e8ddfa", "#4b2f8f")
GOAL = ("#2e7d32", "#ffffff")


def text_w(s, size):
    """文字の幅のおおよそ（全角は1文字ぶん、半角は0.55）"""
    return sum(size if ord(c) > 0x2e7f else size * 0.55 for c in s)


# ---------- #7 会社のロードマップ（横に月が並ぶ年表） ----------
START, MONTHS = (2026, 12), 36       # 2026年12月から3年
MW, LW = 100, 70                     # 1か月の幅、左の「僕・A・2人」の欄の幅
FS = 15                              # 文字の大きさ

# 項目は tools/roadmap7.py（伝言板のコメントや GitHub の Project と同じ中身）
TIMELINE = [(lane, color, [it[:3] for it in roadmap7.ITEMS[lane]])
            for lane, color in (("僕", ME), ("A", YOU), ("2人", BOTH))]


def month_x(ym):
    y, m = map(int, ym.split("-"))
    return LW + ((y - START[0]) * 12 + m - START[1]) * MW


def timeline():
    TRACK, BAR = 36, 28
    body, goals = [], []
    # 行（僕・A・2人）ごとに、重ならないように段を分ける
    lanes, y = [], 118
    for name, color, items in TIMELINE:
        ends, placed = [], []
        for start, end, label in items:
            x0 = month_x(start)
            if end in (None, "TRIP", "GOAL"):
                x1 = x0 + 4 + text_w(label, FS) + 24
            else:
                x1 = month_x(end) + MW
                assert text_w(label, FS) + 20 <= x1 - x0 - 8, f"短すぎる: {label}"
            for t, e in enumerate(ends):
                if e <= x0:
                    break
            else:
                t = len(ends)
                ends.append(0)
            ends[t] = x1 + 6
            placed.append((t, x0, x1, end, label))
        h = len(ends) * TRACK + 12
        lanes.append((name, color, y, h, placed))
        y += h + 8
    H = y + 12
    W = max(LW + MONTHS * MW, max(x1 for *_, placed in lanes for _, _, x1, _, _ in placed)) + 20

    out = [f'<rect x="1" y="1" width="{W - 2:.0f}" height="{H - 2}" rx="14" fill="#ffffff" stroke="#dde3d6" stroke-width="2"/>',
           f'<text x="20" y="38" font-size="22" font-weight="700" fill="#1e2a1c">ロードマップ'
           f'<tspan dx="14" font-size="15" font-weight="400" fill="#66735f">横に送って見る →</tspan></text>']
    # 年と月の見出し、月の区切りの線
    top, bottom = 112, H - 14
    for i in range(MONTHS):
        y_, m_ = divmod(START[1] - 1 + i, 12)
        year, month = START[0] + y_, m_ + 1
        x = LW + i * MW
        if i == 0 or month == 1:
            out.append(f'<text x="{x + 8}" y="70" font-size="17" font-weight="700" fill="#1e2a1c">{year}年</text>')
            out.append(f'<line x1="{x}" y1="54" x2="{x}" y2="{bottom}" stroke="#b9c4ae" stroke-width="2"/>')
        else:
            out.append(f'<line x1="{x}" y1="84" x2="{x}" y2="{bottom}" stroke="#eef1ea" stroke-width="1"/>')
        out.append(f'<text x="{x + MW / 2:.0f}" y="102" font-size="14" fill="#66735f" text-anchor="middle">{month}月</text>')
    out.append(f'<line x1="{LW}" y1="{top - 2}" x2="{LW + MONTHS * MW}" y2="{top - 2}" stroke="#b9c4ae" stroke-width="2"/>')
    # 行
    for name, color, y0, h, placed in lanes:
        out.append(f'<rect x="8" y="{y0}" width="{W - 16:.0f}" height="{h}" rx="10" fill="{color[0]}" fill-opacity="0.25"/>')
        out.append(f'<text x="{LW / 2:.0f}" y="{y0 + h / 2 + 7:.0f}" font-size="19" font-weight="700" fill="{color[1]}" text-anchor="middle">{name}</text>')
        for t, x0, x1, end, label in placed:
            by = y0 + 8 + t * TRACK
            c = TRIP if end == "TRIP" else GOAL if end == "GOAL" else color
            if end == "GOAL":
                goals.append(x0)
            body.append(f'<rect x="{x0 + 4}" y="{by}" width="{x1 - x0 - 8:.0f}" height="{BAR}" '
                        f'rx="{BAR // 2 if end in (None, "TRIP", "GOAL") else 7}" fill="{c[0]}"/>')
            xs = [x0 + 14]
            if end not in (None, "TRIP", "GOAL"):   # 長い棒は、年が変わる所でも名前を出す（横に送っても読めるように）
                tw = text_w(label, FS)
                for i in range(1, MONTHS):
                    jx = LW + i * MW
                    if (START[1] - 1 + i) % 12 == 0 and xs[-1] + tw + 60 < jx and jx + tw + 30 < x1:
                        xs.append(jx + 14)
            for tx in xs:
                body.append(f'<text x="{tx}" y="{by + BAR / 2 + FS * 0.36:.0f}" font-size="{FS}" fill="{c[1]}"'
                            + (' font-weight="700"' if end in ("TRIP", "GOAL") else "") + f'>{escape(label)}</text>')
    for x in goals:   # 会社を作る・支所を開く月は、縦の線で全部の行に示す
        out.append(f'<line x1="{x + 2}" y1="{top}" x2="{x + 2}" y2="{bottom}" stroke="{GOAL[0]}" stroke-width="3" stroke-dasharray="6 5"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}" '
            f'font-family="{FONT}">' + "".join(out + body) + "</svg>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "7-timeline.svg").write_text(timeline(), encoding="utf-8")
    print("site/board-img/7-timeline.svg")


if __name__ == "__main__":
    main()
