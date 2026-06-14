"""Cartoon/illustration version of the Japan PDF.

Replaces hero photos with:
  - Vector cartoon-style city illustrations (Tokyo Tower, Torii gate, Osaka
    Castle, A-Bomb Dome, Mt. Fuji etc.) drawn with reportlab.graphics
  - Emoji-rich section headers
  - A trip-route diagram on the at-a-glance page
  - A simple cost-breakdown bar chart on the costs page

Output: assets/pdfs/desk2destinations-japan.pdf
"""
from __future__ import annotations

from pathlib import Path

from reportlab.graphics.shapes import (
    Circle, Drawing, Line, Polygon, Rect, String, Group, Path as ShapePath,
)
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, NextPageTemplate, PageBreak, PageTemplate, Paragraph,
    Spacer,
)

import _japan_itinerary_build as v1

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "assets" / "pdfs" / "desk2destinations-japan.pdf"
TMP_OUTPUT = HERE / "assets" / "pdfs" / "_desk2destinations-japan.tmp.pdf"

TERRACOTTA = colors.HexColor("#c86446")
INK = colors.HexColor("#1f1d1a")
SOFT_INK = colors.HexColor("#5a5752")
SAKURA = colors.HexColor("#f7c4cc")
SAKURA_DEEP = colors.HexColor("#e88a98")
SKY = colors.HexColor("#cbe2ee")
SKY_DEEP = colors.HexColor("#8fb6c8")
LEAF = colors.HexColor("#7fa37e")
GOLD = colors.HexColor("#d6a857")
CREAM = colors.HexColor("#fdf6f0")
SNOW = colors.HexColor("#eaf2f6")
DOME_GREY = colors.HexColor("#8a8b86")


# ---------------------------------------------------------------------------
# Drawing helpers — each returns a reportlab Drawing flowable
# ---------------------------------------------------------------------------
def _bg(d: Drawing, w: float, h: float, fill):
    d.add(Rect(0, 0, w, h, fillColor=fill, strokeColor=None))


def _sun(d, cx, cy, r, fill):
    d.add(Circle(cx, cy, r, fillColor=fill, strokeColor=None))


def _sakura_petal(cx, cy, size, color):
    # tiny five-circle flower
    g = Group()
    for ang in (0, 72, 144, 216, 288):
        import math
        x = cx + size * 0.5 * math.cos(math.radians(ang - 90))
        y = cy + size * 0.5 * math.sin(math.radians(ang - 90))
        g.add(Circle(x, y, size * 0.45, fillColor=color, strokeColor=None))
    g.add(Circle(cx, cy, size * 0.25, fillColor=GOLD, strokeColor=None))
    return g


def mini_map(title: str, places: list[tuple[str, float, float]],
             travel_note: str, width=17 * cm, height=4.5 * cm):
    """A city-level route map in the same style as the trip-wide route diagram.

    `places` is a list of (label, x, y) tuples with x, y in 0..1 fractions.
    They are connected in order with a dashed terracotta line.
    """
    d = Drawing(width, height)
    _bg(d, width, height, CREAM)
    # Faint ward-ish background blob
    d.add(Polygon([
        width * 0.05, height * 0.30,
        width * 0.18, height * 0.65,
        width * 0.40, height * 0.55,
        width * 0.60, height * 0.70,
        width * 0.82, height * 0.55,
        width * 0.95, height * 0.30,
        width * 0.05, height * 0.30,
    ], fillColor=colors.HexColor("#f3e7d4"),
       strokeColor=colors.HexColor("#e2cfaa"), strokeWidth=0.6))
    # Connect pins in order
    for i in range(len(places) - 1):
        _, x1, y1 = places[i]
        _, x2, y2 = places[i + 1]
        d.add(Line(width * x1, height * y1, width * x2, height * y2,
                   strokeColor=TERRACOTTA, strokeWidth=1.4,
                   strokeDashArray=[4, 3]))
    # Pins + labels
    for label, x, y in places:
        cx = width * x
        cy = height * y
        d.add(Circle(cx, cy, 7, fillColor=TERRACOTTA,
                     strokeColor=colors.white, strokeWidth=1.6))
        d.add(Circle(cx, cy, 2.5, fillColor=colors.white, strokeColor=None))
        # label position: alternate above/below to avoid overlap
        below = (places.index((label, x, y)) % 2 == 0)
        ly = cy - 14 if below else cy + 12
        d.add(String(cx, ly, label, fontName="Helvetica-Bold",
                     fontSize=8, fillColor=INK, textAnchor="middle"))
    # Title
    d.add(String(width * 0.5, height * 0.92, title.upper(),
                 fontName="Helvetica-Bold", fontSize=10, fillColor=TERRACOTTA,
                 textAnchor="middle"))
    # Travel mode at bottom
    d.add(String(width * 0.5, height * 0.08, travel_note,
                 fontName="Helvetica-Oblique", fontSize=8.5,
                 fillColor=SOFT_INK, textAnchor="middle"))
    return d


# Per-city pins (label, x-fraction, y-fraction within the mini-map frame)
CITY_MAPS = {
    "tokyo": (
        "Tokyo — what we walked",
        [
            ("Senso-ji",   0.12, 0.55),
            ("Akihabara",  0.30, 0.50),
            ("Tokyo Stn",  0.46, 0.45),
            ("Ginza",      0.58, 0.40),
            ("Shibuya",    0.72, 0.50),
            ("Meiji",      0.82, 0.55),
            ("Shinjuku",   0.92, 0.50),
        ],
        "Suica · JR Yamanote loop · Willer bus to Mt. Fuji",
    ),
    "kyoto": (
        "Kyoto — what we walked",
        [
            ("Kinkaku-ji",  0.12, 0.55),
            ("Nishiki Mkt", 0.30, 0.45),
            ("Kyoto Stn",   0.46, 0.40),
            ("Kiyomizu",    0.62, 0.55),
            ("Fushimi Inari", 0.78, 0.45),
            ("Uji",         0.92, 0.55),
        ],
        "Day Bus Pass · short JR hop to Uji and Fushimi",
    ),
    "osaka": (
        "Osaka — what we walked",
        [
            ("Osaka Castle", 0.14, 0.55),
            ("Daimaru",      0.34, 0.45),
            ("Dotonbori",    0.50, 0.50),
            ("Don Quijote",  0.66, 0.45),
            ("Mercy Vegan",  0.80, 0.55),
            ("Rinku Outlet", 0.92, 0.45),
        ],
        "Suica · Osaka Metro · Nankai line to Rinku",
    ),
    "hiroshima": (
        "Hiroshima — what we walked",
        [
            ("Hiroshima Stn", 0.12, 0.45),
            ("A-Bomb Dome",   0.30, 0.55),
            ("Cenotaph",      0.46, 0.45),
            ("Peace Museum",  0.60, 0.55),
            ("Hondori Arcade",0.78, 0.45),
            ("Caffè Ponte",   0.92, 0.55),
        ],
        "Day Pass + red Hiroshima Loop Bus · trams · station lockers",
    ),
    "sapporo": (
        "Sapporo — what we walked",
        [
            ("Sapporo Stn",     0.10, 0.50),
            ("Odori Park",      0.26, 0.45),
            ("Pole Town",       0.40, 0.55),
            ("Hill of Buddha",  0.56, 0.45),
            ("Noboribetsu",     0.74, 0.55),
            ("Lake Toya",       0.92, 0.45),
        ],
        "Limousine Bus · Sapporo Metro · day-tour bus for Hokkaido",
    ),
}


def tokyo_scene(width=17 * cm, height=4.5 * cm):
    d = Drawing(width, height)
    _bg(d, width, height, SKY)
    _sun(d, width * 0.85, height * 0.72, height * 0.18, colors.HexColor("#ffd28a"))
    # Skyline silhouettes (rectangles)
    for x, w_, h_ in [
        (0.05, 0.07, 0.45), (0.13, 0.05, 0.60), (0.19, 0.06, 0.40),
        (0.62, 0.06, 0.55), (0.70, 0.04, 0.42), (0.76, 0.07, 0.62),
        (0.84, 0.05, 0.48), (0.92, 0.06, 0.55),
    ]:
        d.add(Rect(width * x, 0, width * w_, height * h_,
                   fillColor=colors.HexColor("#3e4a55"), strokeColor=None))
        # window dots
        for wy in (0.12, 0.22, 0.32, 0.42):
            d.add(Rect(width * (x + 0.012), height * wy, 5, 5,
                       fillColor=colors.HexColor("#ffd87a"), strokeColor=None))
    # Tokyo Tower (centred)
    cx = width * 0.42
    base = 0
    top = height * 0.92
    # Body taper triangle
    d.add(Polygon([
        cx - width * 0.05, base,
        cx + width * 0.05, base,
        cx + width * 0.012, top - height * 0.18,
        cx - width * 0.012, top - height * 0.18,
    ], fillColor=TERRACOTTA, strokeColor=colors.HexColor("#a14e36"), strokeWidth=0.6))
    # Observation deck
    d.add(Rect(cx - width * 0.025, top - height * 0.22, width * 0.05,
               height * 0.05, fillColor=TERRACOTTA, strokeColor=None))
    # Antenna
    d.add(Line(cx, top - height * 0.18, cx, top, strokeColor=TERRACOTTA, strokeWidth=2.4))
    # cross-lattice lines
    for fr in (0.15, 0.30, 0.50, 0.70):
        y = base + (top - height * 0.22 - base) * fr
        wd = (1 - fr) * width * 0.10 + width * 0.024
        d.add(Line(cx - wd / 2, y, cx + wd / 2, y,
                   strokeColor=colors.HexColor("#a14e36"), strokeWidth=0.5))
    # Mt Fuji peeking on left
    d.add(Polygon([
        width * 0.0, height * 0.30,
        width * 0.20, height * 0.76,
        width * 0.40, height * 0.30,
    ], fillColor=colors.HexColor("#9aa9b3"), strokeColor=None))
    d.add(Polygon([
        width * 0.14, height * 0.62,
        width * 0.20, height * 0.76,
        width * 0.26, height * 0.62,
        width * 0.22, height * 0.58,
        width * 0.18, height * 0.58,
    ], fillColor=colors.white, strokeColor=None))
    return d


def kyoto_scene(width=17 * cm, height=4.5 * cm):
    d = Drawing(width, height)
    _bg(d, width, height, colors.HexColor("#ffe9d6"))
    # Mountains
    d.add(Polygon([
        0, height * 0.45,
        width * 0.30, height * 0.85,
        width * 0.55, height * 0.50,
        width * 0.80, height * 0.78,
        width, height * 0.45,
        width, 0, 0, 0,
    ], fillColor=colors.HexColor("#9bbfa3"), strokeColor=None))
    # Sun
    _sun(d, width * 0.78, height * 0.78, height * 0.16, colors.HexColor("#ffb88a"))
    # Torii gate (vermilion)
    cx = width * 0.50
    post_h = height * 0.78
    post_w = width * 0.018
    # Top crossbeam (kasagi) — slight upward curve via two trapezoids
    d.add(Polygon([
        cx - width * 0.18, post_h - height * 0.04,
        cx + width * 0.18, post_h - height * 0.04,
        cx + width * 0.16, post_h,
        cx - width * 0.16, post_h,
    ], fillColor=TERRACOTTA, strokeColor=None))
    # Second crossbeam (nuki)
    d.add(Rect(cx - width * 0.14, post_h - height * 0.16, width * 0.28,
               height * 0.04, fillColor=TERRACOTTA, strokeColor=None))
    # Tablet
    d.add(Rect(cx - width * 0.025, post_h - height * 0.12, width * 0.05,
               height * 0.06, fillColor=colors.white, strokeColor=TERRACOTTA, strokeWidth=0.5))
    # Posts
    d.add(Rect(cx - width * 0.13 - post_w / 2, 0, post_w, post_h,
               fillColor=TERRACOTTA, strokeColor=None))
    d.add(Rect(cx + width * 0.13 - post_w / 2, 0, post_w, post_h,
               fillColor=TERRACOTTA, strokeColor=None))
    # Repeated torii fading into distance
    for i, (sx, sy, scale, alpha) in enumerate([
        (0.66, 0.0, 0.7, colors.HexColor("#dd7a5c")),
        (0.78, 0.0, 0.55, colors.HexColor("#e89a82")),
        (0.88, 0.0, 0.45, colors.HexColor("#eeb6a1")),
    ]):
        cx2 = width * (sx + 0.05)
        ph = post_h * scale
        pw = post_w
        d.add(Polygon([
            cx2 - width * 0.13 * scale, ph - height * 0.04 * scale,
            cx2 + width * 0.13 * scale, ph - height * 0.04 * scale,
            cx2 + width * 0.115 * scale, ph,
            cx2 - width * 0.115 * scale, ph,
        ], fillColor=alpha, strokeColor=None))
        d.add(Rect(cx2 - width * 0.10 * scale, ph - height * 0.12 * scale,
                   width * 0.20 * scale, height * 0.03 * scale,
                   fillColor=alpha, strokeColor=None))
        d.add(Rect(cx2 - width * 0.095 * scale - pw / 2, 0, pw, ph,
                   fillColor=alpha, strokeColor=None))
        d.add(Rect(cx2 + width * 0.095 * scale - pw / 2, 0, pw, ph,
                   fillColor=alpha, strokeColor=None))
    # Sakura petals
    d.add(_sakura_petal(width * 0.10, height * 0.78, 10, SAKURA_DEEP))
    d.add(_sakura_petal(width * 0.20, height * 0.55, 8, SAKURA))
    d.add(_sakura_petal(width * 0.35, height * 0.82, 9, SAKURA_DEEP))
    return d


def osaka_scene(width=17 * cm, height=4.5 * cm):
    d = Drawing(width, height)
    _bg(d, width, height, colors.HexColor("#f4e6cc"))
    # River reflection at base
    d.add(Rect(0, 0, width, height * 0.18, fillColor=colors.HexColor("#9ec3d6"), strokeColor=None))
    # Castle silhouette (centre)
    cx = width * 0.5
    base = height * 0.18
    # Stone base
    d.add(Polygon([
        cx - width * 0.18, base,
        cx + width * 0.18, base,
        cx + width * 0.13, base + height * 0.12,
        cx - width * 0.13, base + height * 0.12,
    ], fillColor=colors.HexColor("#c8b793"), strokeColor=colors.HexColor("#7a6c50"), strokeWidth=0.6))
    # Tier 1
    y0 = base + height * 0.12
    d.add(Rect(cx - width * 0.10, y0, width * 0.20, height * 0.10,
               fillColor=colors.white, strokeColor=colors.HexColor("#6a6a6a"), strokeWidth=0.4))
    # Roof 1 (curved-ish trapezoid)
    d.add(Polygon([
        cx - width * 0.13, y0 + height * 0.10,
        cx + width * 0.13, y0 + height * 0.10,
        cx + width * 0.09, y0 + height * 0.16,
        cx - width * 0.09, y0 + height * 0.16,
    ], fillColor=LEAF, strokeColor=colors.HexColor("#3f5c3f"), strokeWidth=0.6))
    # Tier 2
    y1 = y0 + height * 0.16
    d.add(Rect(cx - width * 0.07, y1, width * 0.14, height * 0.08,
               fillColor=colors.white, strokeColor=colors.HexColor("#6a6a6a"), strokeWidth=0.4))
    # Roof 2
    d.add(Polygon([
        cx - width * 0.10, y1 + height * 0.08,
        cx + width * 0.10, y1 + height * 0.08,
        cx + width * 0.06, y1 + height * 0.14,
        cx - width * 0.06, y1 + height * 0.14,
    ], fillColor=LEAF, strokeColor=colors.HexColor("#3f5c3f"), strokeWidth=0.6))
    # Tier 3 (top)
    y2 = y1 + height * 0.14
    d.add(Rect(cx - width * 0.045, y2, width * 0.09, height * 0.06,
               fillColor=colors.white, strokeColor=colors.HexColor("#6a6a6a"), strokeWidth=0.4))
    # Top roof — gold tipped
    d.add(Polygon([
        cx - width * 0.07, y2 + height * 0.06,
        cx + width * 0.07, y2 + height * 0.06,
        cx, y2 + height * 0.16,
    ], fillColor=GOLD, strokeColor=colors.HexColor("#9c7a30"), strokeWidth=0.6))
    # Antenna
    d.add(Line(cx, y2 + height * 0.16, cx, y2 + height * 0.21,
               strokeColor=GOLD, strokeWidth=1.4))
    # Glico-style running man on right (simplified) — just dotonbori vibes
    rx = width * 0.86
    ry = height * 0.55
    d.add(Rect(rx - 12, ry - 16, 24, 32, fillColor=colors.HexColor("#ffd24c"),
               strokeColor=colors.HexColor("#a07a18"), strokeWidth=0.5))
    d.add(String(rx, ry - 4, "GLICO", fontName="Helvetica-Bold", fontSize=5.5,
                 fillColor=colors.HexColor("#a04030"), textAnchor="middle"))
    # Cherry blossoms
    d.add(_sakura_petal(width * 0.08, height * 0.78, 10, SAKURA_DEEP))
    d.add(_sakura_petal(width * 0.18, height * 0.55, 8, SAKURA))
    d.add(_sakura_petal(width * 0.92, height * 0.82, 9, SAKURA_DEEP))
    return d


def hiroshima_scene(width=17 * cm, height=4.5 * cm):
    d = Drawing(width, height)
    _bg(d, width, height, colors.HexColor("#dfe9d8"))
    # Park ground
    d.add(Rect(0, 0, width, height * 0.16, fillColor=LEAF, strokeColor=None))
    # River
    d.add(Rect(0, height * 0.12, width, height * 0.06,
               fillColor=colors.HexColor("#9ec3d6"), strokeColor=None))
    # A-Bomb Dome — central
    cx = width * 0.5
    base = height * 0.18
    # Building base
    d.add(Rect(cx - width * 0.06, base, width * 0.12, height * 0.30,
               fillColor=colors.HexColor("#cfcfca"), strokeColor=DOME_GREY, strokeWidth=0.6))
    # Window dots
    for wx in (0.42, 0.46, 0.50, 0.54, 0.58):
        for wy in (0.24, 0.34, 0.44):
            d.add(Rect(width * wx, height * wy, 4, 5,
                       fillColor=DOME_GREY, strokeColor=None))
    # Side wings
    d.add(Rect(cx - width * 0.13, base, width * 0.07, height * 0.20,
               fillColor=colors.HexColor("#cfcfca"), strokeColor=DOME_GREY, strokeWidth=0.6))
    d.add(Rect(cx + width * 0.06, base, width * 0.07, height * 0.20,
               fillColor=colors.HexColor("#cfcfca"), strokeColor=DOME_GREY, strokeWidth=0.6))
    # Dome (the iconic skeletal hemisphere)
    dome_cx = cx
    dome_cy = base + height * 0.30
    dome_r = width * 0.06
    d.add(Polygon([
        dome_cx - dome_r, dome_cy,
        dome_cx + dome_r, dome_cy,
        dome_cx + dome_r * 0.8, dome_cy + dome_r * 0.9,
        dome_cx, dome_cy + dome_r,
        dome_cx - dome_r * 0.8, dome_cy + dome_r * 0.9,
    ], fillColor=colors.HexColor("#bfb8b0"), strokeColor=DOME_GREY, strokeWidth=0.7))
    # Skeletal lines on dome
    for ang_deg in (-60, -30, 0, 30, 60):
        import math
        ax = dome_cx + dome_r * math.sin(math.radians(ang_deg))
        ay = dome_cy + dome_r * math.cos(math.radians(ang_deg))
        d.add(Line(dome_cx, dome_cy, ax, ay, strokeColor=DOME_GREY, strokeWidth=0.5))
    # Origami crane (left) — simple triangle pair
    crane_x = width * 0.18
    crane_y = height * 0.62
    d.add(Polygon([
        crane_x - 14, crane_y,
        crane_x + 14, crane_y,
        crane_x, crane_y + 14,
    ], fillColor=colors.white, strokeColor=DOME_GREY, strokeWidth=0.6))
    d.add(Polygon([
        crane_x - 12, crane_y + 4,
        crane_x + 12, crane_y + 4,
        crane_x, crane_y - 12,
    ], fillColor=colors.white, strokeColor=DOME_GREY, strokeWidth=0.6))
    # Trees
    for tx in (0.05, 0.13, 0.83, 0.93):
        d.add(Circle(width * tx, height * 0.22, 12, fillColor=LEAF,
                     strokeColor=colors.HexColor("#3f5c3f"), strokeWidth=0.4))
        d.add(Rect(width * tx - 1.5, height * 0.16, 3, 8,
                   fillColor=colors.HexColor("#6b4a2a"), strokeColor=None))
    return d


def sapporo_scene(width=17 * cm, height=4.5 * cm):
    d = Drawing(width, height)
    _bg(d, width, height, SNOW)
    # Snow ground
    d.add(Rect(0, 0, width, height * 0.20, fillColor=colors.white, strokeColor=None))
    # Mountain (Hokkaido)
    d.add(Polygon([
        0, height * 0.20,
        width * 0.30, height * 0.86,
        width * 0.55, height * 0.20,
    ], fillColor=colors.HexColor("#a3b6c2"), strokeColor=None))
    d.add(Polygon([
        width * 0.20, height * 0.62,
        width * 0.30, height * 0.86,
        width * 0.40, height * 0.62,
        width * 0.34, height * 0.55,
        width * 0.26, height * 0.55,
    ], fillColor=colors.white, strokeColor=None))
    # Second smaller mountain
    d.add(Polygon([
        width * 0.45, height * 0.20,
        width * 0.62, height * 0.62,
        width * 0.78, height * 0.20,
    ], fillColor=colors.HexColor("#bbcdd8"), strokeColor=None))
    # Hill of the Buddha — small mound with statue silhouette right side
    bx = width * 0.85
    d.add(Polygon([
        width * 0.80, height * 0.20,
        bx, height * 0.46,
        width * 0.97, height * 0.20,
    ], fillColor=colors.HexColor("#9eb09a"), strokeColor=None))
    # Buddha head poking out (oval)
    d.add(Polygon([
        bx - 7, height * 0.40,
        bx + 7, height * 0.40,
        bx + 6, height * 0.50,
        bx, height * 0.55,
        bx - 6, height * 0.50,
    ], fillColor=colors.HexColor("#7a8a82"), strokeColor=colors.HexColor("#3a4a42"), strokeWidth=0.5))
    # Snowflakes
    for sx, sy in [(0.10, 0.78), (0.25, 0.40), (0.40, 0.70), (0.55, 0.50),
                    (0.70, 0.78), (0.92, 0.65), (0.15, 0.55), (0.50, 0.85)]:
        cx = width * sx
        cy = height * sy
        for ang_deg in (0, 60, 120):
            import math
            dx = 5 * math.cos(math.radians(ang_deg))
            dy = 5 * math.sin(math.radians(ang_deg))
            d.add(Line(cx - dx, cy - dy, cx + dx, cy + dy,
                       strokeColor=SKY_DEEP, strokeWidth=0.7))
    # Late-season sakura
    d.add(_sakura_petal(width * 0.08, height * 0.30, 9, SAKURA_DEEP))
    d.add(_sakura_petal(width * 0.62, height * 0.35, 8, SAKURA))
    return d


def route_diagram(width=17 * cm, height=4.5 * cm):
    """A horizontal trip route: Tokyo → Kyoto → Osaka → Hiroshima → Sapporo."""
    d = Drawing(width, height)
    _bg(d, width, height, CREAM)
    # Faint Japan island silhouette in background
    d.add(Polygon([
        width * 0.05, height * 0.30,
        width * 0.15, height * 0.55,
        width * 0.30, height * 0.45,
        width * 0.45, height * 0.50,
        width * 0.62, height * 0.40,
        width * 0.78, height * 0.55,
        width * 0.95, height * 0.45,
        width * 0.92, height * 0.30,
        width * 0.05, height * 0.30,
    ], fillColor=colors.HexColor("#f3e7d4"), strokeColor=colors.HexColor("#e2cfaa"), strokeWidth=0.6))
    # Cities along the path
    cities = [
        ("Sapporo",   0.10, 0.75, "✈"),
        ("Tokyo",     0.30, 0.45, "🗼"),
        ("Kyoto",     0.50, 0.45, "⛩"),
        ("Osaka",     0.65, 0.40, "🏯"),
        ("Hiroshima", 0.85, 0.45, "🕊"),
    ]
    # Connect with curved-ish lines (use straight for simplicity)
    for i in range(len(cities) - 1):
        _, x1, y1, _ = cities[i]
        _, x2, y2, _ = cities[i + 1]
        d.add(Line(width * x1, height * y1, width * x2, height * y2,
                   strokeColor=TERRACOTTA, strokeWidth=1.6,
                   strokeDashArray=[4, 3]))
    # City dots + labels
    for label, x, y, _ in cities:
        cx = width * x
        cy = height * y
        d.add(Circle(cx, cy, 8, fillColor=TERRACOTTA, strokeColor=colors.white, strokeWidth=2))
        d.add(Circle(cx, cy, 3, fillColor=colors.white, strokeColor=None))
        d.add(String(cx, cy - 16, label, fontName="Helvetica-Bold",
                     fontSize=9, fillColor=INK, textAnchor="middle"))
    # Title
    d.add(String(width * 0.5, height * 0.92, "OUR ROUTE",
                 fontName="Helvetica-Bold", fontSize=10, fillColor=TERRACOTTA,
                 textAnchor="middle"))
    # Mode-of-travel legend at bottom
    d.add(String(width * 0.5, height * 0.10,
                 "Shinkansen + Willer overnight bus + 1 domestic flight",
                 fontName="Helvetica-Oblique", fontSize=8.5,
                 fillColor=SOFT_INK, textAnchor="middle"))
    return d


# ---------------------------------------------------------------------------
# Visual Top-10 highlights — terracotta number badges + emoji icons
# ---------------------------------------------------------------------------
TOP10 = [
    ("\u9748",  "Mt. Fuji day trip from Tokyo", "Tokyo",
     "Willer highway bus to Kawaguchiko, red Fuji loop to Oishi Park, sprint to Chureito Pagoda for the postcard."),
    ("\u26e9",  "Senso-ji at 7:30 a.m.", "Tokyo",
     "Asakusa\u2019s big landmark, almost empty before the crowds. Worth the alarm."),
    ("\U0001F6A6", "Shibuya Crossing & Hachiko", "Tokyo",
     "Cross it three times. Free upper view from a mall, Falafel Brothers in Parco for lunch."),
    ("\U0001F332", "Meiji Shrine forest", "Tokyo",
     "Wine barrels, Japan\u2019s oldest wooden Torii, a hush you don\u2019t expect this close to Shibuya."),
    ("\U0001F98A", "Fushimi Inari Torii hike", "Kyoto",
     "Walk the vermilion tunnels to the first viewpoint and the city opens up below."),
    ("\U0001F375", "Uji matcha day trip", "Kyoto",
     "An hour from Kyoto. Whisked matcha, parfaits, matcha soba. Most shops shut by 6 p.m."),
    ("\u2728",  "Kinkaku-ji in the rain", "Kyoto",
     "The Golden Temple goes liquid in soft rain and the pond doubles it perfectly."),
    ("\U0001F319", "Dotonbori + Don Quijote", "Osaka",
     "Glico running man, canal reflections, yellow Ferris wheel. Block 3 hours for Donki alone."),
    ("\U0001F54A", "Peace Memorial Park & Dome", "Hiroshima",
     "Stand in front of the Genbaku Dome. Walk the park slowly. The 3D museum is essential."),
    ("\U0001F5FF", "Hill of the Buddha (Tadao Ando)", "Sapporo",
     "Tunnel approach, lavender ring, Buddha reveal. 1.5 hr from Sapporo, worth every minute."),
]


def _badge_drawing(num: int, size: float = 0.95 * cm):
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2 - 1,
                 fillColor=TERRACOTTA, strokeColor=colors.white, strokeWidth=1.5))
    d.add(String(size / 2, size / 2 - 4, str(num),
                 fontName="Helvetica-Bold", fontSize=12,
                 fillColor=colors.white, textAnchor="middle"))
    return d


def visual_top_ten():
    from reportlab.platypus import HRFlowable, Table, TableStyle
    flow = []
    flow.append(Paragraph("Top 10 must-do highlights", v1.S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10))
    flow.append(Paragraph(
        "Curated from what we actually did, in the order we'd tell a friend. "
        "No filler.", v1.S_BODY_J,
    ))
    flow.append(Spacer(1, 6))

    rows = []
    for i, (icon, title, city, desc) in enumerate(TOP10, start=1):
        cell = Paragraph(
            f"<font size=12>{icon}</font> &nbsp; <b>{title}</b> &nbsp;"
            f"<font color='#c86446'>&middot; {city}</font><br/>"
            f"<font size=9.5 color='#5a5752'>{desc}</font>",
            v1.S_BODY,
        )
        rows.append([_badge_drawing(i), cell])

    tbl = Table(rows, colWidths=[1.2 * cm, 16.0 * cm], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e6dfd2")),
    ]))
    flow.append(tbl)
    flow.append(PageBreak())
    return flow


def cost_chart(width=17 * cm, height=6.5 * cm):
    """Horizontal bar chart of mid-range cost split (per person, INR)."""
    d = Drawing(width, height)
    _bg(d, width, height, CREAM)
    # Title
    d.add(String(width * 0.5, height - 14, "Where the rupees went (mid-range, per person)",
                 fontName="Helvetica-Bold", fontSize=10.5, fillColor=INK,
                 textAnchor="middle"))
    chart = HorizontalBarChart()
    chart.x = 110
    chart.y = 18
    chart.width = width - 130
    chart.height = height - 50
    data = [(75000, 25000, 56000, 30800, 14000, 12600, 6500, 5500)]
    chart.data = data
    chart.categoryAxis.categoryNames = [
        "Flights ex-IN", "JR Pass 7-day", "Stays (14 nt)", "Food (14 d)",
        "Local transit", "Attractions", "Hiroshima bus", "Sapporo flight",
    ]
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 8.5
    chart.categoryAxis.labels.fillColor = INK
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 80000
    chart.valueAxis.valueStep = 20000
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 8
    chart.valueAxis.labels.fillColor = SOFT_INK
    chart.bars[0].fillColor = TERRACOTTA
    chart.bars[0].strokeColor = colors.HexColor("#9c4d34")
    chart.bars[0].strokeWidth = 0.4
    chart.barLabels.fontName = "Helvetica-Bold"
    chart.barLabels.fontSize = 8
    chart.barLabels.fillColor = INK
    chart.barLabelFormat = lambda v: f"₹{int(v):,}"
    chart.barLabels.dx = 4
    chart.barLabels.boxAnchor = "w"
    chart.barLabels.nudge = 6
    d.add(chart)
    d.add(String(width * 0.5, 6, "Total ≈ ₹2,80,000–3,20,000 per person, all-in",
                 fontName="Helvetica-Oblique", fontSize=9, fillColor=SOFT_INK,
                 textAnchor="middle"))
    return d


# ---------------------------------------------------------------------------
# Wrap v1 city sections to inject the cartoon scene after the intro
# ---------------------------------------------------------------------------
SCENES = {
    "tokyo": (tokyo_scene, "Tokyo Tower silhouette + Mt. Fuji on the horizon"),
    "kyoto": (kyoto_scene, "Vermilion torii gates fading into the Higashiyama hills"),
    "osaka": (osaka_scene, "Osaka Castle, gold roof glinting"),
    "hiroshima": (hiroshima_scene, "The A-Bomb Dome, paper cranes, Peace Park trees"),
    "sapporo": (sapporo_scene, "Hokkaido snow, Mt. Usu in the distance, Hill of the Buddha"),
}


CITY_URLS = {
    "tokyo":     "https://desk2destinations.com/japan-tokyo.html",
    "kyoto":     "https://desk2destinations.com/japan-kyoto.html",
    "osaka":     "https://desk2destinations.com/japan-osaka.html",
    "hiroshima": "https://desk2destinations.com/japan-hiroshima.html",
    "sapporo":   "https://desk2destinations.com/japan-sapporo.html",
}


def _read_more_line(city: str):
    url = CITY_URLS[city]
    return Paragraph(
        f"<font size=10 color='#5a5752'>\u2192 Read the full {city.title()} "
        f"guide on the site:&nbsp;</font>"
        f"<link href='{url}'><font size=10 color='#c86446'><b>{url.replace('https://','')}</b></font></link>",
        v1.S_BODY,
    )


def _inject_cartoon(city: str, flow: list):
    """Insert the cartoon illustration + mini route-map after the city's intro paragraph."""
    from reportlab.platypus import HRFlowable
    out = []
    inserted = False
    for i, item in enumerate(flow):
        out.append(item)
        if not inserted and isinstance(item, Paragraph) \
                and i >= 2 and isinstance(flow[i - 1], HRFlowable):
            scene_fn, caption_txt = SCENES[city]
            out.append(Spacer(1, 6))
            out.append(scene_fn())
            out.append(Spacer(1, 3))
            out.append(Paragraph(
                f"<font size=8.5 color='#5a5752'><i>{caption_txt}</i></font>",
                v1.S_BODY,
            ))
            # Mini route-map below the cartoon scene
            title, places, travel = CITY_MAPS[city]
            out.append(Spacer(1, 8))
            out.append(mini_map(title, places, travel))
            out.append(Spacer(1, 6))
            out.append(_read_more_line(city))
            out.append(Spacer(1, 8))
            inserted = True
    return out


# ---------------------------------------------------------------------------
# Trim verbose copy — replace known long paragraphs with shorter versions.
# Match by a unique opening substring of the original v1 text.
# ---------------------------------------------------------------------------
TRIMS = {
    # Cover: make the site URL clickable
    "<font color='#c86446'><b>desk2destinations.com</b></font>":
        "<link href='https://desk2destinations.com/'>"
        "<font color='#c86446'><b>desk2destinations.com</b></font></link>"
        "  &middot;  Honesty over hype. Slow over rushed. Practical over pretty.",
    # Closing CTA — link the contact URL and Instagram handle
    "Follow <b>@desk2destinations_</b>":
        "Follow <link href='https://www.instagram.com/desk2destinations_'>"
        "<b><font color='#c86446'>@desk2destinations_</font></b></link> on "
        "Instagram for new diaries and reels, or drop us a note via "
        "<link href='https://desk2destinations.com/contact.html'>"
        "<font color='#c86446'><b>desk2destinations.com/contact.html</b></font>"
        "</link>. We read every message. If you spot something off in this PDF "
        "or want a city we haven\u2019t covered yet, that\u2019s the place to "
        "tell us.",
    # at-a-glance "What we'd do differently"
    "Skipping Miyajima to make":
        "Skipping Miyajima for the overnight Willer bus is the one regret. "
        "Give Hiroshima 36 hours next time so the floating torii isn't a "
        "rushed afterthought.",
    # Tokyo honest reality check
    "Tokyo Station is a maze":
        "Tokyo Station is a maze \u2014 budget an extra 30\u201345 minutes "
        "your first time. Akihabara rewards walking energy, not list energy: "
        "four hours in BIC Camera and we still didn\u2019t see half the floors.",
    # Kyoto honest reality check
    "Kyoto refuses to be rushed":
        "Kyoto refuses to be rushed \u2014 even the rain in Kyoto walks. "
        "If your trip is short, give Kyoto three nights, not two.",
    # Osaka honest reality check
    "<b>Compare prices across at least two Matsumoto":
        "<b>Compare prices across two Matsumoto Kiyoshi stores</b> before bulk "
        "buying \u2014 same product, sometimes 20\u201330% apart in the same "
        "lane. And if you spot a KitKat 14-flavour gift box, just buy it.",
    # Hiroshima honest reality check
    "One day is too tight":
        "One day is too tight. Stay a night and plan half a day for Miyajima "
        "at minimum \u2014 the floating torii is the visit we will come back for.",
    # Sapporo honest reality check
    "Two days is not enough":
        "Two days is not enough \u2014 Hokkaido feels like its own country. "
        "Skipping Bear Ranch + Mt. Usu ropeway to shop instead is the one "
        "call we don\u2019t regret.",
}


def _trim_flow(flow: list) -> list:
    out = []
    for item in flow:
        if isinstance(item, Paragraph) and hasattr(item, "text"):
            text = item.text or ""
            replaced = False
            for needle, replacement in TRIMS.items():
                if text.lstrip().startswith(needle):
                    out.append(Paragraph(replacement, item.style))
                    replaced = True
                    break
            if replaced:
                continue
        out.append(item)
    return out


# ---------------------------------------------------------------------------
# Replace at-a-glance to insert the route diagram after the opening blurb,
# and costs to insert the bar chart instead of the plain table.
# ---------------------------------------------------------------------------
def at_a_glance_with_route():
    flow = v1.at_a_glance()
    from reportlab.platypus import HRFlowable
    out = []
    inserted = False
    for i, item in enumerate(flow):
        out.append(item)
        if not inserted and isinstance(item, Paragraph) and i >= 2 \
                and isinstance(flow[i - 1], HRFlowable):
            out.append(Spacer(1, 6))
            out.append(route_diagram())
            out.append(Spacer(1, 10))
            inserted = True
    return out


def costs_with_chart():
    """Costs page: replace the v1 table with a bar chart but keep the rest."""
    from reportlab.platypus import Table
    flow = v1.costs_and_close()
    out = []
    swapped = False
    for item in flow:
        if not swapped and isinstance(item, Table):
            out.append(cost_chart())
            swapped = True
            continue
        out.append(item)
    return out


# ---------------------------------------------------------------------------
def build():
    doc = BaseDocTemplate(
        str(TMP_OUTPUT),
        pagesize=A4,
        leftMargin=v1.MARGIN, rightMargin=v1.MARGIN,
        topMargin=v1.MARGIN, bottomMargin=v1.MARGIN,
        title="Japan Itinerary | Desk2Destinations",
        author="Ayushi & Harshit Jain",
        subject="Two-week Japan itinerary, vegetarian-friendly",
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[v1.cover_frame],
                     onPage=v1._cover_decoration),
        PageTemplate(id="Body", frames=[v1.frame], onPage=v1._footer),
    ])

    story = []
    story += _trim_flow(v1.cover())
    if isinstance(story[-1], PageBreak):
        story.insert(len(story) - 1, NextPageTemplate("Body"))
    story += at_a_glance_with_route()
    story = _trim_flow(story)
    story += visual_top_ten()

    for city_fn, key in [
        (v1.city_tokyo, "tokyo"),
        (v1.city_kyoto, "kyoto"),
        (v1.city_osaka, "osaka"),
        (v1.city_hiroshima, "hiroshima"),
        (v1.city_sapporo, "sapporo"),
    ]:
        section_flow = city_fn()
        section_flow = _inject_cartoon(key, section_flow)
        section_flow = _trim_flow(section_flow)
        story += section_flow

    story += costs_with_chart() if False else _trim_flow(v1.costs_and_close())

    doc.build(story)
    # Atomic swap: try to replace OUTPUT; if it's locked (PDF viewer open),
    # leave the tmp file and tell the user to close + rerun.
    import shutil
    try:
        shutil.move(str(TMP_OUTPUT), str(OUTPUT))
        target = OUTPUT
    except PermissionError:
        target = TMP_OUTPUT
        print(f"  ! {OUTPUT.name} is locked; wrote to {TMP_OUTPUT.name} instead")
    size_kb = target.stat().st_size / 1024
    print(f"Wrote {target} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    build()
