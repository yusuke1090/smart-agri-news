#!/usr/bin/env python3
"""牛の教科書（site/cow/）の図・グラフを SVG で作る。

    python3 tools/make_cow_figures.py          # site/cow/images/ に書き出す

日本語と英語の両方の章で同じ図を使うので、文字は「日本語 / English」を並べて書く。
グラフの数値は、教科書の本文に書いた目安から作った「イメージ」（実測のデータではない）。
色は、色覚のちがいでも見分けられる組み合わせ（dataviz の検証ずみ）を、決まった順番で使う。
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "site" / "cow" / "images"
FONT = "system-ui, 'Noto Sans JP', 'Hiragino Sans', sans-serif"

TEXT, TEXT2, MUTED, GRID, AXIS = "#1f1f1d", "#52514e", "#8a8984", "#e6e5e0", "#9a9a95"
S1, S2, S3, S4, S5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"   # 検証ずみの順番
RED = "#e34948"                     # しきい値（注意）にだけ使う
WATER = "#d9d8d3"                   # 「水分」のような、目立たせないもの
INK, SKIN, PINK, SOFT = "#2b2b2b", "#ffffff", "#f4c3cb", "#f3f4f6"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size=12, anchor="start", fill=TEXT2, weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{w}{extra}>{esc(s)}</text>'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}" font-size="12">\n'
            f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{TEXT2}"/></marker></defs>\n'
            f'<rect width="{w}" height="{h}" rx="10" fill="#ffffff"/>\n' + "\n".join(body) + "\n</svg>\n")


class Plot:
    """1本の縦軸・1本の横軸の座標を、数値から画面の位置に変える"""

    def __init__(self, x0, y0, x1, y1, xmin, xmax, ymin, ymax):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax

    def X(self, v):
        return self.x0 + (v - self.xmin) / (self.xmax - self.xmin) * (self.x1 - self.x0)

    def Y(self, v):
        return self.y1 - (v - self.ymin) / (self.ymax - self.ymin) * (self.y1 - self.y0)

    def grid(self, yticks, xticks, ylabel=None, xlabel=None, yfmt=str):
        b = []
        for v in yticks:
            y = self.Y(v)
            b.append(f'<path d="M{self.x0} {y:.1f} H{self.x1}" stroke="{GRID}" stroke-width="1"/>')
            b.append(t(self.x0 - 8, y + 4, yfmt(v), 11, "end", MUTED))
        b.append(f'<path d="M{self.x0} {self.y1} H{self.x1}" stroke="{AXIS}" stroke-width="1.5"/>')
        for v, lab in xticks:
            x = self.X(v)
            b.append(f'<path d="M{x:.1f} {self.y1} v5" stroke="{AXIS}" stroke-width="1"/>')
            b.append(t(x, self.y1 + 18, lab, 11, "middle", MUTED))
        if ylabel:
            b.append(t(self.x0 - 8, self.y0 - 14, ylabel, 11.5, "start", TEXT2, extra=' dx="-40"'))
        if xlabel:
            b.append(t((self.x0 + self.x1) / 2, self.y1 + 38, xlabel, 11.5, "middle", TEXT2))
        return b

    def line(self, pts, color, width=2, dash=None):
        d = "M" + " L".join(f"{self.X(a):.1f} {self.Y(b):.1f}" for a, b in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{da}/>'


def smooth(f, a, b, n=120):
    return [(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)]


# ---------------------------------------------------------------------------
# 牛の絵（左向き。見えているのは牛の左側）
def cow(dx=0, dy=0, collar=True):
    g = [f'<g transform="translate({dx} {dy})" stroke="{INK}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">']
    # 脚（奥の脚を先に、少し灰色で）
    for x in (296, 590):
        g.append(f'<path d="M{x} 250 L{x+2} 352" stroke-width="16" stroke="#c9c9c4"/>')
    g.append(f'<path d="M262 240 L262 352" stroke-width="18" stroke="{INK}"/><path d="M262 240 L262 346" stroke-width="13" stroke="{SKIN}"/>')
    g.append(f'<path d="M612 236 Q 624 290 612 352" fill="none" stroke-width="18" stroke="{INK}"/>'
             f'<path d="M612 236 Q 624 290 612 346" fill="none" stroke-width="13" stroke="{SKIN}"/>')
    for x in (262, 612):
        g.append(f'<rect x="{x-10}" y="346" width="20" height="12" rx="3" fill="{INK}" stroke="none"/>')
    for x in (296, 592):
        g.append(f'<rect x="{x-8}" y="348" width="17" height="10" rx="3" fill="#8f8f8a" stroke="none"/>')
    # 胴
    g.append('<path d="M250 132 Q 262 106 330 104 L 560 100 Q 622 98 640 126 Q 656 160 648 206 Q 640 250 606 262 '
             'L 520 266 Q 470 270 420 268 L 300 262 Q 256 258 248 226 Z" fill="#ffffff"/>')
    # 黒い模様（ホルスタイン）
    g.append(f'<path d="M352 106 Q 400 100 438 112 Q 452 150 418 176 Q 380 190 352 168 Q 336 140 352 106 Z" fill="{INK}" stroke="none"/>')
    g.append(f'<path d="M488 170 Q 540 150 590 172 Q 604 210 570 232 Q 520 246 494 222 Q 474 196 488 170 Z" fill="{INK}" stroke="none"/>')
    g.append(f'<path d="M560 102 Q 610 100 632 122 Q 628 146 600 150 Q 566 146 560 102 Z" fill="{INK}" stroke="none"/>')
    # 乳房と乳頭
    g.append(f'<path d="M508 262 Q 500 300 530 308 Q 568 314 586 294 Q 596 276 588 258" fill="{PINK}"/>')
    for x in (528, 566):
        g.append(f'<path d="M{x} 306 L{x} 322" stroke-width="5" stroke="{PINK}"/><path d="M{x} 306 L{x} 322" stroke-width="1.5" fill="none"/>')
    # 尾
    g.append('<path d="M640 120 Q 664 150 660 230 Q 658 270 660 300" fill="none" stroke-width="3"/>')
    g.append(f'<path d="M654 296 Q 660 322 668 300 Q 664 290 654 296 Z" fill="{INK}"/>')
    # 首と頭
    g.append('<path d="M256 132 Q 230 128 206 140 L 196 146" fill="none"/><path d="M250 226 Q 226 222 206 206" fill="none"/>')
    g.append('<path d="M212 142 Q 178 132 148 150 Q 118 168 108 200 Q 102 224 120 234 Q 142 242 164 230 Q 192 214 214 204 Q 226 178 212 142 Z" fill="#ffffff"/>')
    g.append(f'<path d="M212 142 Q 196 136 182 140 Q 186 166 210 176 Q 222 166 212 142 Z" fill="{INK}" stroke="none"/>')
    g.append(f'<path d="M110 206 Q 104 226 120 234 Q 138 240 150 230 Q 138 214 110 206 Z" fill="{PINK}"/>')
    g.append(f'<circle cx="150" cy="178" r="3.5" fill="{INK}" stroke="none"/>')
    g.append('<path d="M200 142 Q 214 122 236 120 Q 230 140 208 150 Z" fill="#ffffff"/>')       # 耳
    g.append(f'<rect x="219" y="124" width="10" height="13" rx="2" fill="{S4}" stroke-width="1.5"/>')  # 耳標
    if collar:
        g.append(f'<path d="M232 128 Q 222 176 230 226" fill="none" stroke="{S1}" stroke-width="9"/>')
        g.append(f'<rect x="222" y="214" width="18" height="16" rx="3" fill="{S1}" stroke="{INK}" stroke-width="1.5"/>')
    g.append("</g>")
    return g


def callout(x, y, tx, ty, lines, anchor="start", color=TEXT2):
    """(x, y) の点から、文字の場所 (tx, ty) まで線を引いて説明を書く"""
    b = [f'<circle cx="{x}" cy="{y}" r="3.5" fill="{color}"/>',
         f'<path d="M{x} {y} L{tx} {ty}" stroke="{color}" stroke-width="1.2" fill="none"/>']
    off = 6 if anchor == "start" else -6
    for i, (s, size, w) in enumerate(lines):
        b.append(t(tx + off, ty + 4 + i * 15, s, size, anchor, TEXT if w else TEXT2, w))
    return b


def fig_cow_parts():
    b = cow(40, 20)
    b += callout(265, 150, 160, 60, [("耳標（個体識別番号）", 12.5, 700), ("ear tag (ID number)", 11, None)], "end")
    b += callout(268, 205, 176, 300, [("首輪（センサーを付ける所）", 12.5, 700), ("collar (for sensors)", 11, None)], "end")
    b += f'<ellipse cx="428" cy="214" rx="82" ry="44" fill="none" stroke="{S3}" stroke-width="2.5" stroke-dasharray="6 4"/>',
    b.append('<rect x="350" y="195" width="156" height="38" rx="6" fill="#ffffff" opacity="0.92"/>')
    b += [t(428, 210, "第一胃（お腹の左側）", 12.5, "middle", TEXT, 700), t(428, 226, "rumen (left side)", 11, "middle", TEXT2)]
    b += callout(560, 322, 470, 384, [("乳房と乳頭", 12.5, 700), ("udder and teats", 11, None)], "end")
    b += callout(658, 372, 740, 336, [("蹄", 12.5, 700), ("hoof", 11, None)])
    b += callout(680, 140, 724, 70, [("尾の付け根", 12.5, 700), ("tail head", 11, None)])
    b.append(f'<path d="M318 120 V378" stroke="{TEXT2}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    b.append(f'<path d="M318 124 V374" stroke="{TEXT2}" stroke-width="1.2" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    b += [t(328, 318, "体高（肩の高さ）", 12, "start", TEXT, 700), t(328, 334, "約150 cm / height ~150 cm", 11, "start", TEXT2),
          t(30, 395, "体重 600〜700 kg", 12, "start", TEXT, 700), t(30, 410, "weight 600–700 kg", 11, "start", TEXT2)]
    b.append(f'<path d="M{40+90} 378 H{40+700}" stroke="{AXIS}" stroke-width="1.5"/>')
    return svg(820, 420, b)


def fig_sensors():
    b = cow(40, 30)
    b.append(f'<ellipse cx="392" cy="262" rx="34" ry="20" fill="none" stroke="{S2}" stroke-width="2" stroke-dasharray="5 4"/>')
    b.append(f'<rect x="381" y="255" width="22" height="14" rx="7" fill="{S2}" stroke="{INK}" stroke-width="1.2"/>')
    b.append(f'<rect x="291" y="330" width="16" height="22" rx="3" fill="{S3}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<rect x="686" y="150" width="12" height="22" rx="3" fill="{S5}" stroke="{INK}" stroke-width="1.5"/>')
    # 天井のカメラ・壁の環境センサー
    b.append(f'<path d="M560 34 h40 v18 h-40 z M600 40 l14 -6 v24 l-14 -6" fill="{TEXT2}"/>')
    b.append(f'<path d="M580 54 L520 120 M580 54 L660 120" stroke="{TEXT2}" stroke-width="1" stroke-dasharray="4 4"/>')
    b.append(f'<rect x="742" y="40" width="40" height="52" rx="5" fill="#ffffff" stroke="{TEXT2}" stroke-width="1.5"/>')
    b.append(t(762, 62, "℃", 13, "middle", TEXT2, 700) + t(762, 80, "%", 13, "middle", TEXT2, 700))
    b += callout(265, 158, 160, 52, [("① 耳標のセンサー", 12.5, 700), ("ear tag sensor", 11, None)], "end")
    b += callout(268, 232, 176, 120, [("② 首輪（活動量・反芻）", 12.5, 700), ("collar: activity, rumination", 11, None)], "end")
    b += callout(299, 340, 200, 392, [("③ 足の歩数計", 12.5, 700), ("pedometer", 11, None)], "end")
    b += callout(392, 262, 452, 392, [("④ 胃の中のボーラス（体温・飲水）", 12.5, 700), ("rumen bolus: temperature, drinking", 11, None)])
    b += callout(692, 172, 708, 232, [("⑤ 尾・体温", 12.5, 700), ("tail, temp.", 11, None)])
    b += callout(560, 336, 700, 360, [("⑥ 搾乳ロボット", 12.5, 700), ("milking robot", 11, None)])
    b += [t(580, 24, "⑦ カメラと AI / camera + AI", 12.5, "middle", TEXT, 700),
          t(762, 108, "⑧ THI", 12.5, "middle", TEXT, 700), t(762, 123, "climate", 11, "middle", TEXT2)]
    return svg(820, 420, b)


def fig_cow_life():
    p = Plot(70, 40, 790, 200, 0, 72, 0, 1)
    b = []
    stages = [(0, 3, "哺育", "calf", SOFT), (3, 23, "育成牛 / heifer", "", "#eaf2fc"), (23, 62, "経産牛（お産と搾乳をくり返す）/ cow", "", "#e8f6f0")]
    for a, z, lab, en, col in stages:
        b.append(f'<rect x="{p.X(a):.1f}" y="44" width="{p.X(z)-p.X(a)-2:.1f}" height="30" rx="4" fill="{col}"/>')
        b.append(t((p.X(a) + p.X(z)) / 2, 64, lab, 12, "middle", TEXT, 700))
    b.append(t(p.X(1.5), 92, en, 11, "middle", TEXT2))
    # 泌乳と乾乳
    c = 23
    n = 1
    while c + 12 <= 62.5:
        b.append(f'<rect x="{p.X(c):.1f}" y="110" width="{p.X(c+10)-p.X(c)-2:.1f}" height="22" rx="4" fill="{S1}"/>')
        b.append(f'<rect x="{p.X(c+10):.1f}" y="110" width="{p.X(c+12)-p.X(c+10)-2:.1f}" height="22" rx="4" fill="{WATER}"/>')
        b.append(f'<path d="M{p.X(c):.1f} 104 V140" stroke="{TEXT}" stroke-width="2"/>')
        b.append(t(p.X(c), 154, f"{n}産", 11.5, "middle", TEXT, 700))
        c += 12.5
        n += 1
    b.append(f'<path d="M{p.X(14):.1f} 98 V140" stroke="{S2}" stroke-width="2" stroke-dasharray="4 3"/>')
    b.append(t(p.X(14), 154, "初めての授精", 11, "middle", TEXT2) + t(p.X(14), 168, "1st AI 13–15 mo", 10.5, "middle", MUTED))
    b.append(t(p.X(23), 168, "初産 22〜24か月", 10.5, "middle", MUTED))
    b.append(f'<path d="M{p.X(62):.1f} 104 V140" stroke="{TEXT2}" stroke-width="2" stroke-dasharray="4 3"/>')
    b.append(t(p.X(62), 154, "牧場を離れる", 11, "middle", TEXT2) + t(p.X(62), 168, "leaves the farm", 10.5, "middle", MUTED))
    for yr in range(7):
        x = p.X(yr * 12)
        b.append(f'<path d="M{x:.1f} 186 v6" stroke="{AXIS}"/>')
        b.append(t(x, 208, f"{yr}歳", 11, "middle", MUTED))
    b.append(f'<path d="M{p.X(0)} 186 H{p.X(72)}" stroke="{AXIS}" stroke-width="1.5"/>')
    b.append(t(p.X(36), 228, "年齢 / age (years)", 11.5, "middle", TEXT2))
    # 凡例
    lx = 470
    b.append(f'<rect x="{lx}" y="240" width="14" height="12" rx="3" fill="{S1}"/>' + t(lx + 20, 250, "乳を搾る（約10か月）/ milking", 11.5, "start", TEXT2))
    b.append(f'<rect x="{lx}" y="258" width="14" height="12" rx="3" fill="{WATER}"/>' + t(lx + 20, 268, "乾乳（約2か月）/ dry period", 11.5, "start", TEXT2))
    return svg(820, 282, b)


def fig_rumen_ph():
    p = Plot(80, 50, 760, 280, 0, 24, 5.0, 7.0)
    b = p.grid([5.0, 5.5, 6.0, 6.5, 7.0], [(h, f"{h}時") for h in range(0, 25, 3)], "pH", "時刻 / time of day", lambda v: f"{v:.1f}")
    b.append(f'<rect x="{p.x0}" y="{p.Y(5.8):.1f}" width="{p.x1-p.x0}" height="{p.Y(5.0)-p.Y(5.8):.1f}" fill="{RED}" opacity="0.07"/>')
    b.append(p.line([(0, 5.8), (24, 5.8)], RED, 1.5, "6 4"))
    b.append(t(p.x0 + 6, p.Y(5.8) - 6, "SARA の目安 5.8 / SARA line", 11, "start", RED, 700))

    def dip(tt, meals, depth, width):
        return sum(depth * math.exp(-((tt - (m + 2.5)) / width) ** 2) for m in meals)
    tmr = smooth(lambda x: 6.45 - dip(x, [6, 18], 0.38, 2.6) - 0.06 * math.sin(x / 24 * 6.28), 0, 24)
    big = smooth(lambda x: 6.55 - dip(x, [6, 17], 1.05, 1.9), 0, 24)
    b.append(p.line(tmr, S1, 2.5))
    b.append(p.line(big, S2, 2.5))
    for m in (6, 17):
        b.append(f'<path d="M{p.X(m):.1f} {p.y1-2} l-6 -10 h12 z" fill="{TEXT2}"/>')
    b.append(t(p.X(6), p.y1 - 16, "エサ", 10.5, "middle", TEXT2) + t(p.X(17), p.y1 - 16, "エサ", 10.5, "middle", TEXT2))
    b.append(t(p.X(3.6), p.Y(6.86), "TMR（全部まぜて、いつでも食べる）", 12, "start", TEXT, 700))
    b.append(t(p.X(3.6), p.Y(6.86) + 15, "TMR: everything mixed", 11, "start", TEXT2))
    b.append(t(p.X(10.2), p.Y(5.42), "濃厚飼料を一度にたくさん", 12, "start", TEXT, 700))
    b.append(t(p.X(10.2), p.Y(5.42) + 15, "a big meal of concentrate", 11, "start", TEXT2))
    b.append(f'<path d="M{p.X(10.1):.1f} {p.Y(5.45):.1f} L{p.X(9.1):.1f} {p.Y(5.55):.1f}" stroke="{S2}" stroke-width="1.5"/>')
    b.append(f'<path d="M{p.X(8.3):.1f} {p.Y(6.7):.1f} L{p.X(8.5):.1f} {p.Y(6.1):.1f}" stroke="{S1}" stroke-width="1.5"/>')
    b += legend(300, 22, [(S1, "TMR"), (S2, "濃厚飼料をまとめて / big concentrate meals")])
    b.append(t(p.x0, p.y1 + 58, "※ 本文の目安から作ったイメージ / illustration based on typical values", 10.5, "start", MUTED))
    return svg(820, 352, b)


def legend(x, y, items):
    b = []
    for col, lab in items:
        b.append(f'<path d="M{x} {y} h18" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        b.append(t(x + 24, y + 4, lab, 11.5, "start", TEXT2))
        x += 30 + len(lab) * 7.2
    return b


def fig_heat_activity():
    p = Plot(80, 50, 770, 270, 0, 63, 0, 14000)
    b = p.grid([0, 3000, 6000, 9000, 12000], [(d, f"{d}") for d in range(0, 64, 7)], "1日の歩数 / steps per day", "日 / day", lambda v: f"{v:,}")
    base = 3400
    heat = {10: 10300, 31: 9800, 52: 10900}
    pre = {9: 5200, 30: 4800, 51: 5600, 11: 4300, 32: 4100, 53: 4500}
    w = (p.x1 - p.x0) / 64
    for d in range(64):
        v = heat.get(d) or pre.get(d) or base + 420 * math.sin(d * 1.7) + 260 * math.cos(d * 0.9)
        x = p.X(d) - w * 0.35
        h = p.Y(0) - p.Y(v)
        b.append(f'<rect x="{x:.1f}" y="{p.Y(v):.1f}" width="{w*0.7:.1f}" height="{h:.1f}" rx="1.5" fill="{S1 if d not in heat else S2}"/>')
    b.append(p.line([(0, base * 2), (63, base * 2)], TEXT2, 1.2, "5 4"))
    b.append(t(p.x0 + 6, p.Y(base * 2) - 6, "ふだんの2倍 / 2× normal", 11, "start", TEXT2))
    for d, v in heat.items():
        b.append(t(p.X(d), p.Y(v) - 8, "発情 / heat", 11.5, "middle", TEXT, 700))
    for a, z in ((10, 31), (31, 52)):
        y = p.Y(12900)
        b.append(f'<path d="M{p.X(a)+8:.1f} {y:.1f} H{p.X(z)-8:.1f}" stroke="{TEXT2}" stroke-width="1.2" marker-start="url(#ah)" marker-end="url(#ah)"/>')
        b.append(t((p.X(a) + p.X(z)) / 2, y - 6, "21日 / 21 days", 11.5, "middle", TEXT2, 700))
    b.append(t(p.x0, p.y1 + 58, "※ 首輪や歩数計のデータのイメージ / illustration of collar or pedometer data", 10.5, "start", MUTED))
    return svg(820, 342, b)


def fig_colostrum():
    p = Plot(80, 40, 770, 250, 0, 24, 0, 100)
    b = [f'<rect x="{p.X(0):.1f}" y="{p.y0}" width="{p.X(2)-p.X(0):.1f}" height="{p.y1-p.y0}" fill="{S3}" opacity="0.18"/>',
         f'<rect x="{p.X(2):.1f}" y="{p.y0}" width="{p.X(6)-p.X(2):.1f}" height="{p.y1-p.y0}" fill="{S4}" opacity="0.14"/>']
    b += p.grid([0, 25, 50, 75, 100], [(h, f"{h}") for h in (0, 2, 6, 12, 18, 24)], "抗体を吸収できる力（生まれた直後 = 100）/ ability to absorb antibodies", "生まれてからの時間（時間）/ hours after birth")
    b.append(p.line(smooth(lambda h: 100 * (1 - h / 24) ** 1.25, 0, 24), S1, 2.5))
    b.append(t(p.X(1), p.y1 - 26, "2時間", 12, "middle", TEXT, 700) + t(p.X(1), p.y1 - 11, "以内に", 11, "middle", TEXT2))
    b.append(t(p.X(4), p.y1 - 26, "遅くとも6時間", 12, "middle", TEXT, 700) + t(p.X(4), p.y1 - 11, "6 h at the latest", 11, "middle", TEXT2))
    b.append(t(p.X(13), p.Y(52), "時間がたつほど吸収できなくなる", 12, "start", TEXT, 700))
    b.append(t(p.X(13), p.Y(52) + 15, "absorption falls every hour", 11, "start", TEXT2))
    b.append(t(p.X(21), p.Y(30), "24時間ほどで", 11, "middle", TEXT2) + t(p.X(21), p.Y(30) + 14, "ほぼ吸収しない", 11, "middle", TEXT2))
    b.append(t(p.x0, p.y1 + 58, "※ 本文の目安から作ったイメージ / illustration", 10.5, "start", MUTED))
    return svg(820, 322, b)


def fig_dry_matter():
    rows = [("乾草", "hay", 1.2), ("配合飼料", "compound feed", 1.3), ("コーンサイレージ", "corn silage", 6.5), ("生草（放牧の草）", "fresh grass", 8.0)]
    p = Plot(200, 60, 760, 250, 0, 10, 0, 1)
    b = [t(p.x0, 34, "エサ 10 kg の中身 / what is inside 10 kg of feed", 13, "start", TEXT, 700)]
    for v in range(0, 11, 2):
        x = p.X(v)
        b.append(f'<path d="M{x:.1f} 56 V{p.y1}" stroke="{GRID}"/>' + t(x, p.y1 + 18, f"{v} kg", 11, "middle", MUTED))
    bh, gap = 30, 14
    for i, (ja, en, water) in enumerate(rows):
        y = 64 + i * (bh + gap)
        dm = 10 - water
        b.append(t(p.x0 - 12, y + 14, ja, 12.5, "end", TEXT, 700) + t(p.x0 - 12, y + 28, en, 11, "end", TEXT2))
        xd = p.X(dm)
        b.append(f'<rect x="{p.x0}" y="{y}" width="{xd-p.x0-1:.1f}" height="{bh}" rx="4" fill="{S1}"/>')
        b.append(f'<rect x="{xd+1:.1f}" y="{y}" width="{p.X(10)-xd-1:.1f}" height="{bh}" rx="4" fill="{WATER}"/>')
        b.append(t((p.x0 + xd) / 2, y + 20, f"乾物 {dm:.1f} kg", 12, "middle", "#ffffff", 700) if dm > 1.5 else t(xd - 6, y + 20, f"{dm:.1f} kg", 12, "end", "#ffffff", 700))
        b.append(t((xd + p.X(10)) / 2, y + 20, f"水分 {water:.1f} kg", 12, "middle", TEXT, 700) if water > 2 else t(xd + 8, y + 20, f"{water:.1f} kg", 12, "start", TEXT, 700))
    b.append(f'<rect x="{p.x0}" y="{p.y1+30}" width="14" height="12" rx="3" fill="{S1}"/>' + t(p.x0 + 20, p.y1 + 40, "乾物（栄養がある所）/ dry matter", 11.5, "start", TEXT2))
    b.append(f'<rect x="{p.x0+260}" y="{p.y1+30}" width="14" height="12" rx="3" fill="{WATER}"/>' + t(p.x0 + 280, p.y1 + 40, "水分 / water", 11.5, "start", TEXT2))
    return svg(820, 306, b)


def fig_timothy_alfalfa():
    b = []
    panels = [("粗たんぱく質 / crude protein (%)", 25, [5, 10, 15, 20, 25], [(8, 12), (17, 22)], "%"),
              ("カルシウム / calcium (%)", 1.6, [0.4, 0.8, 1.2, 1.6], [(0.3, 0.5), (1.2, 1.5)], "%")]
    for k, (title, top, ticks, ranges, unit) in enumerate(panels):
        x0 = 90 + k * 380
        p = Plot(x0, 60, x0 + 290, 250, 0, 1, 0, top)
        b.append(t(x0 - 40, 36, title, 13, "start", TEXT, 700))
        for v in [0] + ticks:
            y = p.Y(v)
            b.append(f'<path d="M{x0} {y:.1f} H{x0+290}" stroke="{GRID if v else AXIS}" stroke-width="{1 if v else 1.5}"/>')
            b.append(t(x0 - 8, y + 4, f"{v:g}", 11, "end", MUTED))
        for j, ((lo, hi), col, ja, en) in enumerate(zip(ranges, (S3, S1), ("チモシー", "アルファルファ"), ("timothy", "alfalfa"))):
            cx = x0 + 80 + j * 130
            mid = (lo + hi) / 2
            y = p.Y(mid)
            b.append(f'<path d="M{cx-26} {p.Y(0):.1f} V{y+4:.1f} q0 -4 4 -4 h44 q4 0 4 4 V{p.Y(0):.1f} z" fill="{col}"/>')
            b.append(f'<path d="M{cx} {p.Y(lo):.1f} V{p.Y(hi):.1f} M{cx-8} {p.Y(lo):.1f} h16 M{cx-8} {p.Y(hi):.1f} h16" stroke="{TEXT}" stroke-width="1.5"/>')
            b.append(t(cx, p.Y(hi) - 8, f"{lo:g}〜{hi:g}{unit}", 12, "middle", TEXT, 700))
            b.append(t(cx, p.y1 + 20, ja, 12.5, "middle", TEXT, 700) + t(cx, p.y1 + 35, en, 11, "middle", TEXT2))
    b.append(t(410, 312, "棒は真ん中の値、細い線は幅（目安）/ bars show the middle, lines show the range", 10.5, "middle", MUTED))
    return svg(820, 326, b)


def fig_cutting_time():
    stages = ["若い草\nyoung", "穂が出る前\nboot", "出穂・開花始め\nheading / early bloom", "開花\nbloom", "実が熟す\nmature"]
    p = Plot(90, 50, 760, 250, 0, 4, 0, 100)
    b = [f'<rect x="{p.X(1.6):.1f}" y="{p.y0}" width="{p.X(2.4)-p.X(1.6):.1f}" height="{p.y1-p.y0}" fill="{S3}" opacity="0.15"/>']
    b += p.grid([0, 25, 50, 75, 100], [], "いちばん高い所を 100 とした値 / relative value (max = 100)")
    for i, s in enumerate(stages):
        ja, en = s.split("\n")
        b.append(f'<path d="M{p.X(i):.1f} {p.y1} v5" stroke="{AXIS}"/>')
        b.append(t(p.X(i), p.y1 + 18, ja, 11.5, "middle", TEXT2) + t(p.X(i), p.y1 + 32, en, 10.5, "middle", MUTED))
    yld = [(0, 30), (1, 55), (2, 80), (3, 94), (4, 100)]
    qual = [(0, 100), (1, 88), (2, 72), (3, 55), (4, 40)]
    b.append(p.line(yld, S1, 2.5))
    b.append(p.line(qual, S2, 2.5))
    for (a, v) in yld:
        b.append(f'<circle cx="{p.X(a):.1f}" cy="{p.Y(v):.1f}" r="4.5" fill="{S1}" stroke="#ffffff" stroke-width="2"/>')
    for (a, v) in qual:
        b.append(f'<circle cx="{p.X(a):.1f}" cy="{p.Y(v):.1f}" r="4.5" fill="{S2}" stroke="#ffffff" stroke-width="2"/>')
    b.append(t(p.X(0.12), p.Y(18), "とれる量 / yield", 12, "start", TEXT, 700))
    b.append(t(p.X(0.12), p.Y(80), "栄養・消化のよさ / quality", 12, "start", TEXT, 700))
    b.append(t(p.X(2), p.y0 + 14, "刈りどき / best time to cut", 12, "middle", TEXT, 700))
    b += legend(470, 24, [(S1, "とれる量 / yield"), (S2, "栄養 / quality")])
    return svg(820, 310, b)


def fig_silage_ph():
    p = Plot(80, 60, 770, 270, 0, 42, 3.5, 6.5)
    b = []
    for a, z, lab, en in ((0, 1, "①", ""), (1, 21, "② 乳酸発酵", "lactic acid fermentation"), (21, 42, "③ 安定", "stable")):
        b.append(f'<rect x="{p.X(a):.1f}" y="{p.y0}" width="{p.X(z)-p.X(a)-1:.1f}" height="{p.y1-p.y0}" fill="{SOFT if a != 1 else "#eef7f2"}"/>')
        b.append(t((p.X(a) + p.X(z)) / 2, p.y0 - 18, lab, 11.5, "middle", TEXT, 700) + t((p.X(a) + p.X(z)) / 2, p.y0 - 5, en, 10.5, "middle", MUTED))
    b += p.grid([3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5], [(d, f"{d}") for d in (0, 7, 14, 21, 28, 35, 42)], "pH", "詰めてからの日数 / days after sealing", lambda v: f"{v:.1f}")
    b.append(t(p.X(0.5), p.y0 - 32, "① 酸素を使い切る / oxygen used up", 10.5, "start", MUTED))
    b.append(p.line([(0, 4.2), (42, 4.2)], RED, 1.5, "6 4"))
    b.append(t(p.X(22), p.Y(4.2) - 6, "目安 4.2 以下 / target ≤ 4.2", 11, "start", RED, 700, extra=' dy="22"'))
    corn = smooth(lambda d: 3.9 + 2.1 * math.exp(-d / 2.6), 0, 42)
    grass = smooth(lambda d: 4.15 + 2.05 * math.exp(-d / 6.5), 0, 42)
    b.append(p.line(corn, S1, 2.5))
    b.append(p.line(grass, S2, 2.5))
    b.append(t(p.X(30), p.Y(3.9) + 18, "コーンサイレージ / corn silage", 12, "middle", TEXT, 700))
    b.append(t(p.X(13), p.Y(4.9), "グラスサイレージ / grass silage", 12, "start", TEXT, 700))
    b.append(f'<path d="M{p.X(12.8):.1f} {p.Y(4.9)-4:.1f} L{p.X(9.5):.1f} {p.Y(4.62):.1f}" stroke="{S2}" stroke-width="1.5"/>')
    b += legend(470, 24, [(S1, "コーン / corn"), (S2, "牧草 / grass")])
    b.append(t(p.x0, p.y1 + 58, "※ 本文の目安から作ったイメージ / illustration", 10.5, "start", MUTED))
    return svg(820, 342, b)


def fig_milk_composition():
    parts = [("乳糖", "lactose", 5, "約4.6%", S1), ("乳脂肪", "milk fat", 4, "約3.9%", S2), ("たんぱく質", "protein", 3, "約3.3%", S3),
             ("ミネラル", "minerals", 1, "約0.7%", S4), ("水分", "water", 87, "約87%", WATER)]
    b = [t(40, 34, "牛乳 100 g の中身（1マス = 1 g）/ what is in 100 g of milk (1 square = 1 g)", 13, "start", TEXT, 700)]
    cells = []
    for ja, en, n, pct, col in parts:
        cells += [col] * n
    size, gap, x0, y0 = 26, 3, 40, 52
    for i, col in enumerate(cells):
        r, c = divmod(i, 10)
        b.append(f'<rect x="{x0 + c*(size+gap)}" y="{y0 + r*(size+gap)}" width="{size}" height="{size}" rx="4" fill="{col}"/>')
    lx, ly = 370, 70
    for ja, en, n, pct, col in parts:
        b.append(f'<rect x="{lx}" y="{ly-12}" width="16" height="16" rx="4" fill="{col}"/>')
        b.append(t(lx + 26, ly + 1, f"{ja}  {pct}", 13, "start", TEXT, 700) + t(lx + 26, ly + 16, en, 11, "start", TEXT2))
        ly += 40
    b.append(t(lx, ly + 6, "水分以外（約13%）を乳固形分、そこから乳脂肪を", 12, "start", TEXT2))
    b.append(t(lx, ly + 22, "除いたもの（約8.7%）を無脂乳固形分（SNF）という", 12, "start", TEXT2))
    b.append(t(lx, ly + 42, "Solids ≈ 13%. Solids minus fat ≈ 8.7% = SNF", 11, "start", MUTED))
    return svg(820, 352, b)


def fig_letdown():
    p = Plot(80, 50, 770, 250, 0, 8, 0, 100)
    b = [f'<rect x="{p.X(1):.1f}" y="{p.y0}" width="{p.X(1.5)-p.X(1):.1f}" height="{p.y1-p.y0}" fill="{S3}" opacity="0.2"/>']
    b += p.grid([0, 25, 50, 75, 100], [(m, f"{m}") for m in range(9)], "血液の中のオキシトシン（いちばん多い所 = 100）/ oxytocin in blood", "乳頭を刺激してからの時間（分）/ minutes after stimulating the teats")
    curve = smooth(lambda m: 100 * (m / 1.7) ** 2 * math.exp(2 * (1 - m / 1.7)) if m > 0 else 0, 0, 8)
    b.append(p.line(curve, S1, 2.5))
    b.append(t(p.X(1.55), p.Y(40), "← ミルカーを付ける（60〜90秒後）", 12, "start", TEXT, 700))
    b.append(t(p.X(1.55), p.Y(40) + 15, "attach the unit at 60–90 s", 11, "start", TEXT2))
    b.append(t(p.X(0.05), p.Y(90), "前搾り・拭く", 11.5, "start", TEXT, 700) + t(p.X(0.05), p.Y(90) + 14, "stimulate", 10.5, "start", TEXT2))
    b.append(t(p.X(4.3), p.Y(70), "効き目は数分だけ", 12, "start", TEXT, 700) + t(p.X(4.3), p.Y(70) + 15, "lasts only a few minutes", 11, "start", TEXT2))
    b.append(t(p.x0, p.y1 + 58, "※ イメージ。驚いたり痛かったりすると、アドレナリンで出にくくなる / illustration", 10.5, "start", MUTED))
    return svg(820, 322, b)


def fig_udder():
    b = [t(30, 34, "上から見た乳房 / udder from above", 13, "start", TEXT, 700)]
    # 4つの分房（上から見た図。左が頭のほう）
    x0, y0 = 50, 60
    b.append(f'<rect x="{x0}" y="{y0}" width="230" height="200" rx="60" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<path d="M{x0+115} {y0+6} V{y0+194} M{x0+6} {y0+100} H{x0+224}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    for (cx, cy, ja, en) in ((x0+57, y0+50, "左前", "front left"), (x0+172, y0+50, "左後", "rear left"),
                             (x0+57, y0+150, "右前", "front right"), (x0+172, y0+150, "右後", "rear right")):
        b.append(f'<circle cx="{cx}" cy="{cy+22}" r="9" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>')
        b.append(t(cx, cy - 6, ja, 12.5, "middle", TEXT, 700) + t(cx, cy + 8, en, 10.5, "middle", TEXT2))
    b.append(t(x0 + 115, y0 + 224, "← 頭のほう / head", 11, "middle", TEXT2))
    b.append(t(x0 + 115, y0 + 244, "後ろの分房が乳の約6割 / rear quarters give ~60%", 11.5, "middle", TEXT, 700))
    # 1つの分房の断面
    b.append(t(360, 34, "1つの分房の中（断面）/ inside one quarter", 13, "start", TEXT, 700))
    b.append(f'<path d="M380 60 Q 380 50 400 50 L 600 50 Q 620 50 620 70 Q 622 200 560 236 Q 530 252 520 270 L 516 330 Q 510 346 500 346 Q 490 346 484 330 L 480 270 Q 470 252 440 236 Q 378 200 380 70 Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
    import random
    rnd = random.Random(3)
    for _ in range(46):
        cx, cy = 400 + rnd.random() * 200, 66 + rnd.random() * 74
        b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="#ffffff" stroke="#c2707e" stroke-width="1.5"/>')
    for sx in (420, 460, 500, 540, 580):
        b.append(f'<path d="M{sx} 140 Q {sx} 170 500 196" fill="none" stroke="#c2707e" stroke-width="3"/>')
    b.append(f'<ellipse cx="500" cy="210" rx="44" ry="20" fill="#ffffff" stroke="#c2707e" stroke-width="2"/>')
    b.append(f'<path d="M490 228 L492 318 L508 318 L510 228 Z" fill="#ffffff" stroke="#c2707e" stroke-width="2"/>')
    b.append(f'<rect x="494" y="320" width="12" height="18" fill="#c99a3a" stroke="{INK}" stroke-width="1"/>')
    b += callout(600, 100, 640, 80, [("乳腺胞（乳を作る小さな袋）", 12, 700), ("alveoli (make milk)", 10.5, None)])
    b += callout(560, 160, 640, 140, [("乳管（乳の通り道）", 12, 700), ("milk ducts", 10.5, None)])
    b += callout(540, 210, 640, 200, [("乳腺槽（乳がたまる所）", 12, 700), ("gland cistern", 10.5, None)])
    b += callout(508, 280, 640, 260, [("乳頭槽", 12, 700), ("teat cistern", 10.5, None)])
    b += callout(506, 330, 640, 320, [("乳頭口（栓で閉じる）", 12, 700), ("teat canal (closed by a plug)", 10.5, None)])
    return svg(820, 360, b)


def fig_cmt():
    levels = [("−", "水のよう", "like water", "〜20万", 0), ("±", "少しとろみ", "slightly thick", "20万〜40万", 1),
              ("+", "はっきりゲル", "clear gel", "40万〜120万", 2), ("++", "すぐ固まる", "gels at once", "120万〜500万", 3),
              ("+++", "盛り上がる", "domes up", "500万〜", 4)]
    b = [t(40, 34, "PL テスト（CMT）の見方 / reading the CMT", 13, "start", TEXT, 700)]
    # パドル
    b.append(f'<rect x="40" y="56" width="250" height="214" rx="20" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<rect x="150" y="270" width="30" height="56" rx="8" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
    for (cx, cy, ja, en, lv) in ((102, 104, "左前", "FL", 0), (228, 104, "右前", "FR", 1), (102, 204, "左後", "RL", 3), (228, 204, "右後", "RR", 0)):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{SOFT}" stroke="{INK}" stroke-width="1.5"/>')
        b += blob(cx, cy, lv, 24)
        b.append(t(cx, cy + 50, f"{ja} / {en}", 11, "middle", TEXT2))
    b.append(t(165, 346, "分房ごとに乳と試薬を混ぜる / mix milk + reagent per quarter", 11, "middle", TEXT2))
    # 反応の段階
    x = 330
    b.append(t(x, 66, "反応 / score", 11.5, "start", MUTED) + t(x, 230, "体細胞数の目安（1 mL）/ approx. SCC per mL", 11.5, "start", MUTED))
    for i, (sym, ja, en, scc, lv) in enumerate(levels):
        cx = x + 44 + i * 94
        b.append(f'<circle cx="{cx}" cy="128" r="34" fill="{SOFT}" stroke="{INK}" stroke-width="1.5"/>')
        b += blob(cx, 128, lv, 24)
        b.append(t(cx, 90, sym, 16, "middle", TEXT, 700))
        b.append(t(cx, 182, ja, 12, "middle", TEXT, 700) + t(cx, 197, en, 10.5, "middle", TEXT2))
        b.append(t(cx, 254, scc, 12, "middle", TEXT, 700))
    b.append(f'<path d="M{x+20} 276 H{x+452}" stroke="{TEXT2}" stroke-width="1.5" marker-end="url(#ah)"/>')
    b.append(t(x + 236, 296, "体細胞が多い（乳房炎が重い）ほど、ドロッと固まる / more cells → thicker gel", 11.5, "middle", TEXT2))
    b.append(t(x, 330, "この例では左後の分房が「++」→ 乳房炎が疑われる", 12, "start", TEXT, 700))
    b.append(t(x, 346, "In this example, the rear-left quarter scores ++ → suspect mastitis", 11, "start", TEXT2))
    return svg(820, 362, b)


def blob(cx, cy, lv, r):
    """PL テストのくぼみの中の様子（0: 水のよう 〜 4: 盛り上がる）"""
    col = ["#cfe0f5", "#b9d1ef", "#9ec0ea", "#7fa9e0", "#5f90d4"][lv]
    if lv == 0:
        return [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>']
    pts = []
    for k in range(18):
        a = k / 18 * 6.283
        rr = r * (0.55 + 0.1 * lv) * (1 + 0.08 * lv * math.sin(a * 3 + lv))
        pts.append(f"{cx + rr*math.cos(a):.1f} {cy + rr*math.sin(a):.1f}")
    b = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#e4eef9"/>',
         f'<path d="M{" L".join(pts)} Z" fill="{col}" stroke="#4a78b8" stroke-width="{0.8 + 0.4*lv:.1f}"/>']
    if lv >= 4:
        b.append(f'<ellipse cx="{cx-4}" cy="{cy-5}" rx="7" ry="4" fill="#ffffff" opacity="0.6"/>')
    return b


def fig_mastitis_routes():
    b = []
    cols = [(30, "伝染性 / contagious", S1, [("感染した牛の乳房", "an infected udder"), ("ミルカー・手・タオル", "milking unit, hands, towels"), ("ほかの牛の乳頭", "another cow's teat")],
             "防ぐ: 搾乳の衛生、1頭1枚のタオル、感染した牛は最後に搾る", "Prevent: milking hygiene, 1 towel per cow, milk infected cows last"),
            (420, "環境性 / environmental", S2, [("ふん・敷料・泥", "manure, bedding, mud"), ("寝たときに乳頭の先が触れる", "teat ends touch it when lying"), ("乳頭口から乳房へ", "through the teat canal")],
             "防ぐ: 乾いた清潔な敷料、ポストディッピング、搾乳後は立たせる", "Prevent: dry clean bedding, post-dip, keep cows standing")]
    for x, title, col, steps, pj, pe in cols:
        b.append(f'<rect x="{x}" y="20" width="370" height="36" rx="8" fill="{col}"/>')
        b.append(t(x + 185, 44, title, 14, "middle", "#ffffff", 700))
        for i, (ja, en) in enumerate(steps):
            y = 74 + i * 78
            b.append(f'<rect x="{x+40}" y="{y}" width="290" height="50" rx="8" fill="#ffffff" stroke="{col}" stroke-width="2"/>')
            b.append(t(x + 185, y + 22, ja, 13, "middle", TEXT, 700) + t(x + 185, y + 39, en, 11, "middle", TEXT2))
            if i < 2:
                b.append(f'<path d="M{x+185} {y+52} V{y+74}" stroke="{TEXT2}" stroke-width="2" marker-end="url(#ah)"/>')
        b.append(t(x + 185, 322, pj, 11.5, "middle", TEXT, 700) + t(x + 185, 338, pe, 10.5, "middle", TEXT2))
    return svg(820, 352, b)


def fig_blood_milk():
    b = [t(30, 34, "乳に血が混じるしくみ / how blood gets into milk", 13, "start", TEXT, 700)]
    # 乳腺胞と毛細血管
    b.append(f'<circle cx="190" cy="170" r="92" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<circle cx="190" cy="170" r="50" fill="#ffffff" stroke="#c2707e" stroke-width="10"/>')
    b.append(t(190, 166, "乳", 14, "middle", TEXT, 700) + t(190, 182, "milk", 11, "middle", TEXT2))
    for k in range(10):
        a = k / 10 * 6.283
        x1, y1 = 190 + 70 * math.cos(a), 170 + 70 * math.sin(a)
        x2, y2 = 190 + 86 * math.cos(a + 0.4), 170 + 86 * math.sin(a + 0.4)
        b.append(f'<path d="M{x1:.1f} {y1:.1f} Q {190 + 82*math.cos(a+0.1):.1f} {170 + 82*math.sin(a+0.1):.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{RED}" stroke-width="2.5"/>')
    b.append(f'<path d="M226 132 l10 -6 l-2 10 l8 4 l-10 4 z" fill="{RED}"/>')
    for (dx, dy) in ((210, 150), (200, 160), (218, 162), (206, 172)):
        b.append(f'<circle cx="{dx}" cy="{dy}" r="3.5" fill="{RED}"/>')
    b += callout(236, 128, 300, 62, [("細い血管（毛細血管）が破れる", 12, 700), ("a capillary breaks", 10.5, None)])
    b.append(t(190, 286, "乳腺胞のまわりを細い血管が囲む", 11.5, "middle", TEXT2) + t(190, 301, "capillaries surround the alveoli", 10.5, "middle", MUTED))
    # 原因
    causes = [("① お産の直後（いちばん多い）", "right after calving: udder edema"), ("② 乳房のけが", "injury to the udder"),
              ("③ 搾乳のしかた", "vacuum too high, overmilking"), ("④ 乳房炎", "mastitis"), ("⑤ 血が止まりにくい病気（まれ）", "clotting disorders (rare)")]
    for i, (ja, en) in enumerate(causes):
        y = 100 + i * 44
        b.append(f'<rect x="400" y="{y}" width="290" height="38" rx="7" fill="{"#fdecea" if i == 0 else SOFT}" stroke="{RED if i == 0 else AXIS}" stroke-width="1.5"/>')
        b.append(t(412, y + 17, ja, 12.5, "start", TEXT, 700) + t(412, y + 32, en, 10.5, "start", TEXT2))
    # 試験管
    b.append(f'<path d="M730 70 V250 Q 730 272 750 272 Q 770 272 770 250 V70" fill="#fde3e3" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<path d="M732 226 H768 V250 Q 768 270 750 270 Q 732 270 732 250 Z" fill="{RED}"/>')
    b.append(t(750, 292, "置いておくと", 11, "middle", TEXT2) + t(750, 306, "赤いものが沈む", 11, "middle", TEXT2) + t(750, 320, "red cells sink", 10.5, "middle", MUTED))
    return svg(820, 336, b)


def fig_transition():
    p = Plot(90, 50, 770, 260, -21, 42, 0, 40)
    b = []
    need = [(d, 15 + (0 if d < 0 else 17 * (1 - math.exp(-d / 6)) + 1.5 * d / 42)) for d in [x / 2 for x in range(-42, 85)]]
    eat = [(d, (15 - 3.5 * math.exp(-((d - 0) / 6) ** 2)) if d < 0 else 11.5 + 14 * (1 - math.exp(-d / 22))) for d in [x / 2 for x in range(-42, 85)]]
    poly = [(d, n) for d, n in need if d >= 0] + [(d, e) for d, e in reversed(eat) if d >= 0]
    b.append(f'<path d="M{" L".join(f"{p.X(a):.1f} {p.Y(v):.1f}" for a, v in poly)} Z" fill="{S2}" opacity="0.16"/>')
    b += p.grid([0, 10, 20, 30, 40], [(d, f"{d}") for d in (-21, -14, -7, 0, 7, 14, 21, 28, 35, 42)], "エネルギー（イメージ）/ energy (illustration)", "お産からの日数 / days from calving")
    b.append(f'<path d="M{p.X(0):.1f} {p.y0} V{p.y1}" stroke="{TEXT}" stroke-width="1.5" stroke-dasharray="4 3"/>')
    b.append(t(p.X(0) + 6, p.y0 + 12, "お産 / calving", 12, "start", TEXT, 700))
    b.append(p.line(need, S2, 2.5))
    b.append(p.line(eat, S1, 2.5))
    b.append(t(p.X(30), p.Y(38.5), "乳を作るのに要るエネルギー", 12, "middle", TEXT, 700) + t(p.X(30), p.Y(38.5) + 15, "energy needed for milk", 11, "middle", TEXT2))
    b.append(t(p.X(30), p.Y(16.5), "食べて得るエネルギー", 12, "middle", TEXT, 700) + t(p.X(30), p.Y(16.5) + 15, "energy from feed", 11, "middle", TEXT2))
    b.append(t(p.X(8), p.Y(22), "足りない分", 12, "middle", TEXT, 700) + t(p.X(8), p.Y(22) + 15, "（体の脂肪を使う）", 11, "middle", TEXT2) + t(p.X(8), p.Y(22) + 29, "energy gap", 10.5, "middle", MUTED))
    b.append(t(p.X(-10.5), p.Y(9.5), "お産の前は食べる量が減る", 11.5, "middle", TEXT2) + t(p.X(-10.5), p.Y(9.5) + 14, "cows eat less before calving", 10.5, "middle", MUTED))
    b += legend(440, 24, [(S2, "要る / needed"), (S1, "食べて得る / from feed")])
    return svg(820, 330, b)


def fig_thi():
    temps = list(range(36, 19, -2))
    hums = list(range(30, 91, 10))
    x0, y0, cw, ch = 160, 70, 82, 30
    b = [t(x0 + cw * len(hums) / 2, 36, "湿度（%）/ relative humidity", 12, "middle", TEXT2),
         t(40, y0 - 10, "気温 / temp.", 12, "start", TEXT2)]
    bands = [(68, "#fdf3ea", TEXT), (72, "#f9cfae", TEXT), (80, "#ef8f55", TEXT), (999, "#c4501f", "#ffffff")]
    for j, h in enumerate(hums):
        b.append(t(x0 + j * cw + cw / 2, y0 - 10, f"{h}%", 11.5, "middle", TEXT2, 700))
    for i, tc in enumerate(temps):
        y = y0 + i * ch
        b.append(t(x0 - 12, y + 20, f"{tc}℃", 11.5, "end", TEXT2, 700))
        for j, h in enumerate(hums):
            thi = round(0.8 * tc + h / 100 * (tc - 14.4) + 46.4)
            fill, ink = next((c, k) for lim, c, k in bands if thi < lim)
            b.append(f'<rect x="{x0 + j*cw + 1}" y="{y + 1}" width="{cw-2}" height="{ch-2}" rx="4" fill="{fill}"/>')
            b.append(t(x0 + j * cw + cw / 2, y + 20, f"{thi:.0f}", 12, "middle", ink, 700))
    ly = y0 + len(temps) * ch + 24
    labs = [("68 未満: ふつう", "below 68: OK"), ("68〜71: 影響が出始める", "68–71: effects start"), ("72〜79: 暑熱ストレス", "72–79: heat stress"), ("80 以上: 強いストレス", "80+: severe")]
    for k, ((fill, ink), (ja, en)) in enumerate(zip([(c, k_) for _, c, k_ in bands], labs)):
        x = 40 + k * 195
        b.append(f'<rect x="{x}" y="{ly}" width="16" height="16" rx="4" fill="{fill}" stroke="{AXIS}" stroke-width="0.8"/>')
        b.append(t(x + 22, ly + 12, ja, 12, "start", TEXT, 700) + t(x + 22, ly + 27, en, 10.5, "start", TEXT2))
    b.append(t(40, ly + 52, "THI = 0.8 × 気温 + 湿度/100 × (気温 − 14.4) + 46.4（ますの中の数字が THI）", 11, "start", MUTED))
    return svg(820, ly + 66, b)


def fig_cow_day():
    segs = [("横になって休む", "lying, resting", 12, S1), ("食べる", "eating", 4, S2), ("立つ・歩く", "standing, walking", 4.5, S3),
            ("搾乳・移動", "milking, moving", 3, S4), ("水を飲む", "drinking", 0.5, S5)]
    x0, x1, y = 40, 780, 70
    b = [t(x0, 34, "牛の1日（24時間）の使い方の目安 / a cow's 24 hours (typical)", 13, "start", TEXT, 700)]
    sc = (x1 - x0) / 24
    x = x0
    for ja, en, h, col in segs:
        w = h * sc
        b.append(f'<rect x="{x:.1f}" y="{y}" width="{w-2:.1f}" height="44" rx="4" fill="{col}"/>')
        if h >= 3:
            b.append(t(x + w / 2, y + 20, ja, 12.5, "middle", "#ffffff" if col in (S1, S2) else TEXT, 700))
            b.append(t(x + w / 2, y + 36, f"{h:g}時間 / {h:g} h", 11, "middle", "#ffffff" if col in (S1, S2) else TEXT))
        x += w
    xd = x - 0.5 * sc
    b.append(f'<path d="M{xd+4:.1f} {y+46} L{xd-30:.1f} {y+78}" stroke="{TEXT2}" stroke-width="1.2"/>')
    b.append(t(xd - 34, y + 86, "水を飲む 0.5時間（80〜150 L）", 12, "end", TEXT, 700) + t(xd - 34, y + 101, "drinking 0.5 h (80–150 L)", 11, "end", TEXT2))
    for hh in range(0, 25, 6):
        b.append(f'<path d="M{x0 + hh*sc:.1f} {y+48} v6" stroke="{AXIS}"/>' + t(x0 + hh * sc, y + 68, f"{hh}", 11, "middle", MUTED))
    # 反芻（重なっている）
    ry = y + 130
    b.append(t(x0, ry - 10, "反芻はこのうちの 7〜10時間。多くは横になっている間にする / rumination: 7–10 h, mostly while lying", 12, "start", TEXT, 700))
    b.append(f'<rect x="{x0}" y="{ry}" width="{6.5*sc:.1f}" height="16" rx="4" fill="none" stroke="{S1}" stroke-width="2" stroke-dasharray="5 3"/>')
    b.append(f'<rect x="{x0 + 12*sc + 4*sc:.1f}" y="{ry}" width="{1.5*sc:.1f}" height="16" rx="4" fill="none" stroke="{S3}" stroke-width="2" stroke-dasharray="5 3"/>')
    b.append(t(x0 + 3.25 * sc, ry + 12, "横になって反芻", 11, "middle", TEXT2) + t(x0 + 16.75 * sc, ry + 12, "立って反芻", 11, "middle", TEXT2))
    return svg(820, 236, b)


FIGS = {
    "cow-parts.svg": fig_cow_parts, "cow-life.svg": fig_cow_life, "rumen-ph.svg": fig_rumen_ph,
    "heat-activity.svg": fig_heat_activity, "colostrum.svg": fig_colostrum, "dry-matter.svg": fig_dry_matter,
    "timothy-alfalfa.svg": fig_timothy_alfalfa, "cutting-time.svg": fig_cutting_time, "silage-ph.svg": fig_silage_ph,
    "udder.svg": fig_udder, "milk-composition.svg": fig_milk_composition, "letdown.svg": fig_letdown,
    "cmt.svg": fig_cmt, "mastitis-routes.svg": fig_mastitis_routes, "blood-milk.svg": fig_blood_milk,
    "transition.svg": fig_transition, "thi.svg": fig_thi, "cow-day.svg": fig_cow_day, "sensors.svg": fig_sensors,
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGS.items():
        (OUT / name).write_text(fn(), encoding="utf-8")
    print(f"{len(FIGS)} 枚の図を {OUT} に書き出しました")
