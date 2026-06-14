"""Generic country itinerary PDF builder (lighter template).

Each country supplies a data dict; this module renders the PDF.

Data shape (see _italy_data for an example):
    COUNTRY = {
        "slug":            "italy",                       # used for filename + URL
        "country_name":    "Italy",                       # cover title
        "subtitle_cities": "Rome \u00b7 Amalfi \u00b7 \u2026",
        "cover_quote":     "...",
        "intro":           "...",                         # at-a-glance opening
        "best_time":       "...",
        "visa":            "...",
        "currency":        "EUR (\u20ac)",
        "transit_overall": "...",
        "regret":          "...",
        "transit_note":    "...",                         # closing one-liner
        "total":           "\u20b9... per person",
        "trip_duration":   "1 week",                      # cover sub
        "top10":  [(title, city, desc), \u2026 \u00d710],
        "costs":  [(category, detail, cost), \u2026],
        "cities": {
            "<key>": {
                "title":    "Rome",
                "tagline":  "...",
                "intro":    "...",
                "top5":     [(name, note), \u2026 \u00d75],
                "stays":    "...",
                "transit":  "...",
                "food":     "...",
                "days":     "...",
                "reality_check": "...",
                "pins":     [(label, x, y), \u2026 \u00d75]   # 0..1 fractions
                "travel_note": "...",
                "url":      "https://desk2destinations.com/italy-rome.html",
            },
            \u2026
        },
        "city_order": ["rome", "amalfi", \u2026],
    }
"""
from __future__ import annotations

from pathlib import Path
import shutil

from reportlab.graphics.shapes import (
    Circle, Drawing, Line, Polygon, Rect, String,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "assets" / "pdfs"

TERRACOTTA = colors.HexColor("#c86446")
TERRACOTTA_DEEP = colors.HexColor("#9c4d34")
INK = colors.HexColor("#1f1d1a")
SOFT_INK = colors.HexColor("#5a5752")
RULE_GREY = colors.HexColor("#d6cfbe")
CREAM = colors.HexColor("#fdf6f0")
SAND = colors.HexColor("#f3e7d4")
SAND_LINE = colors.HexColor("#e2cfaa")
GOLD = colors.HexColor("#d6a857")

MARGIN = 1.6 * cm

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


def _bg(d, w, h, fill):
    d.add(Rect(0, 0, w, h, fillColor=fill, strokeColor=None))


def country_route_diagram(data, width=17 * cm, height=6.0 * cm):
    """Country-level route map. Pulls (label, x, y) pins from data['city_order']
    using each city's first pin as the city anchor — or, if data provides
    'country_pins' explicitly, uses those instead."""
    d = Drawing(width, height)
    _bg(d, width, height, CREAM)
    # Generic country-shaped sand polygon
    d.add(Polygon([
        width * 0.08, height * 0.30,
        width * 0.18, height * 0.78,
        width * 0.40, height * 0.88,
        width * 0.62, height * 0.82,
        width * 0.80, height * 0.62,
        width * 0.92, height * 0.40,
        width * 0.78, height * 0.18,
        width * 0.55, height * 0.12,
        width * 0.30, height * 0.18,
        width * 0.08, height * 0.30,
    ], fillColor=SAND, strokeColor=SAND_LINE, strokeWidth=0.8))

    pins = data.get("country_pins")
    if not pins:
        pins = []
        for key in data["city_order"]:
            c = data["cities"][key]
            label = c["title"].split(" ")[0]
            pins.append((label, 0.5, 0.5))   # fallback flat row
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
        lx = cx + 12 if i % 2 == 0 else cx - 12
        anchor = "start" if i % 2 == 0 else "end"
        d.add(String(lx, cy - 3, label, fontName="Helvetica-Bold",
                     fontSize=9, fillColor=INK, textAnchor=anchor))

    title = f"THE ROUTE \u2014 {data.get('trip_duration', '')}, "\
            f"{len(data['city_order'])} STOPS"
    d.add(String(width * 0.5, height - 14, title.upper(),
                 fontName="Helvetica-Bold", fontSize=10.5,
                 fillColor=TERRACOTTA, textAnchor="middle"))
    d.add(String(width * 0.5, 8, data.get("route_caption", ""),
                 fontName="Helvetica-Oblique", fontSize=9,
                 fillColor=SOFT_INK, textAnchor="middle"))
    return d


def mini_map(title, places, travel_note, width=17 * cm, height=4.2 * cm):
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
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2 - 0.5,
                 fillColor=TERRACOTTA,
                 strokeColor=TERRACOTTA_DEEP, strokeWidth=0.4))
    d.add(String(size / 2, size / 2 - 3.2, str(num),
                 fontName="Helvetica-Bold", fontSize=10,
                 fillColor=colors.white, textAnchor="middle"))
    return d


def pin_marker(size=12):
    d = Drawing(size, size)
    d.add(Circle(size / 2, size / 2, size / 2 - 1,
                 fillColor=TERRACOTTA,
                 strokeColor=colors.white, strokeWidth=1.0))
    d.add(Circle(size / 2, size / 2, size / 2 - 4,
                 fillColor=colors.white, strokeColor=None))
    return d


def _cover_decoration(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    canvas.setFillColor(TERRACOTTA)
    canvas.rect(0, A4[1] - 18, A4[0], 18, stroke=0, fill=1)
    canvas.rect(0, 0, A4[0], 18, stroke=0, fill=1)
    canvas.restoreState()


def _make_footer(country_name):
    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(SOFT_INK)
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(MARGIN, 1.0 * cm,
                          f"Desk2Destinations  \u2022  {country_name} itinerary")
        canvas.drawRightString(A4[0] - MARGIN, 1.0 * cm, f"{doc.page}")
        canvas.setStrokeColor(RULE_GREY)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN, 1.4 * cm, A4[0] - MARGIN, 1.4 * cm)
        canvas.restoreState()
    return _footer


cover_frame = Frame(MARGIN, MARGIN, A4[0] - 2 * MARGIN, A4[1] - 2 * MARGIN,
                    leftPadding=0, rightPadding=0, topPadding=0,
                    bottomPadding=0, showBoundary=0)
body_frame = Frame(MARGIN, MARGIN, A4[0] - 2 * MARGIN, A4[1] - 2 * MARGIN,
                   leftPadding=0, rightPadding=0, topPadding=0,
                   bottomPadding=0.6 * cm, showBoundary=0)


def cover(data):
    flow = []
    flow.append(Spacer(1, 5.0 * cm))
    flow.append(Paragraph(data["country_name"].upper(), S_COVER_TITLE))
    flow.append(Paragraph(f"\u2014 {data['subtitle_cities']} \u2014",
                          S_COVER_SUB))
    flow.append(Spacer(1, 0.6 * cm))
    flow.append(Paragraph(f"<i>\u201c{data['cover_quote']}\u201d</i>",
                          S_PULLQUOTE))
    flow.append(Spacer(1, 1.2 * cm))
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


def at_a_glance(data):
    flow = []
    flow.append(Paragraph(f"{data['country_name']} at a glance", S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=10))
    flow.append(Paragraph(data["intro"], S_BODY))
    flow.append(Spacer(1, 6))
    flow.append(country_route_diagram(data))
    flow.append(Spacer(1, 12))

    facts = [
        ("Best time", data["best_time"]),
        ("Visa (IN)", data["visa"]),
        ("Currency", data["currency"]),
        ("Getting around", data["transit_overall"]),
        ("If we did it again", data["regret"]),
    ]
    rows = [[Paragraph(f"<b>{label}</b>", S_BODY),
             Paragraph(value, S_BODY)] for label, value in facts]
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


def top_ten(data):
    flow = []
    flow.append(Paragraph("The top 10 \u2014 our personal highlights",
                          S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=10))
    flow.append(Paragraph(
        "Ten moments worth flying back for. Ranked roughly in the order "
        "they made us go \u201coh.\u201d",
        S_BODY,
    ))
    flow.append(Spacer(1, 8))
    rows = []
    for i, item in enumerate(data["top10"], start=1):
        title, city, desc = item
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


def city_section(c):
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
    for name, note in c["top5"]:
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
    rows = [[Paragraph(f"<b>{label}</b>", S_BODY),
             Paragraph(value, S_BODY)] for label, value in facts]
    facts_tbl = Table(rows, colWidths=[3.6 * cm,
                                       A4[0] - 2 * MARGIN - 3.6 * cm])
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

    url = c["url"]
    flow.append(Paragraph(
        f"<font size=10 color='#5a5752'>\u2192 Read the full "
        f"{c['title']} guide on the site:&nbsp;</font>"
        f"<link href='{url}'><font size=10 color='#c86446'>"
        f"<b>{url.replace('https://', '')}</b></font></link>",
        S_BODY,
    ))
    flow.append(PageBreak())
    return flow


def costs_and_close(data):
    flow = []
    flow.append(Paragraph("Costs \u2014 where the rupees went", S_PAGE_H))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE_GREY,
                           spaceBefore=0, spaceAfter=10))
    flow.append(Paragraph(
        "Mid-range, vegetarian-friendly, two travellers splitting stays. "
        "Numbers are per-person, rounded honestly. Flights vary the most.",
        S_BODY,
    ))
    flow.append(Spacer(1, 8))
    table_data = [[
        Paragraph(f"<b>{a}</b>", S_BODY),
        Paragraph(b, S_BODY),
        Paragraph(f"<b>{c}</b>", S_BODY),
    ] for a, b, c in data["costs"]]
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
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e6dfd2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CREAM]),
    ]))
    flow.append(tbl)
    flow.append(Spacer(1, 10))
    flow.append(Paragraph(f"<b>Total:</b> {data['total']}", S_BODY))
    flow.append(Spacer(1, 16))

    flow.append(Paragraph("One last thing", S_SECTION))
    flow.append(Paragraph(data["transit_note"], S_BODY))
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


def build_pdf(data):
    out = OUT_DIR / f"desk2destinations-{data['slug']}.pdf"
    tmp = OUT_DIR / f"_desk2destinations-{data['slug']}.tmp.pdf"
    doc = BaseDocTemplate(
        str(tmp), pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"{data['country_name']} Itinerary | Desk2Destinations",
        author="Ayushi & Harshit Jain",
        subject=f"{data['country_name']} itinerary, vegetarian-friendly",
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame],
                     onPage=_cover_decoration),
        PageTemplate(id="Body", frames=[body_frame],
                     onPage=_make_footer(data["country_name"])),
    ])
    story = []
    story += cover(data)
    story += at_a_glance(data)
    story += top_ten(data)
    for key in data["city_order"]:
        story += city_section(data["cities"][key])
    story += costs_and_close(data)
    doc.build(story)
    try:
        shutil.move(str(tmp), str(out))
        target = out
    except PermissionError:
        target = tmp
        print(f"  ! {out.name} is locked; wrote {tmp.name} instead")
    size_kb = target.stat().st_size / 1024
    print(f"Wrote {target.name} ({size_kb:.1f} KB)")
    return target
