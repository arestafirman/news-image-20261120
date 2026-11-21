#!/usr/bin/env python3
"""Render the one-image front page for Friday 20 November 2026.

Deterministic broadsheet poster (1024x1024) drawn with Pillow from the
verified story list in the build notes: 56 stories (13 drawn features +
43 one-line briefs), 7 regions whose counts sum to 56, six big verified
numbers, a UTC timeline, a dotted world map with numbered pins, and a
DATE CHECK box. No network, no clock, no randomness: the same input
always writes the same PNG bytes.

Usage: python3 generate_image.py [output-path]
Default output is entry.png next to this file.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 24                      # side margin
CW = W - 2 * MX              # content width: 976

PAPER = (246, 240, 220)      # newsprint cream
PAPER_DK = (238, 230, 205)
INK = (26, 26, 26)
RED = (179, 35, 27)
RED_DK = (140, 24, 18)
BLUE = (31, 78, 121)
GREY = (90, 86, 76)
RULE = (60, 56, 48)
SEA = (214, 226, 222)
LAND = (226, 211, 170)
LAND_LINE = (190, 172, 122)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if (serif and bold) else \
        "DejaVuSerif.ttf" if serif else \
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, lines, fnt, fill=INK, leading=None, align="left",
               box_w=None):
    """Draw lines of text; returns the y just below the last line."""
    lead = leading if leading is not None else int(fnt.size * 1.18)
    for ln in lines:
        if align == "center" and box_w is not None:
            lx = x + (box_w - d.textlength(ln, font=fnt)) / 2
        elif align == "right" and box_w is not None:
            lx = x + box_w - d.textlength(ln, font=fnt)
        else:
            lx = x
        d.text((lx, y), ln, font=fnt, fill=fill)
        y += lead
    return y


def rule(d, x0, x1, y, width=1, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def fit_lines(d, text, fnt, max_w, max_lines):
    """Wrap text, trimming the last line with an ellipsis if it overflows."""
    lines = wrap(d, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "…", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    y = 16
    d.text((MX, y), "THE WORLD IN ONE DAY", font=font(15, bold=True), fill=RED)
    right = "56 STORIES  ·  7 REGIONS  ·  13 DRAWN"
    d.text((W - MX - d.textlength(right, font=font(11, bold=True)), y + 3),
           right, font=font(11, bold=True), fill=INK)
    y = 38
    head = "FRIDAY 20 NOVEMBER 2026"
    hf = font(41, bold=True, serif=True)
    d.text(((W - d.textlength(head, font=hf)) / 2, y), head, font=hf, fill=INK)
    y = 86
    sub1 = ("Russian missiles hit Kyiv's bridges  ·  Cyclone Akvan comes ashore  ·  "
            "AI sell-off sinks Asia's markets")
    sub2 = "UK and EU seal a reset deal  ·  COP31 ends its last day with no deal"
    sf = font(13, bold=True)
    d.text(((W - d.textlength(sub1, font=sf)) / 2, y), sub1, font=sf, fill=INK)
    d.text(((W - d.textlength(sub2, font=sf)) / 2, y + 17), sub2, font=sf, fill=INK)
    rule(d, MX, W - MX, 118, width=2)


# ---------------------------------------------------------------- UTC strip
UTC_SLOTS = [
    ("02:30", "Akvan landfall near Gopalpur; Poland air alert"),
    ("05:00", "New Zealand 368 all out in Wellington"),
    ("05:30", "Taiex closes down 6.2% in Taipei"),
    ("08:00", "Kenya switches on Turkana oil drilling"),
    ("12:00", "COP31 draft drops the words “fossil fuels”"),
    ("15:00", "COP31 runs past its Friday close — no deal"),
    ("21:00", "S&P 500 ends down 3.7%, in correction"),
]


def draw_utc(d):
    y = 124
    d.text((MX, y), "THE DAY IN UTC", font=font(10, bold=True), fill=RED)
    slot_w = CW / 7
    for i, (t, ev) in enumerate(UTC_SLOTS):
        x = MX + i * slot_w + (6 if i else 0)
        d.text((x, y + 14), t, font=font(11, bold=True), fill=RED)
        text_block(d, x, y + 28, fit_lines(d, ev, font(8.5), slot_w - 12, 3),
                   font(8.5), leading=10)
        if i:
            d.line([(MX + i * slot_w - 3, y + 14), (MX + i * slot_w - 3, y + 56)],
                   fill=(200, 192, 168), width=1)
    rule(d, MX, W - MX, 186, width=1)


# ---------------------------------------------------------------- big numbers
BIG_NUMBERS = [
    ("3", "Kyiv bridges hit over the Dnipro"),
    ("300,000+", "people moved to shelters before Cyclone Akvan"),
    ("−6.2%", "Taiwan's Taiex at Friday's close"),
    ("100,000", "youth visas a year each way in the UK–EU deal"),
    ("2.3%", "Japan consumer inflation in October"),
    ("60.7%", "tumours respond in the pancreatic pill trial"),
]


def draw_numbers(d):
    y = 194
    col_w = CW / 6
    nf = font(27, bold=True, serif=True)
    lf = font(9)
    for i, (num, label) in enumerate(BIG_NUMBERS):
        x = MX + i * col_w
        cx = x + col_w / 2
        d.text((cx - d.textlength(num, font=nf) / 2, y), num, font=nf,
               fill=RED if i % 2 == 0 else INK)
        text_block(d, x + 6, y + 34,
                   fit_lines(d, label, lf, col_w - 12, 3), lf, leading=10.5,
                   align="center", box_w=col_w - 12)
        if i:
            d.line([(x - 3, y + 2), (x - 3, y + 58)], fill=(200, 192, 168), width=1)
    rule(d, MX, W - MX, 254, width=2)


# ---------------------------------------------------------------- region strip
REGIONS = [  # (label, count) — counts sum to 56
    ("EUROPE", 12, (36, 66, 94)),
    ("ASIA", 9, (156, 43, 37)),
    ("MIDDLE EAST", 6, (91, 58, 110)),
    ("AFRICA", 8, (122, 92, 20)),
    ("AMERICAS", 10, (47, 93, 58)),
    ("OCEANIA", 4, (15, 95, 107)),
    ("GLOBAL", 7, (68, 68, 68)),
]


def draw_regions(d):
    y = 260
    x = MX
    total = sum(c for _, c, _ in REGIONS)
    rf = font(10, bold=True)
    for label, count, colour in REGIONS:
        w_ = CW * count / total
        d.rectangle([x, y, x + w_ - 1, y + 22], fill=colour)
        txt = "%s · %d" % (label, count)
        d.text((x + (w_ - d.textlength(txt, font=rf)) / 2, y + 5), txt,
               font=rf, fill=(255, 255, 255))
        x += w_
    rule(d, MX, W - MX, 290, width=1)


# ---------------------------------------------------------------- illustrations
def panel_frame(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_ - 1, y + h_ - 1], outline=RULE, width=1)


def ribbon(d, x, y, w_, label):
    """Red label ribbon across the top of an illustration."""
    rf = font(10, bold=True)
    tw = d.textlength(label, font=rf) + 14
    d.polygon([(x, y), (x + tw, y), (x + tw - 8, y + 15), (x, y + 15)], fill=RED)
    d.text((x + 7, y + 2), label, font=rf, fill=(255, 255, 255))


def caption(d, x, y, w_, text_):
    """Small source caption inside the bottom of an illustration."""
    cf = font(8)
    tw = d.textlength(text_, font=cf) + 10
    d.rectangle([x + w_ - tw, y - 13, x + w_ - 1, y - 1], fill=(0, 0, 0))
    d.text((x + w_ - tw + 5, y - 12), text_, font=cf, fill=(255, 255, 255))


def draw_kyiv(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(16, 24, 48))
    for sx, sy in [(28, 18), (90, 8), (150, 22), (210, 10), (260, 26), (300, 14)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 200))
    # skyline
    for bx, bw, bh in [(0, 34, 34), (40, 26, 48), (72, 40, 30), (118, 30, 52),
                       (154, 36, 38), (196, 28, 46), (230, 34, 30), (270, 40, 44)]:
        d.rectangle([x + bx, y + h_ - 26 - bh, x + bx + bw, y + h_ - 26],
                    fill=(8, 12, 26))
        for wy in range(y + h_ - 22 - bh, y + h_ - 30, 8):
            for wx in range(x + bx + 5, x + bx + bw - 4, 9):
                d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 214, 110))
    # river
    d.rectangle([x, y + h_ - 26, x + w_, y + h_], fill=(38, 68, 110))
    for rx in range(6, w_, 26):
        d.line([(x + rx, y + h_ - 12), (x + rx + 12, y + h_ - 12)],
               fill=(120, 160, 200), width=1)
    # bridge arches
    for ax in (40, 130, 220):
        d.arc([x + ax, y + h_ - 52, x + ax + 70, y + h_ - 8], 180, 360,
              fill=(255, 170, 60), width=3)
        d.line([(x + ax, y + h_ - 30), (x + ax + 70, y + h_ - 30)],
               fill=(255, 170, 60), width=2)
    # missile trails and bursts
    for mx, my, mdx in [(60, 10, 26), (180, 4, -20), (250, 16, -30)]:
        d.line([(x + mx, y + my), (x + mx + mdx, y + my + 26)],
               fill=(255, 200, 90), width=2)
        for bx_, by_, r_ in [(mx + mdx, my + 26, 7), (mx + mdx, my + 26, 3)]:
            d.ellipse([x + bx_ - r_, y + by_ - r_, x + bx_ + r_, y + by_ + r_],
                      fill=(255, 140, 40) if r_ > 4 else (255, 230, 150))
    ribbon(d, x, y, w_, "KYIV — NIGHT STRIKE")
    caption(d, x, y + h_, w_, "Officials' count")


def draw_cyclone(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(206, 226, 228))
    # coastline (east India) and land
    d.polygon([(x + 150, y), (x + w_, y), (x + w_, y + h_), (x + 120, y + h_),
               (x + 128, y + 78), (x + 150, y + 34)], fill=(233, 220, 180))
    d.line([(x + 150, y), (x + 150, y + 34), (x + 128, y + 78), (x + 120, y + h_)],
           fill=(120, 110, 80), width=2)
    # spiral bands
    cx, cy = x + 118, y + 62
    for r_, col in [(46, (30, 110, 150)), (36, (60, 140, 170)),
                    (26, (90, 170, 190)), (16, (30, 110, 150))]:
        d.arc([cx - r_, cy - r_, cx + r_, cy + r_], 20, 300, fill=col, width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(179, 35, 27))
    # rain streaks
    for rx in range(10, w_ - 10, 18):
        d.line([(x + rx, y + 8), (x + rx - 5, y + 22)], fill=(120, 150, 170), width=1)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(255, 255, 255), width=2)
    ribbon(d, x, y, w_, "CYCLONE AKVAN")
    caption(d, x, y + h_, w_, "Weather office")


def draw_markets(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(255, 255, 255))
    for gy in range(y + 16, y + h_ - 8, 18):
        d.line([(x + 8, gy), (x + w_ - 8, gy)], fill=(232, 232, 232), width=1)
    pts = [(x + 14, y + 28), (x + 60, y + 36), (x + 105, y + 32),
           (x + 150, y + 54), (x + 195, y + 62), (x + 240, y + 82),
           (x + 285, y + 90)]
    d.line(pts, fill=RED, width=3)
    for i in range(len(pts) - 1):
        bx = pts[i][0]
        d.rectangle([bx, pts[i][1], bx + 16, y + h_ - 6],
                    fill=(240, 120, 110) if i > 2 else (200, 200, 200))
    d.text((x + 12, y + 18), "TAIEX  −6.2%   ·   KOSPI  −5.2%   ·   NIKKEI  −5.1%",
           font=font(10, bold=True), fill=RED)
    ribbon(d, x, y, w_, "AI SELL-OFF")
    caption(d, x, y + h_, w_, "Closing prices")


def draw_flag_uk(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(1, 33, 105))
    d.polygon([(x, y), (x + 12, y), (x + w_ - 12, y + h_), (x + w_ - 24, y + h_)],
              fill=(255, 255, 255))
    d.polygon([(x + w_, y), (x + w_ - 12, y), (x + 24, y + h_), (x + 12, y + h_)],
              fill=(255, 255, 255))
    d.rectangle([x + w_ / 2 - 4, y, x + w_ / 2 + 4, y + h_], fill=(255, 255, 255))
    d.rectangle([x, y + h_ / 2 - 4, x + w_, y + h_ / 2 + 4], fill=(255, 255, 255))
    d.rectangle([x + w_ / 2 - 2, y, x + w_ / 2 + 2, y + h_], fill=(200, 16, 46))
    d.rectangle([x, y + h_ / 2 - 2, x + w_, y + h_ / 2 + 2], fill=(200, 16, 46))


def draw_flag_eu(d, x, y, w_, h_):
    import math
    d.rectangle([x, y, x + w_, y + h_], fill=(0, 51, 153))
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        sx = x + w_ / 2 + math.cos(a) * w_ * 0.30
        sy = y + h_ / 2 + math.sin(a) * h_ * 0.30
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 204, 0))


def draw_ukeu(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(240, 234, 214))
    draw_flag_uk(d, x + 22, y + 10, 62, 34)
    draw_flag_eu(d, x + w_ - 84, y + 10, 62, 34)
    d.line([(x + 84, y + 27), (x + w_ - 84, y + 27)], fill=RED, width=2)
    d.polygon([(x + w_ / 2 - 5, y + 22), (x + w_ / 2 + 5, y + 27),
               (x + w_ / 2 - 5, y + 32)], fill=RED)
    ribbon(d, x, y, w_, "UK–EU DEAL")


def draw_cop31(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(30, 80, 70))
    cols = [(179, 35, 27), (255, 204, 0), (31, 78, 121), (255, 255, 255),
            (47, 93, 58), (200, 120, 40), (91, 58, 110)]
    for i, c in enumerate(cols):
        fx = x + 12 + i * 24
        d.rectangle([fx, y + 8, fx + 18, y + 24], fill=c)
        d.line([(fx + 9, y + 24), (fx + 9, y + 34)], fill=(200, 200, 200), width=1)
    d.rectangle([x + 14, y + 34, x + 112, y + 46], fill=(240, 234, 214))
    d.text((x + 18, y + 36), "COP31 — NO DEAL", font=font(9, bold=True),
           fill=RED_DK)
    ribbon(d, x, y, w_, "CLIMATE TALKS")


def draw_poland(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(226, 232, 228))
    d.polygon([(x + 30, y + 8), (x + 90, y + 6), (x + 150, y + 14),
               (x + 160, y + 30), (x + 120, y + 46), (x + 70, y + 48),
               (x + 40, y + 34)], fill=(246, 240, 220),
              outline=(120, 110, 90))
    d.ellipse([x + 118, y + 26, x + 126, y + 34], fill=RED)
    d.text((x + 130, y + 22), "LUBLIN", font=font(8, bold=True), fill=RED)
    d.polygon([(x + 14, y + 14), (x + 34, y + 18), (x + 14, y + 22)], fill=INK)
    d.line([(x + 34, y + 18), (x + 60, y + 20)], fill=INK, width=1)
    ribbon(d, x, y, w_, "MISSILE IN POLAND")


def draw_iraq(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(232, 206, 150))
    d.ellipse([x + w_ - 40, y + 6, x + w_ - 16, y + 30], fill=(240, 180, 60))
    d.rectangle([x, y + 34, x + w_, y + h_], fill=(200, 164, 110))
    for tx in (30, 90):
        d.rectangle([x + tx, y + 30, x + tx + 42, y + 42], fill=(90, 90, 80))
        d.rectangle([x + tx + 6, y + 24, x + tx + 30, y + 30], fill=(110, 110, 95))
        d.ellipse([x + tx + 6, y + 42, x + tx + 14, y + 50], fill=INK)
        d.ellipse([x + tx + 28, y + 42, x + tx + 36, y + 50], fill=INK)
    ribbon(d, x, y, w_, "JURF AL-SAKHAR")


def draw_italy(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(238, 228, 200))
    for ax in (20, 62, 104):
        d.arc([x + ax, y + 22, x + ax + 34, y + 50], 180, 360,
              fill=(150, 100, 60), width=3)
        d.line([(x + ax, y + 36), (x + ax + 34, y + 36)], fill=(150, 100, 60),
               width=2)
    d.rectangle([x, y + 50, x + w_, y + h_], fill=(200, 180, 140))
    for px, pl in [(150, "NO"), (170, "24H")]:
        d.line([(x + px, y + 12), (x + px, y + 40)], fill=INK, width=2)
        d.rectangle([x + px - 8, y + 6, x + px + 8, y + 16], fill=(255, 255, 255),
                    outline=INK)
        d.text((x + px - 6, y + 8), pl, font=font(7, bold=True), fill=INK)
    ribbon(d, x, y, w_, "GENERAL STRIKE")


def draw_japan(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(255, 255, 255))
    d.polygon([(x + 12, y + h_ - 6), (x + 26, y + 8), (x + 40, y + h_ - 6)],
              outline=RED, width=2)
    d.line([(x + 26, y + 8), (x + 26, y + h_ - 6)], fill=RED, width=2)
    d.text((x + 52, y + 4), "¥ 2.3%", font=font(20, bold=True, serif=True), fill=INK)
    d.line([(x + 52, y + 34), (x + 90, y + 30), (x + 130, y + 40),
            (x + 168, y + 30)], fill=RED, width=2)
    d.polygon([(x + 168, y + 30), (x + 160, y + 30), (x + 168, y + 38)], fill=RED)
    ribbon(d, x, y, w_, "INFLATION 2.3%")


def draw_seoul(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(232, 228, 214))
    d.polygon([(x + 50, y + 6), (x + 136, y + 6), (x + 93, y + 20)], fill=(90, 80, 60))
    for cx in (58, 82, 106, 130):
        d.rectangle([x + cx, y + 20, x + cx + 8, y + 44], fill=(120, 110, 90))
    d.rectangle([x + 46, y + 44, x + w_ - 46, y + 50], fill=(90, 80, 60))
    d.rectangle([x + 148, y + 30, x + 168, y + 34], fill=(120, 80, 40))
    d.line([(x + 158, y + 34), (x + 158, y + 44)], fill=(120, 80, 40), width=3)
    ribbon(d, x, y, w_, "TOP JUDGE")


def draw_kenya(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(250, 214, 130))
    d.ellipse([x + w_ - 44, y + 4, x + w_ - 16, y + 32], fill=(240, 160, 40))
    d.polygon([(x + 30, y + h_ - 4), (x + 52, y + 10), (x + 74, y + h_ - 4)],
              fill=INK)
    for ly in range(y + 18, y + h_ - 8, 8):
        t = (ly - y) / h_
        lx0 = x + 30 + (52 - 30) * t
        lx1 = x + 74 - (74 - 52) * t
        d.line([(lx0, ly), (lx1, ly)], fill=(250, 214, 130), width=1)
    d.rectangle([x + 110, y + 26, x + 150, y + 34], fill=INK)
    d.line([(x + 110, y + 26), (x + 96, y + 14)], fill=INK, width=3)
    d.line([(x + 150, y + 26), (x + 164, y + 14)], fill=INK, width=3)
    ribbon(d, x, y, w_, "FIRST OIL WELL")


def draw_bukele(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(226, 232, 240))
    d.rectangle([x + 56, y + 22, x + 130, y + 48], fill=(0, 51, 153))
    d.rectangle([x + 76, y + 18, x + 110, y + 22], fill=INK)
    d.rectangle([x + 84, y + 6, x + 102, y + 18], fill=(255, 255, 255), outline=INK)
    d.text((x + 88, y + 8), "✓", font=font(10, bold=True), fill=RED)
    d.text((x + w_ - 62, y + 4), "3rd TERM", font=font(11, bold=True), fill=INK)
    ribbon(d, x, y, w_, "THIRD TERM BID")


def draw_cricket(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=(120, 170, 90))
    d.rectangle([x + 60, y + 8, x + 126, y + h_ - 6], fill=(210, 190, 140))
    for sx in (88, 94, 100):
        d.line([(x + sx, y + 12), (x + sx, y + 26)], fill=(255, 220, 60), width=2)
    d.rectangle([x + 130, y + 20, x + 136, y + 44], fill=(140, 90, 40))
    d.ellipse([x + 150, y + 40, x + 158, y + 48], fill=RED)
    d.text((x + 10, y + 30), "368", font=font(16, bold=True, serif=True),
           fill=(255, 255, 255))
    ribbon(d, x, y, w_, "TEST CRICKET")


# ---------------------------------------------------------------- feature panels
# (n, city, field, tag, title, body, source, draw function)
FEATURES = [
    (1, "KYIV", "WAR", "REPORTED",
     "Russian missiles hit three Kyiv bridges",
     "100+ missiles and 400+ drones fired overnight; power and water cut in "
     "the capital; at least nine killed across Ukraine.",
     "Kyiv Independent, BBC", draw_kyiv),
    (2, "ODISHA", "CYCLONE", "OFFICIAL",
     "Cyclone Akvan comes ashore in eastern India",
     "300,000+ moved to shelters; 423 rescue teams out; winds 70–80 km/h "
     "near Gopalpur.",
     "IMD, PTI", draw_cyclone),
    (3, "MARKETS", "ASIA", "CONFIRMED",
     "AI sell-off sinks Asia's stock markets",
     "Taiex −6.2%, Kospi −5.2%, Nikkei −5.1%; SoftBank −14.5% in its worst "
     "day since Aug 2024.",
     "CNBC market data", draw_markets),
    (4, "BRUSSELS", "DIPLOMACY", "CONFIRMED",
     "UK and EU seal a “reset” deal",
     "Youth mobility: 100,000 places a year each way, ages 18–31.",
     "BBC, EU Council", draw_ukeu),
    (5, "ANTALYA", "CLIMATE", "REPORTED",
     "COP31 reaches its last day with no deal",
     "Final draft drops “fossil fuels” and the $120bn adaptation figure.",
     "UN News, Reuters", draw_cop31),
    (6, "POLAND", "SECURITY", "REPORTED",
     "Russian missile lands in Poland",
     "Kh-101 found near Lublin; Polish and NATO jets scrambled; no casualties.",
     "Reuters", draw_poland),
    (7, "IRAQ", "SECURITY", "REPORTED",
     "Iraqi army enters a militia stronghold",
     "Troops move into Jurf al-Sakhar under a compromise deal with "
     "Kataib Hezbollah.",
     "Reuters, France 24", draw_iraq),
    (8, "ROME", "LABOUR", "REPORTED",
     "General strike over Italy's budget",
     "CGIL's 24-hour stoppage hits transport in about 100 cities.",
     "AFP, AP", draw_italy),
    (9, "TOKYO", "ECONOMY", "OFFICIAL",
     "Japan's inflation picks up to 2.3%",
     "October CPI 2.3% (core 2.2%); yen near 159 per dollar.",
     "Reuters", draw_japan),
    (10, "SEOUL", "POLITICS", "REPORTED",
     "Korea's ruling party to impeach top judge",
     "Move against Chief Justice Cho Hee-dae deepens political tensions.",
     "Korea Herald", draw_seoul),
    (11, "TURKANA", "ENERGY", "OFFICIAL",
     "Kenya starts drilling its first oil well",
     "Amosing 1 spudded 14 years after the 2012 discovery; first oil due 1 Dec.",
     "TV47, The Standard", draw_kenya),
    (12, "SAN SALVADOR", "POLITICS", "REPORTED",
     "Bukele files to run for a third term",
     "Re-election bid lodged with the electoral tribunal; vote 28 Feb 2027.",
     "AP, Al Jazeera", draw_bukele),
    (13, "WELLINGTON", "SPORT", "CONFIRMED",
     "Phillips hits 118 as New Zealand make 368",
     "Nicholls 175*; India 159/1 at stumps on day two of the first Test.",
     "NZ Herald, Reuters", draw_cricket),
]


def draw_feature(d, f, x, y, w_, img_h, hero):
    n, city, field, tag, title, body, src, art = f
    art(d, x, y, w_, img_h)
    panel_frame(d, x, y, w_, img_h)
    if not hero:
        caption(d, x, y + img_h, w_, src.split(",")[0])
    ty = y + img_h + 6
    kf = font(10 if hero else 8, bold=True)
    tag_f = font(8 if hero else 7.5, bold=True)
    d.text((x, ty), "%d %s · %s" % (n, city, field), font=kf, fill=INK)
    tag_txt = "[%s]" % tag
    d.text((x + w_ - d.textlength(tag_txt, font=tag_f), ty + 1), tag_txt,
           font=tag_f, fill=RED)
    ty += 11
    tf = font(13.5 if hero else 10.5, bold=True)
    ty = text_block(d, x, ty, fit_lines(d, title, tf, w_, 2), tf,
                    leading=15 if hero else 11)
    bf = font(10 if hero else 9)
    ty = text_block(d, x, ty + 1, fit_lines(d, body, bf, w_, 2 if hero else 2),
                    bf, leading=11 if hero else 9.5)
    if hero:
        d.text((x, ty + 1), "(%s)" % src, font=font(8), fill=GREY)


def draw_features(d):
    # hero row: 3 panels
    gap = 11
    hw = (CW - 2 * gap) // 3
    for i, f in enumerate(FEATURES[:3]):
        draw_feature(d, f, MX + i * (hw + gap), 296, hw, 100, hero=True)
    # two small rows of 5
    sw = (CW - 4 * gap) // 5
    for row, feats in enumerate((FEATURES[3:8], FEATURES[8:13])):
        y0 = 480 if row == 0 else 594
        for i, f in enumerate(feats):
            draw_feature(d, f, MX + i * (sw + gap), y0, sw, 52, hero=False)


# ---------------------------------------------------------------- world map
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-80, 73),
     (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 38),
     (-80, 32), (-81, 26), (-90, 21), (-97, 16), (-94, 17), (-87, 13),
     (-83, 9), (-79, 9), (-92, 15), (-105, 20), (-110, 23), (-117, 33),
     (-125, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 60)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-70, -52), (-66, -55),
     (-65, -45), (-62, -40), (-58, -35), (-52, -32), (-48, -28), (-41, -23),
     (-35, -9), (-35, -6), (-44, -3), (-50, 0), (-55, 5), (-60, 8), (-70, 11),
     (-75, 10)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5),
     (13, -10), (12, -17), (15, -27), (18, -33), (20, -35), (26, -34),
     (32, -29), (35, -24), (40, -16), (40, -10), (42, -4), (46, 0), (51, 2),
     (51, 10), (48, 11), (44, 11), (40, 15), (38, 18), (37, 22), (35, 28),
     (32, 31), (30, 31), (22, 33), (11, 34), (10, 37), (5, 37), (-1, 35)],
    # Eurasia
    [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-1, 50), (2, 51),
     (5, 53), (8, 55), (8, 57), (10, 59), (18, 56), (21, 55), (24, 58),
     (24, 60), (30, 60), (30, 66), (40, 68), (50, 69), (60, 69), (68, 73),
     (75, 73), (80, 73), (90, 75), (100, 77), (110, 74), (120, 73), (130, 72),
     (140, 72), (150, 70), (160, 70), (170, 67), (178, 65), (178, 62),
     (170, 60), (162, 56), (158, 52), (150, 59), (142, 54), (141, 50),
     (140, 45), (135, 43), (130, 42), (127, 40), (126, 38), (122, 38),
     (120, 35), (122, 32), (120, 28), (118, 25), (110, 21), (108, 18),
     (105, 10), (104, 9), (100, 8), (98, 10), (97, 16), (94, 17), (92, 21),
     (89, 22), (86, 20), (84, 19), (80, 15), (80, 13), (77, 8), (75, 12),
     (72, 20), (70, 21), (66, 25), (62, 25), (58, 25), (56, 26), (54, 26),
     (52, 28), (50, 29), (48, 30), (48, 29), (50, 26), (52, 25), (54, 24),
     (57, 26), (59, 22), (58, 20), (55, 17), (52, 15), (48, 14), (44, 13),
     (43, 12), (40, 15), (39, 21), (38, 24), (36, 29), (35, 31), (34, 28),
     (33, 31), (30, 36), (27, 37), (26, 38), (23, 36), (22, 37), (20, 40),
     (19, 42), (15, 44), (12, 45), (8, 44), (7, 44), (3, 43), (0, 40),
     (-2, 37), (-6, 36)],
    # Australia
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (140, -17), (136, -15), (135, -12), (132, -12), (130, -13), (126, -14),
     (122, -17), (118, -20)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (133, 34), (136, 35), (139, 36), (140, 38), (141, 41),
     (142, 44), (144, 44), (141, 40), (140, 36), (137, 34), (133, 33)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -40), (177, -38), (178, -37),
     (175, -38), (173, -40), (170, -42)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25),
     (43, -22), (43, -18)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76),
     (-35, 77), (-50, 76), (-55, 74), (-58, 70), (-55, 66), (-52, 62),
     (-48, 60)],
    # Sumatra, Borneo, New Guinea
    [(95, 5), (100, 0), (104, -4), (106, -6), (102, -2), (97, 3)],
    [(109, 1), (113, 4), (117, 6), (119, 2), (117, -2), (113, -3), (110, -2)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
     (142, -8), (136, -6), (132, -4)],
]

# (number, lon, lat, nudge dx, nudge dy) — nudges keep the crowded
# Europe / Middle East pins from overlapping each other.
PINS = [
    (1, 30.5, 50.4, 16, -12), (2, 84.9, 19.3, 0, -10),
    (3, 121.5, 25.0, 9, -3), (4, 30.7, 36.9, 14, 8),
    (5, 4.35, 50.85, -18, -8), (6, 22.6, 51.2, -4, 13),
    (7, 44.2, 32.9, 18, 12), (8, 12.5, 41.9, -15, 8),
    (9, 139.7, 35.7, 7, -9), (10, 127.0, 37.5, -9, -7),
    (11, 36.0, 3.0, 9, 3), (12, -89.2, 13.7, -7, -9),
    (13, 174.8, -41.3, -5, 9),
]


def draw_map(d, x, y, w_, h_):
    d.rectangle([x, y, x + w_, y + h_], fill=SEA)
    d.rectangle([x, y, x + w_, y + h_], outline=RULE, width=1)

    def proj(lon, lat):
        px = x + (lon + 180) / 360 * w_
        py = y + (78 - lat) / 136 * h_
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=LAND_LINE)
    pf = font(7.5, bold=True)
    for n, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        lx, ly = px + dx, py + dy
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        if abs(dx) + abs(dy) > 2:
            d.line([(px, py), (lx, ly)], fill=RED, width=1)
        d.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(n)
        d.text((lx - d.textlength(t, font=pf) / 2, ly - 5), t, font=pf,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- briefs
BRIEFS = [
    (14, "Lviv: Russian strike on railway station kills two (BBC)"),
    (15, "Smolensk: Ukraine drones hit Dorogobuzh chemical plant (Kyiv Ind.)"),
    (16, "Kryvyi Rih: two dead, 42 hurt in strike, incl. four children"),
    (17, "Copenhagen: MPs approve Greenland defence deal with US (AP)"),
    (18, "Berlin: Merz rejects a “new Yalta” deal on Europe's future"),
    (19, "Tallinn: Estonia to shut Russia road border on 1 Dec (Reuters)"),
    (20, "Copenhagen: Denmark expels Russian attaché in 'rapper plot'"),
    (21, "London: UK pledges 1,000 drones, £260m for Ukraine (BBC)"),
    (22, "Taipei: ~2,700 China-linked accounts flagged over polls"),
    (23, "Tokyo: Japan to study nuclear-powered submarines (Yonhap)"),
    (24, "Dhaka: fresh arson attacks; 124 held amid Hasina tension"),
    (25, "Ulaanbaatar: Mongolia's president resigns"),
    (26, "Riyadh: Houthi missiles hit capital; PIF Tower damaged"),
    (27, "Hormuz: tanker ablaze off Oman; UKMTO warning 214-26"),
    (28, "Gaza: Israeli troops cross Yellow Line; strikes kill 6"),
    (29, "Yemen: coalition strikes Hodeidah; missiles downed (Al Jaz.)"),
    (30, "Washington: Pentagon puts Iran war cost at $48.3bn"),
    (31, "Washington: Senate blocks Iran war-powers bid, 51–48"),
    (32, "California: state subpoenas Nvidia over chips for China"),
    (33, "New York: S&P 500 −3.7% to 6,910, in correction (Nasdaq −5.3%)"),
    (34, "New York: Anthropic falls 8.5% a day after Nasdaq debut"),
    (35, "Washington: Senate passes energy permitting bill, 62–33"),
    (36, "Port-au-Prince: police say 34 gang suspects killed in raid"),
    (37, "Brasília: Lula advances Indigenous land recognition"),
    (38, "Mexico City: Sheinbaum leads Revolution Day parade"),
    (39, "Central Peru: magnitude 6.7 quake; 20 Nov local time (USGS)"),
    (40, "South Kordofan: drone strike kills 10 at a gold mine"),
    (41, "Blantyre: fuel crisis — 20 litres a day, night queues"),
    (42, "Mogadishu: Somalia orders UAE envoy out in 72 hours"),
    (43, "Abuja: Nigeria moves to end jail for attempted suicide"),
    (44, "Yenne, Senegal: migrant boat capsizes; 4 dead, dozens missing"),
    (45, "Horn of Africa: Ethiopia–Eritrea cross-border shelling"),
    (46, "Abidjan: AfDB says 22 African states near debt distress"),
    (47, "Suva: Fiji declares disaster as El Niño drought bites"),
    (48, "South Pacific: Cyclone Xavier, Cat 4, nears Cook Islands"),
    (49, "Bougainville: Rio Tinto pledges $370m Panguna cleanup"),
    (50, "Space: BepiColombo reaches Mercury after eight years (ESA)"),
    (51, "Health: pancreatic pill trial: 60.7% tumours respond"),
    (52, "Culture: GTA VI sells est. $2.36bn on day one, 24.5m copies"),
    (53, "Las Vegas: Russell fastest in wet F1 second practice"),
    (54, "Turin: Zverev beats Fils to reach ATP Finals semi-finals"),
    (55, "Bhopal: India women beat Malaysia 4–1 in hockey opener"),
    (56, "Culture: Fiona the hippo dies at Cincinnati Zoo"),
]


def draw_map_and_briefs(d):
    y0 = 706
    # map column
    d.text((MX, y0), "WHERE IT HAPPENED", font=font(11, bold=True), fill=INK)
    d.text((MX, y0 + 14), "Numbers on the map match the story numbers.",
           font=font(8.5), fill=GREY)
    draw_map(d, MX, y0 + 30, 328, 192)
    # briefs column
    bx = MX + 340
    bw = W - MX - bx
    d.text((bx, y0), "ALSO ON FRIDAY 20 NOVEMBER — 43 MORE STORIES",
           font=font(11, bold=True), fill=INK)
    rule(d, bx, W - MX, y0 + 16, width=1)
    col_w = (bw - 12) / 2
    bf = font(8.5)
    nf = font(8.5, bold=True)
    row_h = 9.3
    for i, (n, txt) in enumerate(BRIEFS):
        col = 0 if i < 22 else 1
        row = i if i < 22 else i - 22
        x = bx + col * (col_w + 12)
        yy = y0 + 22 + row * row_h
        num = "%d " % n
        d.text((x, yy), num, font=nf, fill=RED)
        line = txt
        max_w = col_w - d.textlength(num, font=nf)
        while d.textlength(line, font=bf) > max_w and len(line) > 4:
            line = line[:-1]
        if line != txt:
            line = line.rstrip(" ,;:") + "…"
        d.text((x + d.textlength(num, font=nf), yy), line, font=bf, fill=INK)
    rule(d, MX, W - MX, 934, width=1)


# ---------------------------------------------------------------- date check + footer
def draw_datecheck(d):
    y = 940
    d.rectangle([MX, y, W - MX, y + 50], outline=RED, width=2)
    d.rectangle([MX, y, MX + 108, y + 16], fill=RED)
    d.text((MX + 6, y + 2), "DATE CHECK", font=font(10, bold=True),
           fill=(255, 255, 255))
    f = font(9)
    l1 = ("Left out on purpose — first reported BEFORE Friday: Trump–Xi–Putin "
          "Shenzhen summit + peace declaration (Thu 19 Nov) · ICJ ruling: "
          "Myanmar genocide of the Rohingya (Thu 19 Nov) · Anthropic IPO $83, "
          "debut +17% (Thu 19 Nov) · Van Gogh sale $190.4m (Wed 18 Nov) · "
          "Voyager 1 one-light-day mark (Wed 18 Nov) · GTA VI launch (Thu 19 Nov) "
          "— only Friday's day-one sales are used.")
    l2 = ("Not yet: BepiColombo's Mercury orbit entry (Sat 21 Nov) · any final "
          "COP31 deal · ATP Finals final (Sun 22 Nov) · Kenya's first oil (1 Dec).")
    text_block(d, MX + 6, y + 19, fit_lines(d, l1, f, CW - 12, 2), f, leading=11)
    d.text((MX + 6, y + 41), l2, font=f, fill=INK)


def draw_footer(d):
    f = font(8.5)
    l1 = "Every story here happened, or was first reported, on Friday 20 November 2026."
    l2 = ("Sources: AP · Reuters · AFP · BBC · Al Jazeera · Kyiv Independent · IMD · "
          "PTI · UN News · EU Council · California DOJ · USGS · NZ Herald · TV47 · "
          "Fiji Met · UKMTO · CNBC.  Original drawings — no photographs.")
    d.text(((W - d.textlength(l1, font=f)) / 2, 996), l1, font=f, fill=INK)
    d.text(((W - d.textlength(l2, font=f)) / 2, 1006), l2, font=f, fill=INK)


# ---------------------------------------------------------------- main
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Deterministic newsprint grain (fixed seed): a light speckle over the
    # paper before anything is drawn on it, so the sheet reads as printed
    # paper rather than flat colour. Same seed, same bytes, every run.
    import random
    rng = random.Random(20261120)
    for _ in range(34000):
        gx, gy = rng.randrange(W), rng.randrange(H)
        dv = rng.randrange(-7, 8)
        d.point((gx, gy), fill=(PAPER[0] + dv, PAPER[1] + dv, PAPER[2] + dv))
    d.rectangle([8, 8, W - 9, H - 9], outline=RULE, width=1)
    draw_masthead(d)
    draw_utc(d)
    draw_numbers(d)
    draw_regions(d)
    draw_features(d)
    draw_map_and_briefs(d)
    draw_datecheck(d)
    draw_footer(d)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, format="PNG", optimize=True)
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
