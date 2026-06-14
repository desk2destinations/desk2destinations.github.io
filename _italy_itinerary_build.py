"""Italy itinerary PDF (lighter template, no per-country cartoons).

Output: assets/pdfs/desk2destinations-italy.pdf
"""
from __future__ import annotations

from pathlib import Path
import shutil

from reportlab.graphics.shapes import (
    Circle, Drawing, Line, Polygon, Rect, String, Group,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, NextPageTemplate,
    PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "assets" / "pdfs" / "desk2destinations-italy.pdf"
TMP_OUTPUT = HERE / "assets" / "pdfs" / "_desk2destinations-italy.tmp.pdf"

# Brand palette (matches Japan PDF + site)
TERRACOTTA = colors.HexColor("#c86446")
TERRACOTTA_DEEP = colors.HexColor("#9c4d34")
INK = colors.HexColor("#1f1d1a")
SOFT_INK = colors.HexColor("#5a5752")
RULE_GREY = colors.HexColor("#d6cfbe")
CREAM = colors.HexColor("#fdf6f0")
SAND = colors.HexColor("#f3e7d4")
SAND_LINE = colors.HexColor("#e2cfaa")
SEA = colors.HexColor("#cbe2ee")
OLIVE = colors.HexColor("#7fa37e")
GOLD = colors.HexColor("#d6a857")

MARGIN = 1.6 * cm

# Styles
S_BODY = ParagraphStyle(
    "body", fontName="Helvetica", fontSize=10.5, leading=15,
    textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6,
)
S_BODY_C = ParagraphStyle(
    "body_c", parent=S_BODY, alignment=TA_CENTER, textColor=SOFT_INK,
)
S_PAGE_H = ParagraphStyle(
    "page_h", fontName="Helvetica-Bold", fontSize=20, leading=24,
    textColor=TERRACOTTA, spaceAfter=4, alignment=TA_LEFT,
)
S_SECTION = ParagraphStyle(
    "section", fontName="Helvetica-Bold", fontSize=12.5, leading=15,
    textColor=INK, spaceBefore=8, spaceAfter=4,
)
S_CITY_H = ParagraphStyle(
    "city_h", fontName="Helvetica-Bold", fontSize=24, leading=28,
    textColor=TERRACOTTA, alignment=TA_LEFT, spaceAfter=2,
)
S_CITY_SUB = ParagraphStyle(
    "city_sub", fontName="Helvetica-Oblique", fontSize=11, leading=14,
    textColor=SOFT_INK, spaceAfter=8,
)
S_COVER_TITLE = ParagraphStyle(
    "cover_title", fontName="Helvetica-Bold", fontSize=44, leading=48,
    textColor=TERRACOTTA, alignment=TA_CENTER, spaceAfter=10,
)
S_COVER_SUB = ParagraphStyle(
    "cover_sub", fontName="Helvetica", fontSize=14, leading=18,
    textColor=INK, alignment=TA_CENTER, spaceAfter=20,
)
S_PULLQUOTE = ParagraphStyle(
    "pull", fontName="Helvetica-Oblique", fontSize=12.5, leading=17,
    textColor=SOFT_INK, alignment=TA_CENTER, spaceAfter=14,
)


# ---------------------------------------------------------------------------
# Italy content (extracted from desk2destinations.com city pages)
# ---------------------------------------------------------------------------
ITALY = {
    "cover_quote": "In Italy, food isn\u2019t part of the story \u2014 it is the story.",
    "at_a_glance_intro": (
        "A whirlwind week across Rome\u2019s ancient stones, Amalfi\u2019s "
        "coastal drama, Florence\u2019s Renaissance soul, and Venice\u2019s "
        "watery dream. Missed stops became memories, queues became rituals, "
        "and every city revealed layers of art, history, and food that "
        "refuse to leave you."
    ),
    "best_time": "April \u2014 shoulder season, perfect weather, fewer crowds than peak summer.",
    "visa": "Schengen visa for Indian passport holders; up to 90 days.",
    "currency": "EUR (\u20ac)",
    "transit_overall": (
        "Trenitalia and Italo trains link the major cities; regional buses "
        "(SITA, Flixbus) handle secondary routes and the Amalfi coast. "
        "Venice runs on water \u2014 vaporetto and the occasional gondola."
    ),
    "regret": (
        "We rushed Florence in a single day. Next time, three nights in "
        "Florence and a real overnight in Amalfi instead of the dawn-bus "
        "scramble back."
    ),
    "transit_note": (
        "Always validate train tickets at the platform machine \u2014 "
        "inspectors do check, and the fines are not friendly to tourists."
    ),
    "total": "\u20b91,80,000 \u2013 2,20,000 per person, all-in (1 week, mid-range)",
}

TOP10 = [
    ("\u2694\ufe0f", "Colosseum", "Rome",
     "2,000-year-old amphitheatre that survived earthquakes, fires and a million selfie sticks."),
    ("\ud83d\udcb0", "Trevi Fountain", "Rome",
     "Baroque marvel collecting \u20ac1M+ a year for charity. Three coins, one wish, every time."),
    ("\ud83c\udfa8", "Vatican & Sistine Chapel", "Rome",
     "Nine miles of museums culminating in Michelangelo\u2019s ceiling \u2014 stand still, look up."),
    ("\ud83c\udf4b", "Amalfi Coast Drive", "Amalfi",
     "Cliffs, lemon groves, sea-sparkle and a bus driver who clearly trusts physics."),
    ("\ud83c\udf70", "Sal De Riso, Minori", "Amalfi",
     "Delizia al Limone by candlelight beside the Tyrrhenian. Worth every euro of the seating charge."),
    ("\ud83d\uddfc", "Leaning Tower, Pisa", "Florence",
     "55.86 m of beautifully wrong, where Galileo did the falling-bodies thing."),
    ("\ud83c\udf55", "Gustapizza", "Florence",
     "Two-hour queue, two-minute revelation. Wood-fired pizza that recalibrates expectations."),
    ("\ud83c\udf09", "Rialto Bridge", "Venice",
     "1591 Istrian-stone arch lined with shops \u2014 the original instagram-the-canal spot."),
    ("\ud83d\udc94", "Bridge of Sighs", "Venice",
     "Prisoners\u2019 last view of Venice; lovers\u2019 first under the sunset. Same bridge, different stories."),
    ("\ud83c\udf66", "Gelato, everywhere", "All four",
     "Romeo (Rome), Venchi (Florence), and one no-name Venetian cone we still dream about."),
]

COSTS = [
    ("Category", "Detail", "Approx \u20b9 / pp"),
    ("Flights", "IN \u2192 Rome via Barcelona", "\u20b945,000"),
    ("Trains", "Rome \u2192 Salerno \u2192 Florence \u2192 Venice", "\u20b912,000"),
    ("Buses", "Flixbus rescues + Amalfi coast SITA", "\u20b94,500"),
    ("Stays", "4 Airbnbs across 7 nights", "\u20b942,000"),
    ("Food", "Trattorias, Sal De Riso dinner, daily gelato", "\u20b932,000"),
    ("Attractions", "Roma Pass, Vatican, Pisa, museums", "\u20b910,000"),
    ("Local transit", "Vaporetto, metro, validated tickets", "\u20b94,000"),
    ("Souvenirs & extras", "Limoncello, olive oil, lemon chocolates", "\u20b96,000"),
]

CITIES = {
    "rome": {
        "title": "Rome",
        "tagline": "Ancient stones, Trevi coins & the perfect tiramisu",
        "intro": (
            "Rome doesn\u2019t whisper \u2014 it hands history to you on a "
            "paper plate, somewhere between a slice of pizza and a fountain "
            "full of wishes. We landed off the Barcelona flight, fumbled "
            "with the Roma Pass, and let the city do the rest."
        ),
        "top5": [
            ("\ud83c\udfdb\ufe0f", "Colosseum", "80 AD gladiator arena \u2014 still humming."),
            ("\ud83d\udcb0", "Trevi Fountain", "Three coins. One wish. Try the tiramisu next door."),
            ("\ud83c\udfa8", "Vatican City", "St Peter\u2019s, Sistine Chapel, nine miles of museums."),
            ("\ud83c\udfad", "Spanish Steps", "Hepburn-and-gelato territory; ignore the rose sellers."),
            ("\ud83c\udf70", "Two Sizes", "Tiramisu in every flavour. Get more than you think."),
        ],
        "stays": "Airbnb near Termini \u2014 host ran late, a delivery guy let us in. Welcome to Rome.",
        "transit": "Bus from FCO; 24-hour Roma Pass for metro, buses and museum cuts.",
        "food": "Romeo Gelateria near the Spanish Steps, Two Sizes (tiramisu), neighbourhood pizza-and-pasta spot for a no-fuss dinner.",
        "days": "1 day (we should have done 2)",
        "reality_check": "Crowds are real, ticket inspectors are real, and yes \u2014 they do check at the busiest stop, not the quietest.",
        "pins": [
            ("Termini", 0.10, 0.55),
            ("Colosseum", 0.32, 0.40),
            ("Trevi", 0.50, 0.55),
            ("Pantheon", 0.62, 0.62),
            ("Vatican", 0.86, 0.70),
        ],
        "travel_note": "On foot + metro line A \u2014 most of central Rome is walkable.",
    },
    "amalfi": {
        "title": "Amalfi Coast",
        "tagline": "Lemons, cliffs and a candlelit dinner by the Tyrrhenian",
        "intro": (
            "Train from Roma Termini to Salerno, a connection muddle to "
            "Vietri, a gamble back to Salerno, and finally the bus that "
            "hugs the coast. The Tyrrhenian sparkles, the lemon groves "
            "lean in, and every wrong turn turns out to be a postcard."
        ),
        "top5": [
            ("\ud83c\udf0a", "Tyrrhenian drive", "The bus ride is the attraction \u2014 sit on the right."),
            ("\ud83c\udf57", "Sal De Riso", "Candlelit dinner, the famed Delizia al Limone, sea breeze."),
            ("\ud83c\udfd6\ufe0f", "Beach dip & sorbet", "Cold water, cold sorbet, warm afternoon."),
            ("\ud83c\udf74", "Cuoppo d\u2019Amalfi", "Veg-friendly fried cuoppo \u2014 perfect walking food."),
            ("\ud83c\udf85", "Minori apartment", "Two minutes from the pasticceria, fountain across the road."),
        ],
        "stays": "A small apartment in Minori with a fountain and the sea across the road \u2014 quieter and cheaper than Amalfi town itself.",
        "transit": "Train Roma \u2192 Salerno; then SITA bus along the coast. The 6 AM bus back to Salerno is non-negotiable if you have a morning train.",
        "food": "Sal De Riso (sit-down), Pasticceria Sal De Riso (Delizia al Limone), Cuoppo d\u2019Amalfi for veg-friendly fried snacks, lemon sorbet at every other corner.",
        "days": "2 days",
        "reality_check": "Sal De Riso\u2019s seating + cutlery charge is steep; the pastries are not. Buy the lemon chocolates from a supermarket, not a tourist boutique.",
        "pins": [
            ("Salerno", 0.08, 0.40),
            ("Vietri", 0.22, 0.55),
            ("Minori", 0.45, 0.65),
            ("Amalfi town", 0.65, 0.55),
            ("Positano", 0.88, 0.45),
        ],
        "travel_note": "SITA / Flixbus along the coast \u2014 reserve forward seats for the views.",
    },
    "florence": {
        "title": "Florence (& Pisa)",
        "tagline": "An accidental detour that stole our hearts",
        "intro": (
            "We weren\u2019t supposed to be here. The Naples\u2192Florence "
            "bus blew past our stop while we slept, dropped us in Bologna, "
            "and a \u20ac40 Flixbus rescued the day. Florence wasn\u2019t "
            "the plan, and it became the city we most want to come back to."
        ),
        "top5": [
            ("\ud83d\uddfc", "Leaning Tower of Pisa", "55.86 m, 12th-century, beautifully wrong."),
            ("\ud83c\udf55", "Gustapizza", "Two hours of queue. Two minutes of bliss."),
            ("\u26ea", "Duomo & dome", "Brunelleschi\u2019s dome \u2014 the Renaissance, in stone."),
            ("\ud83c\udf09", "Ponte Vecchio", "Medieval bridge of jewellers; sunset works best."),
            ("\ud83c\udf66", "Venchi gelato", "Cold, creamy, ruinous in the best way."),
        ],
        "stays": "Apartment with an elderly host who spoke no English \u2014 hand gestures and warm bread did the rest.",
        "transit": "Flixbus Bologna \u2192 Florence (\u20ac40, cash-saver of the trip); regional train Florence \u2192 Pisa (1.5 hr); 4 AM bus to Villa Costanza for the next leg.",
        "food": "Gustapizza (worth the queue), Venchi gelato, supermarket olive oil + chocolates as souvenirs that survive the flight home.",
        "days": "1 day (next time: 3)",
        "reality_check": "Missed stops, wrong stations, two-hour queues \u2014 and still the highlight of the week. Florence rewards slowing down.",
        "pins": [
            ("Sta. M. Novella", 0.10, 0.65),
            ("Duomo", 0.32, 0.55),
            ("Uffizi", 0.50, 0.40),
            ("Ponte Vecchio", 0.65, 0.50),
            ("Pisa (day trip)", 0.92, 0.70),
        ],
        "travel_note": "Walk the centro storico; train to Pisa for the day-trip.",
    },
    "venice": {
        "title": "Venice",
        "tagline": "Twenty-four hours in a waking dream",
        "intro": (
            "Five AM bus from Florence; we arrived as the canals caught "
            "the first shimmer of light. Venice is often called the Paris "
            "of Italy. It isn\u2019t. It is its own thing \u2014 romantic, "
            "chaotic, and somehow exactly enough in twenty-four hours."
        ),
        "top5": [
            ("\ud83c\udf09", "Rialto Bridge", "1591 stone arch, shops on the deck."),
            ("\ud83d\udc94", "Bridge of Sighs", "Last view of Venice; first kiss at sunset."),
            ("\ud83c\udfdb\ufe0f", "St Mark\u2019s Square", "Europe\u2019s living room."),
            ("\ud83c\udf5d", "I Love Italy (pasta)", "Creamy, simple, divine."),
            ("\ud83c\udf66", "Old corner gelateria", "No frills. Pure magic. Forgot the name. Will find it again."),
        ],
        "stays": "Airbnb on the outer island \u2014 cheaper, quieter and a more honest pulse than the main tourist zone.",
        "transit": "Vaporetto where you must, walking everywhere else. The maze of alleys is the city, not a problem to solve.",
        "food": "I Love Italy (pasta), one tiny gelateria near the canals, risotto cooked in the apartment from a local market haul.",
        "days": "1 day (somehow enough)",
        "reality_check": "The first restaurant we picked was closed on Sunday \u2014 Venice has Sunday rhythms. Don\u2019t over-plan; let the alleys do their thing.",
        "pins": [
            ("Sta. Lucia", 0.08, 0.70),
            ("Rialto", 0.32, 0.55),
            ("St Mark\u2019s", 0.55, 0.40),
            ("Bridge of Sighs", 0.72, 0.50),
            ("Outer island stay", 0.92, 0.30),
        ],
        "travel_note": "Walking + vaporetto line 1 along the Grand Canal.",
    },
}

CITY_URLS = {
    "rome":     "https://desk2destinations.com/italy-rome.html",
    "amalfi":   "https://desk2destinations.com/italy-amalfi.html",
    "florence": "https://desk2destinations.com/italy-florence.html",
    "venice":   "https://desk2destinations.com/italy-venice.html",
}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def _bg(d, w, h, fill):
    d.add(Rect(0, 0, w, h, fillColor=fill, strokeColor=None))


def italy_route_diagram(width=17 * cm, height=6.0 * cm):
    """Country-shaped route map with the four cities pinned in order."""
    d = Drawing(width, height)
    _bg(d, width, height, CREAM)

    # Stylised Italy "boot" silhouette (very abstract)
    d.add(Polygon([
        width * 0.30, height * 0.92,    # north (Alps)
        width * 0.55, height * 0.95,
        width * 0.62, height * 0.78,
        width * 0.50, height * 0.62,
        width * 0.55, height * 0.50,
        width * 0.66, height * 0.45,
        width * 0.62, height * 0.32,
        width * 0.55, height * 0.20,
        width * 0.62, height * 0.10,    # heel
        width * 0.78, height * 0.18,    # boot tip
        width * 0.72, height * 0.30,
        width * 0.50, height * 0.32,
        width * 0.42, height * 0.45,
        width * 0.32, height * 0.65,
        width * 0.22, height * 0.78,
        width * 0.30, height * 0.92,
    ], fillColor=SAND, strokeColor=SAND_LINE, strokeWidth=0.8))

    # Cities (geographic order is Venice → Florence → Rome → Amalfi)
    pins = [
        ("Venice",   0.55, 0.86),
        ("Florence", 0.46, 0.72),
        ("Rome",     0.52, 0.50),
        ("Amalfi",   0.62, 0.32),
    ]
    for i in range(len(pins) - 1):
        _, x1, y1 = pins[i]
        _, x2, y2 = pins[i + 1]
        d.add(Line(width * x1, height * y1, width * x2, height * y2,
                   strokeColor=TERRACOTTA, strokeWidth=1.6,
                   strokeDashArray=[4, 3]))
    for i, (label, x, y) in enumerate(pins):
        cx, cy = width * x, height * y
        d.add(Circle(cx, cy, 7.5, fillColor=TERRACOTTA,
                     strokeColor=colors.white, strokeWidth=1.6))
        d.add(Circle(cx, cy, 2.6, fillColor=colors.white, strokeColor=None))
        # label to the side, alternating
        lx = cx + 12 if i % 2 == 0 else cx - 12
        anchor = "start" if i % 2 == 0 else "end"
        d.add(String(lx, cy - 3, label, fontName="Helvetica-Bold",
                     fontSize=9, fillColor=INK, textAnchor=anchor))

    # Title + caption
    d.add(String(width * 0.5, height - 14,
                 "THE ROUTE \u2014 1 WEEK, 4 CITIES",
                 fontName="Helvetica-Bold", fontSize=10.5,
                 fillColor=TERRACOTTA, textAnchor="middle"))
    d.add(String(width * 0.5, 8,
                 "Trains + buses + one ferry of hope. Always validate.",
                 fontName="Helvetica-Oblique", fontSize=9,
                 fillColor=SOFT_INK, textAnchor="middle"))
    return d


def mini_map(title, places, travel_note, width=17 * cm, height=4.2 * cm):
    """Per-city route map \u2014 same visual language as the country map."""
    d = Drawing(width, height)
    _bg(d, width, height, CREAM)
    d.add(Polygon([
        width * 0.05, height * 0.30,
        width * 0.18, height * 0.65,
        width * 0.40, height * 0.55,
        width * 0.60, height * 0.70,
        width * 0.82, height * 0.55,
        width * 0.95, height * 0.30,
        width * 0.05, height * 0.30,
    ], fillColor=SAND, strokeColor=SAND_LINE, strokeWidth=0.6))
    for i in range(len(places) - 1):
        _, x1, y1 = places[i]
        _, x2, y2 = places[i + 1]
        d.add(Line(width * x1, height * y1, width * x2, height * y2,
                   strokeColor=TERRACOTTA, strokeWidth=1.4,
                   strokeDashArray=[4, 3]))
    for idx, (label, x, y) in enumerate(places):
        cx, cy = width * x, height * y
        d.add(Circle(cx, cy, 6.5, fillColor=TERRACOTTA,
                     strokeColor=colors.white, strokeWidth=1.4))
        d.add(Circle(cx, cy, 2.3, fillColor=colors.white, strokeColor=None))
        below = (idx % 2 == 0)
        ly = cy - 14 if below else cy + 11
        d.add(String(cx, ly, label, fontName="Helvetica-Bold",
                     fontSize=8, fillColor=INK, textAnchor="middle"))
    d.add(String(width * 0.5, height - 12, title.upper(),
                 fontName="Helvetica-Bold", fontSize=10,
                 fillColor=TERRACOTTA, textAnchor="middle"))
    d.add(String(width * 0.5, 6, travel_note,
                 fontName="Helvetica-Oblique", fontSize=8.5,
                 fillColor=SOFT_INK, textAnchor="middle"))
    return d


def badge(num, size=20):
    """Numbered terracotta circle badge for the top-10 page."""
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2 - 0.5,
                 fillColor=TERRACOTTA,
                 strokeColor=TERRACOTTA_DEEP, strokeWidth=0.4))
    d.add(String(size / 2, size / 2 - 3.2, str(num),
                 fontName="Helvetica-Bold", fontSize=10,
                 fillColor=colors.white, textAnchor="middle"))
    return d


def pin_marker(size=12):
    """Small terracotta pin — same visual language as the mini-map pins."""
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2 - 1,
                 fillColor=TERRACOTTA,
                 strokeColor=colors.white, strokeWidth=1.0))
    d.add(Circle(size / 2, size / 2, size / 2 - 4,
                 fillColor=colors.white, strokeColor=None))
    return d


# ---------------------------------------------------------------------------
# Page templates / decorations
# ---------------------------------------------------------------------------
def _cover_decoration(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    # Top + bottom terracotta band
    canvas.setFillColor(TERRACOTTA)
    canvas.rect(0, A4[1] - 18, A4[0], 18, stroke=0, fill=1)
    canvas.rect(0, 0, A4[0], 18, stroke=0, fill=1)
    canvas.restoreState()


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SOFT_INK)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(MARGIN, 1.0 * cm,
                      "Desk2Destinations  \u2022  Italy itinerary")
    canvas.drawRightString(A4[0] - MARGIN, 1.0 * cm,
                           f"{doc.page}")
    canvas.setStrokeColor(RULE_GREY)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, 1.4 * cm, A4[0] - MARGIN, 1.4 * cm)
    canvas.restoreState()


cover_frame = Frame(MARGIN, MARGIN, A4[0] - 2 * MARGIN, A4[1] - 2 * MARGIN,
                    leftPadding=0, rightPadding=0, topPadding=0,
                    bottomPadding=0, showBoundary=0)
body_frame = Frame(MARGIN, MARGIN, A4[0] - 2 * MARGIN, A4[1] - 2 * MARGIN,
                   leftPadding=0, rightPadding=0, topPadding=0,
                   bottomPadding=0.6 * cm, showBoundary=0)


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------
def cover():
    flow = []
    flow.append(Spacer(1, 5.0 * cm))
    flow.append(Paragraph("ITALY", S_COVER_TITLE))
    flow.append(Paragraph("\u2014 Rome \u00b7 Amalfi \u00b7 Florence \u00b7 Venice \u2014",
                          S_COVER_SUB))
    flow.append(Spacer(1, 0.6 * cm))
    flow.append(Paragraph(f"<i>\u201c{ITALY['cover_quote']}\u201d</i>",
                          S_PULLQUOTE))
    flow.append(Spacer(1, 1.2 * cm))
    # A small terracotta divider with a sun/olive motif
    d = Drawing(8 * cm, 1.2 * cm)
    d.add(Line(0, 0.6 * cm, 3 * cm, 0.6 * cm,
               strokeColor=TERRACOTTA, strokeWidth=1.2))
    d.add(Circle(4 * cm, 0.6 * cm, 0.32 * cm, fillColor=GOLD,
                 strokeColor=TERRACOTTA, strokeWidth=0.6))
    d.add(Line(5 * cm, 0.6 * cm, 8 * cm, 0.6 * cm,
               strokeColor=TERRACOTTA, strokeWidth=1.2))
    d.hAlign = "CENTER"
    flow.append(d)
    flow.append(Spacer(1, 1.0 * cm))
    flow.append(Paragraph(
        "<link href='https://desk2destinations.com/'>"
        "<font color='#c86446'><b>desk2destinations.com</b></font></link>"
        "  &middot;  Honesty over hype. Slow over rushed. "
        "Practical over pretty.",
        S_BODY_C,
    ))
    flow.append(Paragraph("By Ayushi & Harshit Jain", S_BODY_C))
    flow.append(NextPageTemplate("Body"))
    flow.append(PageBreak())
    return flow


def at_a_glance():
    flow = []
    flow.append(Paragraph("Italy at a glance", S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=10))
    flow.append(Paragraph(ITALY["at_a_glance_intro"], S_BODY))
    flow.append(Spacer(1, 6))
    flow.append(italy_route_diagram())
    flow.append(Spacer(1, 12))

    facts = [
        ("Best time", ITALY["best_time"]),
        ("Visa (IN)", ITALY["visa"]),
        ("Currency", ITALY["currency"]),
        ("Getting around", ITALY["transit_overall"]),
        ("If we did it again", ITALY["regret"]),
    ]
    rows = [[
        Paragraph(f"<b>{label}</b>", S_BODY),
        Paragraph(value, S_BODY),
    ] for label, value in facts]
    tbl = Table(rows, colWidths=[3.6 * cm, A4[0] - 2 * MARGIN - 3.6 * cm])
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


def top_ten():
    flow = []
    flow.append(Paragraph("The top 10 \u2014 our personal highlights", S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=10))
    flow.append(Paragraph(
        "Ten moments worth flying back for. Ranked roughly in the order "
        "they made us go \u201coh.\u201d",
        S_BODY,
    ))
    flow.append(Spacer(1, 8))

    rows = []
    for i, (icon, title, city, desc) in enumerate(TOP10, start=1):
        rows.append([
            badge(i),
            Paragraph(
                f"<b>{title}</b>  <font color='#c86446' size=9.5>"
                f"\u00b7 {city}</font><br/>"
                f"<font size=9.5 color='#5a5752'>{desc}</font>",
                S_BODY,
            ),
        ])
    tbl = Table(rows, colWidths=[1.2 * cm,
                                 A4[0] - 2 * MARGIN - 1.2 * cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25,
         colors.HexColor("#e6dfd2")),
    ]))
    flow.append(tbl)
    flow.append(PageBreak())
    return flow


def city_section(key):
    c = CITIES[key]
    flow = []
    flow.append(Paragraph(c["title"], S_CITY_H))
    flow.append(Paragraph(c["tagline"], S_CITY_SUB))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=8))
    flow.append(Paragraph(c["intro"], S_BODY))
    flow.append(Spacer(1, 6))

    flow.append(mini_map(c["title"], c["pins"], c["travel_note"]))
    flow.append(Spacer(1, 8))

    flow.append(Paragraph("Top 5 here", S_SECTION))
    rows = []
    for icon, name, note in c["top5"]:
        rows.append([
            pin_marker(),
            Paragraph(
                f"<b>{name}</b>  <font size=9.5 color='#5a5752'>"
                f"\u2014 {note}</font>",
                S_BODY,
            ),
        ])
    tbl = Table(rows, colWidths=[0.8 * cm,
                                 A4[0] - 2 * MARGIN - 0.8 * cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    flow.append(tbl)
    flow.append(Spacer(1, 6))

    facts = [
        ("Days", c["days"]),
        ("Where we stayed", c["stays"]),
        ("Getting around", c["transit"]),
        ("Where we ate", c["food"]),
        ("Reality check", c["reality_check"]),
    ]
    rows = [[
        Paragraph(f"<b>{label}</b>", S_BODY),
        Paragraph(value, S_BODY),
    ] for label, value in facts]
    facts_tbl = Table(rows,
                      colWidths=[3.6 * cm, A4[0] - 2 * MARGIN - 3.6 * cm])
    facts_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25,
         colors.HexColor("#e6dfd2")),
    ]))
    flow.append(facts_tbl)
    flow.append(Spacer(1, 8))

    url = CITY_URLS[key]
    flow.append(Paragraph(
        f"<font size=10 color='#5a5752'>\u2192 Read the full "
        f"{c['title']} guide on the site:&nbsp;</font>"
        f"<link href='{url}'><font size=10 color='#c86446'>"
        f"<b>{url.replace('https://', '')}</b></font></link>",
        S_BODY,
    ))
    flow.append(PageBreak())
    return flow


def costs_and_close():
    flow = []
    flow.append(Paragraph("Costs \u2014 where the rupees went", S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=10))
    flow.append(Paragraph(
        "Mid-range, vegetarian-friendly, two travellers splitting stays. "
        "Numbers are per-person, rounded honestly. Flights vary the most \u2014 "
        "we bought ours 5 weeks out.",
        S_BODY,
    ))
    flow.append(Spacer(1, 8))

    table_data = [[
        Paragraph(f"<b>{a}</b>", S_BODY),
        Paragraph(b, S_BODY),
        Paragraph(f"<b>{c}</b>", S_BODY),
    ] for a, b, c in COSTS]
    tbl = Table(table_data, colWidths=[3.4 * cm, 9.4 * cm,
                                       A4[0] - 2 * MARGIN - 12.8 * cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), TERRACOTTA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3,
         colors.HexColor("#e6dfd2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, CREAM]),
    ]))
    flow.append(tbl)
    flow.append(Spacer(1, 10))
    flow.append(Paragraph(
        f"<b>Total:</b> {ITALY['total']}",
        S_BODY,
    ))
    flow.append(Spacer(1, 16))

    flow.append(Paragraph("One last thing", S_SECTION))
    flow.append(Paragraph(ITALY["transit_note"], S_BODY))
    flow.append(Spacer(1, 8))
    flow.append(Paragraph(
        "Follow <link href='https://www.instagram.com/desk2destinations_'>"
        "<b><font color='#c86446'>@desk2destinations_</font></b></link> on "
        "Instagram for new diaries and reels, or drop us a note via "
        "<link href='https://desk2destinations.com/contact.html'>"
        "<font color='#c86446'><b>desk2destinations.com/contact.html"
        "</b></font></link>. If we got a city wrong, or you want one we "
        "haven\u2019t covered yet \u2014 that\u2019s the place to tell us.",
        S_BODY,
    ))
    return flow


# ---------------------------------------------------------------------------
def build():
    doc = BaseDocTemplate(
        str(TMP_OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Italy Itinerary | Desk2Destinations",
        author="Ayushi & Harshit Jain",
        subject="One-week Italy itinerary, vegetarian-friendly",
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame],
                     onPage=_cover_decoration),
        PageTemplate(id="Body", frames=[body_frame], onPage=_footer),
    ])

    story = []
    story += cover()
    story += at_a_glance()
    story += top_ten()
    for key in ("rome", "amalfi", "florence", "venice"):
        story += city_section(key)
    story += costs_and_close()

    doc.build(story)
    try:
        shutil.move(str(TMP_OUTPUT), str(OUTPUT))
        target = OUTPUT
    except PermissionError:
        target = TMP_OUTPUT
        print(f"  ! {OUTPUT.name} is locked; wrote {TMP_OUTPUT.name} instead")
    size_kb = target.stat().st_size / 1024
    print(f"Wrote {target} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    build()
