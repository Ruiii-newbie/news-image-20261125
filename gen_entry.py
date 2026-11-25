#!/usr/bin/env python3
"""Render the 25 November 2026 world-news front page as entry.png.

Deterministic: fixed fonts, fixed coordinates, no clock, no randomness,
no network. Run: python3 gen_entry.py  ->  entry.png (1024x1024).

Layout budget (1024 tall): masthead 0-118, lead 148-442, row two
458-708, row three 724-958, footer 958-1010. Text is measured to fit
its slot; nothing is placed by guesswork.
"""

import math
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (16, 16, 16)
PAPER = (251, 248, 239)
GREY = (96, 92, 84)
RED = (178, 34, 34)
GREEN = (16, 118, 60)
NAVY = (23, 58, 94)
TEAL = (14, 108, 108)
ORANGE = (196, 90, 20)
GOLD = (172, 128, 18)
SKY = (214, 228, 236)


def fnt(path, size):
    return ImageFont.truetype(path, size)


def wrap_lines(draw, text, font, width):
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=font) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def block(draw, x, y, text, font, width, leading, fill=INK):
    for line in wrap_lines(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def kick(draw, x, y, text, fill):
    font = fnt(SANS_B, 20)
    draw.text((x, y), text.upper(), font=font, fill=fill)
    return y + 28


def head(draw, x, y, text, size, width, leading, fill=INK):
    return block(draw, x, y, text, fnt(SERIF_B, size), width, leading, fill)


def hline(draw, x0, y, x1, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def chart_art(draw, x, y, w, h):
    """Falling market chart: red line over grey bars, inside the box."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 26, 30))
    # grid
    for i in range(1, 4):
        gy = y + i * h // 4
        draw.line([(x + 8, gy), (x + w - 8, gy)], fill=(52, 56, 62), width=1)
    # bars, descending
    n = 9
    bw = (w - 24) // n
    tops = [0.18, 0.30, 0.26, 0.44, 0.40, 0.58, 0.52, 0.72, 0.84]
    for i, t in enumerate(tops):
        bx = x + 12 + i * bw
        by = y + 14 + int(t * (h - 40))
        draw.rectangle([bx, by, bx + bw - 6, y + h - 14],
                       fill=(70, 76, 84))
    # falling line
    pts = []
    for i, t in enumerate(tops):
        px = x + 12 + i * bw + (bw - 6) // 2
        py = y + 14 + int(t * (h - 40)) - 8
        pts.append((px, py))
    draw.line(pts, fill=(235, 70, 60), width=5, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 120, 105))
    draw.text((x + 14, y + h - 34), "NVDA -6%   MICRON -11%",
              font=fnt(SANS_B, 19), fill=(255, 150, 135))


def rocket_art(draw, x, y, w, h):
    """A small rocket climbing past a gold star field, inside the box."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    for sx, sy, r in [(18, 12, 2), (70, 26, 2), (130, 10, 2), (200, 30, 2),
                      (300, 12, 2), (380, 28, 2), (440, 12, 2),
                      (250, 34, 2), (40, 34, 2), (420, 34, 2)]:
        draw.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                     fill=GOLD)
    cx = x + w // 2
    # flame
    draw.polygon([(cx - 6, y + h - 12), (cx, y + h - 2),
                  (cx + 6, y + h - 12)], fill=(240, 170, 40))
    # body
    draw.polygon([(cx, y + 4), (cx + 8, y + 18), (cx + 8, y + h - 12),
                  (cx - 8, y + h - 12), (cx - 8, y + 18)],
                 fill=(240, 240, 238))
    draw.rectangle([cx - 8, y + 20, cx + 8, y + 26], fill=RED)
    draw.ellipse([cx - 3, y + 12, cx + 3, y + 18], fill=NAVY)
    # fins
    draw.polygon([(cx - 8, y + h - 20), (cx - 16, y + h - 12),
                  (cx - 8, y + h - 12)], fill=RED)
    draw.polygon([(cx + 8, y + h - 20), (cx + 16, y + h - 12),
                  (cx + 8, y + h - 12)], fill=RED)
    # smoke puffs
    for i, r in enumerate([5, 7, 5]):
        px = cx - 14 + i * 14
        draw.ellipse([px - r, y + h - 10 - r, px + r, y + h - 10 + r],
                     fill=(200, 208, 216))


def burst_art(draw, x, y, w, h):
    """A dusk skyline with an orange blast burst, inside the box."""
    draw.rectangle([x, y, x + w, y + h], fill=(38, 34, 40))
    base = y + h - 4
    heights = [18, 28, 22, 34, 26, 16, 30, 20]
    bw = w // len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        draw.rectangle([bx + 2, base - bh, bx + bw - 2, base],
                       fill=(22, 20, 24))
    cx, cy = x + w - 34, y + 16
    for k in range(8):
        ang = k * math.pi / 4
        r = 15 if k % 2 == 0 else 8
        ex = cx + int(r * math.cos(ang))
        ey = cy + int(r * math.sin(ang))
        draw.line([(cx, cy), (ex, ey)], fill=(240, 170, 40), width=3)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 200, 60))
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 240, 170))


def quake_art(draw, x, y, w, h):
    """A seismograph zigzag on paper, inside the box."""
    draw.rectangle([x, y, x + w, y + h], fill=PAPER,
                   outline=(180, 176, 168), width=2)
    mid = y + h // 2 + 4
    draw.text((x + 8, y + 4), "M 5.6", font=fnt(SANS_B, 18), fill=RED)
    pts = [(x + 78, mid)]
    steps = [(20, -4), (16, 6), (14, -12), (12, 14), (10, -16),
             (10, 18), (12, -14), (14, 8), (16, -4), (18, 2)]
    px = x + 78
    for dx, dy in steps:
        px += dx
        pts.append((px, mid + dy))
    pts.append((x + w - 6, mid))
    draw.line(pts, fill=RED, width=3, joint="curve")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 30

    # ---- Masthead (0-118) ----
    d.rectangle([0, 0, W, 118], fill=INK)
    d.text((m, 14), "THE WORLD", font=fnt(SERIF_B, 62), fill=PAPER)
    d.text((W - m - 340, 28), "ONE DAY · ONE IMAGE",
           font=fnt(SANS_B, 22), fill=(200, 190, 160))
    d.text((W - m - 340, 60), "WEDNESDAY 25 NOV 2026",
           font=fnt(SANS, 22), fill=(200, 190, 160))
    hline(d, m, 132, W - m, width=3)

    # ---- Lead: markets sell-off (148-442) ----
    lx, ly = m, 148
    y = kick(d, lx, ly, "Markets · The AI sell-off returns", RED)
    y = head(d, lx, y + 2,
             "A day after Nvidia's 31% surge, the AI trade collapses again",
             36, 580, 44)
    y = block(d, lx, y + 8,
              "Nasdaq -1.5%, S&P 500 -0.5%; Nvidia -6%, Micron -11% "
              "and the chip index -8%. The Dow rose 0.8%. Selling "
              "worsened on a report the Trump administration is "
              "preparing higher tariffs on China, the EU and 14 other "
              "economies.",
              fnt(SANS, 20), 580, 26, fill=GREY)
    chart_art(d, lx + 620, ly + 6, 344, 252)
    d.text((lx + 620, ly + 266), "Wall Street, Tuesday",
           font=fnt(SANS_B, 17), fill=GREY)
    hline(d, m, 442, W - m, width=2)

    # ---- Row two: Shenzhou-24 + Gaza (458-708) ----
    ry = 458
    half = (W - 2 * m - 24) // 2
    # Shenzhou, left
    x = m
    y = kick(d, x, ry, "Space · Jiuquan, China", NAVY)
    y = head(d, x, y + 2, "China launches Shenzhou-24 — first Pakistani in orbit",
             28, half, 34)
    y = block(d, x, y + 6,
              "Muhammad Zeeshan Ali, a Pakistan Air Force pilot, flies "
              "to Tiangong — the first foreign astronaut aboard it. "
              "A week in orbit.",
              fnt(SANS, 20), half, 26, fill=GREY)
    rocket_art(d, x, 656, half, 44)
    # Gaza, right
    x = m + half + 24
    y = kick(d, x, ry, "Gaza", RED)
    y = head(d, x, y + 2, "Strike kills Hamas security chief in Gaza City",
             28, half, 34)
    y = block(d, x, y + 6,
              "An Israeli airstrike in western Gaza City killed Naeem "
              "Abu Nahel, Hamas' security chief. Seven were killed in "
              "Gaza on Tuesday.",
              fnt(SANS, 20), half, 26, fill=GREY)
    burst_art(d, x, 656, half, 44)
    hline(d, m, 708, W - m, width=2)

    # ---- Row three: three shorts (724-958) ----
    ry = 724
    third = (W - 2 * m - 48) // 3
    cols = [
        ("Colombia", ORANGE, "Gunmen hold 30 hostages in Cartagena shop",
         "Armed men seized a supermarket after a failed armoured-truck "
         "robbery. Five elderly women were released; talks continue.",
         None),
        ("Yemen", TEAL, "Saudi strikes kill 43 in Yemen, Houthis say",
         "Seventeen telecom workers died in Hodeida and 26 more in a "
         "strike on buses and trucks in Lahj province.",
         None),
        ("Nepal", RED, "Magnitude 5.6 quake hits eastern Nepal",
         "The quake struck Koshi province near the Tibet border at "
         "07:17 local time on Tuesday.",
         "quake"),
    ]
    for i, (kick_text, colour, headline_text, body, art) in enumerate(cols):
        x = m + i * (third + 24)
        y = kick(d, x, ry, kick_text, colour)
        y = head(d, x, y + 2, headline_text, 24, third, 29)
        y = block(d, x, y + 4, body, fnt(SANS, 18), third, 23, fill=GREY)
        if art == "quake":
            quake_art(d, x, 900, third, 48)

    # ---- Footer strip (958-1010) ----
    hline(d, m, 958, W - m, width=2)
    d.text((m, 968),
           "ALSO: Malaysia to send 6,500 Rohingya back to Myanmar · "
           "COP31 ends with no deal · Microsoft declares 'Code Red'",
           font=fnt(SANS, 17), fill=GREY)
    d.text((m, 992),
           "Gukesh holds Sindarov in chess title defence · Sources: Reuters · AP · BBC — 25 November 2026",
           font=fnt(SANS_B, 15), fill=GREY)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote %s %dx%d" % (OUT, W, H))


if __name__ == "__main__":
    build()
