"""Generate the polished Japan Itinerary PDF for Desk2Destinations.

Pilot script. Re-run after feedback. Outputs:
  assets/pdfs/desk2destinations-japan.pdf
"""
from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "assets" / "pdfs" / "desk2destinations-japan.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

TERRACOTTA = colors.HexColor("#c86446")
INK = colors.HexColor("#1f1d1a")
SOFT_INK = colors.HexColor("#5a5752")
RULE_GREY = colors.HexColor("#d8d3cb")
TABLE_HEAD_BG = colors.HexColor("#f1ebe2")
TABLE_ALT_BG = colors.HexColor("#faf6ef")

MARGIN = 1.8 * cm
PAGE_W, PAGE_H = A4

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()

S_BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10.5, leading=10.5 * 1.4, textColor=INK,
    alignment=TA_LEFT, spaceAfter=6,
)
S_BODY_J = ParagraphStyle(
    "BodyJ", parent=S_BODY, alignment=TA_JUSTIFY,
)
S_BODY_SOFT = ParagraphStyle(
    "BodySoft", parent=S_BODY, textColor=SOFT_INK,
)
S_PAGE_H = ParagraphStyle(
    "PageHead", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=18, leading=22, textColor=INK, spaceAfter=4,
)
S_SECTION = ParagraphStyle(
    "Section", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=13, leading=16, textColor=INK, spaceBefore=10, spaceAfter=2,
)
S_SUB = ParagraphStyle(
    "Sub", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=11, leading=14, textColor=INK, spaceBefore=6, spaceAfter=2,
)
S_COVER_TITLE = ParagraphStyle(
    "CoverTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=32, leading=36, textColor=INK, alignment=TA_LEFT,
)
S_COVER_SUB = ParagraphStyle(
    "CoverSub", parent=styles["Normal"], fontName="Helvetica",
    fontSize=14, leading=18, textColor=SOFT_INK, alignment=TA_LEFT,
)
S_COVER_META = ParagraphStyle(
    "CoverMeta", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=10.5, leading=14, textColor=TERRACOTTA, alignment=TA_LEFT,
)
S_PULLQUOTE = ParagraphStyle(
    "Pull", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=12, leading=18, textColor=SOFT_INK, alignment=TA_LEFT,
    leftIndent=8, rightIndent=8, spaceBefore=8, spaceAfter=8,
)
S_FOOTNOTE = ParagraphStyle(
    "Note", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=9.5, leading=13, textColor=SOFT_INK,
)
S_BULLET = ParagraphStyle(
    "Bullet", parent=S_BODY, leftIndent=0, bulletIndent=0,
)


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------
def _footer(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SOFT_INK)
    canvas.drawRightString(
        PAGE_W - MARGIN,
        MARGIN * 0.55,
        f"Desk2Destinations  \u00b7  Japan Itinerary  \u00b7  Page {doc.page}",
    )
    canvas.restoreState()


def _cover_decoration(canvas, doc):
    # Terracotta band along the left edge.
    canvas.saveState()
    canvas.setFillColor(TERRACOTTA)
    canvas.rect(0, 0, 0.7 * cm, PAGE_H, stroke=0, fill=1)
    canvas.restoreState()


frame = Frame(
    MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN,
    id="content", showBoundary=0,
)
cover_frame = Frame(
    MARGIN + 0.3 * cm, MARGIN, PAGE_W - 2 * MARGIN - 0.3 * cm,
    PAGE_H - 2 * MARGIN, id="cover", showBoundary=0,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def section(title: str):
    return [
        Spacer(1, 4),
        Paragraph(title, S_SECTION),
        HRFlowable(
            width="22%", thickness=1.6, color=TERRACOTTA,
            spaceBefore=2, spaceAfter=6, lineCap="round",
        ),
    ]


def sub(title: str):
    return Paragraph(title, S_SUB)


def body(text: str, justify: bool = True):
    return Paragraph(text, S_BODY_J if justify else S_BODY)


def numbered(items: list[str]):
    return ListFlowable(
        [ListItem(Paragraph(t, S_BULLET), leftIndent=14) for t in items],
        bulletType="1", start="1", leftIndent=18, bulletFontName="Helvetica-Bold",
        bulletFontSize=10.5, bulletColor=TERRACOTTA, bulletDedent=8,
    )


def bullets(items: list[str]):
    return ListFlowable(
        [ListItem(Paragraph(t, S_BULLET), leftIndent=14) for t in items],
        bulletType="bullet", start="\u2022", leftIndent=14,
        bulletFontSize=10.5, bulletColor=TERRACOTTA, bulletDedent=6,
    )


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
def cover():
    flow = []
    flow.append(Spacer(1, 4 * cm))
    flow.append(Paragraph("JAPAN", S_COVER_META))
    flow.append(Spacer(1, 0.2 * cm))
    flow.append(Paragraph("Japan Itinerary", S_COVER_TITLE))
    flow.append(Spacer(1, 0.15 * cm))
    flow.append(HRFlowable(
        width="35%", thickness=2.2, color=TERRACOTTA,
        spaceBefore=2, spaceAfter=14, lineCap="round",
    ))
    flow.append(Paragraph(
        "Two weeks across Tokyo, Kyoto, Osaka, Hiroshima &amp; Sapporo.",
        S_COVER_SUB,
    ))
    flow.append(Spacer(1, 0.6 * cm))
    flow.append(Paragraph(
        "<i>&ldquo;Tokyo welcomes you with your favourite video game character "
        "&mdash; a giant Mario waving at us before we&rsquo;d even cleared "
        "customs &mdash; and somehow that already feels right.&rdquo;</i>",
        S_PULLQUOTE,
    ))
    flow.append(Spacer(1, 5.5 * cm))
    flow.append(HRFlowable(
        width="100%", thickness=0.6, color=RULE_GREY, spaceAfter=10,
    ))
    flow.append(Paragraph(
        "<b>By Ayushi &amp; Harshit Jain</b>", S_BODY,
    ))
    flow.append(Paragraph(
        "<font color='#c86446'><b>desk2destinations.com</b></font>  &middot;  "
        "Honesty over hype. Slow over rushed. Practical over pretty.",
        S_BODY_SOFT,
    ))
    flow.append(PageBreak())
    return flow


def at_a_glance():
    flow = []
    flow.append(Paragraph("Japan at a glance", S_PAGE_H))
    flow.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=12,
    ))
    flow.append(Paragraph(
        "We did the classic Golden Route plus Hokkaido in two weeks &mdash; "
        "Tokyo, Kyoto, Osaka, a one-day reckoning in Hiroshima, and a quick "
        "Sapporo flight up north. Roughly 1,200 km of Shinkansen, one overnight "
        "Willer bus, one domestic flight. Here is the practical version of "
        "everything we wish someone had handed us before we boarded.",
        S_BODY_J,
    ))

    flow += section("Best time to visit")
    flow.append(body(
        "Cherry blossom season runs late March to early April in Tokyo and "
        "Kyoto; Hokkaido blooms two to three weeks later, so late April "
        "(when we went) is a sweet spot if you want sakura twice. Autumn "
        "(October&ndash;November) is gentler and gives you maple foliage. "
        "December&ndash;February is the ski/snow window in Hokkaido."
    ))

    flow += section("Visa &amp; documents (Indians)")
    flow.append(body(
        "Japan now offers an <b>eVisa for Indian passport holders</b> "
        "&mdash; processing is roughly five working days through the official "
        "VFS portal. Carry the printout. Carry your passport for tax-free "
        "shopping over &yen;5,000 (most drugstores and outlets stamp it on the "
        "spot)."
    ))

    flow += section("Currency, plug, language")
    flow.append(body(
        "Currency: Japanese Yen (JPY); rough thumb rule on our trip was "
        "<b>1 yen \u2248 \u20b90.55</b>. ATMs at 7-Eleven and Lawson reliably "
        "take Indian cards. Plug type A/B (same as US, two flat pins). "
        "English signage is excellent in stations and tourist zones; outside "
        "those, Google Translate's camera mode is your best friend &mdash; "
        "we used it daily on snack packaging."
    ))

    flow += section("Transit")
    flow.append(body(
        "<b>JR Pass</b> for inter-city Shinkansen hops &mdash; the 7-day pass "
        "starts paying off the moment you do a Tokyo&ndash;Kyoto&ndash;"
        "Hiroshima loop. <b>Suica / Pasmo IC card</b> for everything local: "
        "metro, buses, vending machines, and convenience stores. In Kyoto "
        "specifically, switch to a <b>Day Bus Pass</b> &mdash; it breaks "
        "even at four rides and easily clears five on a temple day. For "
        "long hops on a budget, <b>Willer overnight buses</b> are cheaper "
        "than the Shinkansen and surprisingly comfortable."
    ))

    flow += section("Rough daily budget per person (INR)")
    flow.append(bullets([
        "<b>Stays:</b> Hostel bunk \u20b93,000&ndash;5,000 / night (we used "
        "Hostel Wasabi in Asakusa); 3-star hotel \u20b95,000&ndash;8,000 "
        "(Almont Inn, Garner Hotel, Kiori Exec sit here); 5-star "
        "\u20b915,000+ (Sapporo Park Hotel).",
        "<b>Food:</b> \u20b91,500&ndash;3,000 / day if you mix convenience "
        "stores, ramen counters and one nicer meal. Vegan/veg adds about 10%.",
        "<b>Local transit:</b> \u20b9500&ndash;1,500 / day on Suica + day "
        "passes.",
        "<b>JR Pass 7-day:</b> roughly \u20b925,000 per person at the time "
        "we travelled.",
        "<b>Attractions:</b> \u20b9500&ndash;1,500 / day &mdash; most temples "
        "and parks are \u20b9300&ndash;500.",
    ]))

    flow += section("What we'd do differently")
    flow.append(body(
        "Skipping Miyajima to make the overnight Willer bus from Hiroshima "
        "is the one regret of the trip &mdash; the math was tight, but we "
        "should have stayed an extra night. If we did it again, we'd give "
        "Hiroshima a full 36 hours so the floating torii at Itsukushima "
        "isn't a rushed afterthought."
    ))
    flow.append(PageBreak())
    return flow


def top_ten():
    flow = []
    flow.append(Paragraph("Top 10 must-do highlights", S_PAGE_H))
    flow.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    flow.append(Paragraph(
        "Curated from what we actually did, in the order we would tell a "
        "friend to do them. Each one is in our diary somewhere &mdash; no "
        "filler, no second-hand recommendations.",
        S_BODY_J,
    ))
    flow.append(Spacer(1, 4))

    items = [
        "<b>Mt. Fuji day trip from Tokyo</b> &nbsp;<font color='#c86446'>"
        "&middot; Tokyo</font><br/><font size=9.5 color='#5a5752'>Willer "
        "highway bus from a Shibuya mall's 5th floor to Kawaguchiko. "
        "Take the red Fuji loop bus to Oishi Park, then sprint to "
        "Chureito Pagoda for the postcard view.</font>",
        "<b>Senso-ji at 7:30 a.m.</b> &nbsp;<font color='#c86446'>"
        "&middot; Tokyo</font><br/><font size=9.5 color='#5a5752'>"
        "The Asakusa landmark is a different temple before the crowds "
        "arrive &mdash; quiet, almost empty, completely worth the alarm.</font>",
        "<b>Shibuya Crossing &amp; Hachiko</b> &nbsp;<font color='#c86446'>"
        "&middot; Tokyo</font><br/><font size=9.5 color='#5a5752'>"
        "Cross it three times. Then go up for the free upper view from "
        "a mall before lunch at Falafel Brothers in Parco.</font>",
        "<b>Meiji Shrine &amp; the forest in the megacity</b> &nbsp;"
        "<font color='#c86446'>&middot; Tokyo</font><br/>"
        "<font size=9.5 color='#5a5752'>Wine barrels, the oldest wooden "
        "Torii, and a hush that should not exist this close to Shibuya.</font>",
        "<b>Fushimi Inari hike</b> &nbsp;<font color='#c86446'>"
        "&middot; Kyoto</font><br/><font size=9.5 color='#5a5752'>"
        "Walk through the vermilion Torii tunnels to at least the first "
        "viewpoint &mdash; the city opens up below you.</font>",
        "<b>Uji matcha day trip</b> &nbsp;<font color='#c86446'>"
        "&middot; Kyoto</font><br/><font size=9.5 color='#5a5752'>"
        "An hour from Kyoto. Whisked matcha, parfaits, the Murasaki "
        "Shikibu statue, and matcha soba to take home. Most shops shut "
        "by 6 p.m., so go early.</font>",
        "<b>Kinkaku-ji in the rain</b> &nbsp;<font color='#c86446'>"
        "&middot; Kyoto</font><br/><font size=9.5 color='#5a5752'>"
        "The Golden Temple goes liquid in soft rain and the pond doubles "
        "it perfectly. Better than in the sun.</font>",
        "<b>Dotonbori at night + Don Quijote</b> &nbsp;<font color='#c86446'>"
        "&middot; Osaka</font><br/><font size=9.5 color='#5a5752'>"
        "The Glico running man, the canal reflections, the yellow Ferris "
        "wheel above Donki. Block out 3+ hours for Don Quijote alone.</font>",
        "<b>Peace Memorial Park &amp; the A-Bomb Dome</b> &nbsp;"
        "<font color='#c86446'>&middot; Hiroshima</font><br/>"
        "<font size=9.5 color='#5a5752'>Stand in front of the Genbaku "
        "Dome. Walk the park slowly. The 3D projection inside the museum "
        "is essential and difficult.</font>",
        "<b>Hill of the Buddha (Tadao Ando)</b> &nbsp;<font color='#c86446'>"
        "&middot; Sapporo</font><br/><font size=9.5 color='#5a5752'>"
        "1.5 hours out of central Sapporo, but the tunnel approach and "
        "lavender-ringed Buddha statue are worth every minute. Then "
        "ice-cream your way home.</font>",
    ]
    flow.append(numbered(items))
    flow.append(PageBreak())
    return flow


# ----- City sections --------------------------------------------------------
def city_tokyo():
    inner = []
    inner.append(Paragraph("Tokyo", S_PAGE_H))
    inner.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    inner.append(Paragraph(
        "<i>You don't ease into Tokyo. You land, you blink, and you're "
        "already in love.</i> Seven days here, split into two stints &mdash; "
        "Asakusa for the first five, then a quick pit-stop hotel night "
        "before our Sapporo flight, and a final rainy day after.",
        S_BODY_J,
    ))

    inner += section("Top 5 things we did")
    inner.append(numbered([
        "<b>Mt. Fuji from Kawaguchiko &amp; Chureito Pagoda</b> &mdash; via "
        "the Willer highway bus from Shibuya.",
        "<b>Senso-ji at sunrise</b>, then the Asakusa market for daifuku, "
        "baby castella cakes and matcha ice cream.",
        "<b>Shibuya, Meiji Shrine, Harajuku, Shinjuku</b> in one long, "
        "perfect day &mdash; ending at Omoide Yokocho and Golden Gai.",
        "<b>Akihabara at BIC Camera and Yodobashi</b> &mdash; eight to "
        "twelve floors of electronics each. Budget your time wisely.",
        "<b>Jimbocho books district</b> &mdash; the Sanseido publishing-house "
        "store, then a quietly perfect dinner at OBIC&Agrave; in Ginza.",
    ]))

    inner += section("Where we stayed")
    inner.append(body(
        "<b>Hostel Wasabi, Asakusa</b> for the first stretch &mdash; spotless, "
        "a stone's throw from Senso-ji, free luggage hold till early evening. "
        "Then <b>Almont Inn</b> near Tokyo Station for the one-night pit-stop "
        "before our Sapporo flight; they held our suitcases for the two days "
        "we were in Hokkaido."
    ))

    inner += section("Getting around")
    inner.append(body(
        "<b>Suica card</b> on the metro, JR lines and at every Lawson. "
        "<b>Willer Express bus</b> for the Mt. Fuji day trip and the overnight "
        "to Kyoto &mdash; departs from the 5th floor of a Shibuya mall (yes, "
        "really). Tokyo Station is its own underground city; map T's TanTan "
        "or any restaurant inside it before you go in."
    ))

    inner += section("Veg/vegan food picks")
    inner.append(bullets([
        "<b>2foods, Ginza</b> &mdash; vegan burger, smoothie, a quick first-day "
        "lunch.",
        "<b>Fujifuku, Asakusa</b> &mdash; tiny owner-chef-run vegan Japanese "
        "set course; one meal and one drink per person, and one of the warmest "
        "evenings of our trip.",
        "<b>Afuri</b> &mdash; our first proper ramen in Japan, late-night near "
        "Akihabara.",
        "<b>T's TanTan, Tokyo Station</b> &mdash; the famous vegan tantanmen. "
        "Worth the 7:30&ndash;8:30 p.m. station maze.",
        "<b>Falafel Brothers, Parco Shibuya</b> and <b>Komeda's Plant-Based "
        "Kissa, Ginza</b> &mdash; both excellent backups when ramen feels "
        "heavy.",
        "<b>OBIC&Agrave;, Ginza</b> &mdash; date-night Italian on our last "
        "evening, owner sources olive oil straight from Italy.",
    ]))

    inner += section("Day-by-day flow (compressed)")
    inner.append(bullets([
        "<b>Day 1 &mdash; Arrival, Ginza, one-drink rule.</b> "
        "Morning: land at Haneda/Narita, Suica + metro to Hostel Wasabi. "
        "Afternoon: Ginza shopping (Uniqlo, GU, On Shoes), 2foods for lunch. "
        "Evening: GU at Rox Mall in Asakusa, Fujifuku for the set course; "
        "book the Willer bus to Mt. Fuji for the day after next.",
        "<b>Day 2 &mdash; Kappabashi &amp; Akihabara.</b> "
        "Morning: slow start, vegan caf&eacute; pizza. "
        "Afternoon: Kappabashi knife/ceramics street, then BIC Camera "
        "(3pm&ndash;7pm). "
        "Evening: Indian thali at Yodobashi, neon walk through Akihabara.",
        "<b>Day 3 &mdash; The Mt. Fuji Day.</b> "
        "Morning: Senso-ji at 7:30 a.m. (empty), Hachiko, Willer bus from "
        "Shibuya. "
        "Afternoon: Fuji Bus red &amp; green loops, Oishi Park photo "
        "session, ice cream and cookies. "
        "Evening: sprint to Chureito Pagoda, Willer back to Akihabara, "
        "Afuri ramen.",
        "<b>Day 4 &mdash; Shibuya, Shinjuku, Harajuku.</b> "
        "Morning: Meiji Shrine forest. "
        "Afternoon: Shibuya crossing + upper view, Falafel Brothers, "
        "Pok&eacute;mon Center, ABC Mart, Shibuya 109, Takeshita Street "
        "boba. "
        "Evening: Shinjuku neon, Omoide Yokocho, Golden Gai, T's TanTan "
        "at Tokyo Station.",
        "<b>Day 5 &mdash; Asakusa market &amp; Jimbocho.</b> "
        "Morning: Asakusa market snack tour and Senso-ji photos with "
        "crowds. "
        "Afternoon: Jimbocho books district (Kreyszig moment), Ain Soph "
        "in Ginza, Daiso, Sanseido bookstore. "
        "Evening: hostel pickup, Willer overnight bus to Kyoto from 9:40 "
        "p.m.",
        "<b>Day 6 &mdash; Back in Tokyo (pit-stop).</b> "
        "Afternoon: Almont Inn check-in, more Uniqlo Ginza, Komeda's "
        "Plant-Based Kissa. "
        "Evening: pizza on Uber Eats in bed; pack a single backpack for "
        "Sapporo.",
        "<b>Day 7 &mdash; Final day &amp; the Lawson incident.</b> "
        "Morning: 4 a.m. Limousine bus from Sapporo to New Chitose, fly "
        "back through heavy Tokyo rain. "
        "Afternoon: okonomiyaki and plum wine in Asakusa; matcha pilgrimage "
        "(The Matcha House, Hatoya Matcha, Maccha House). "
        "Evening: omikuji at Senso-ji, OBIC&Agrave; dinner in Ginza, the "
        "legendary multi-Suica Lawson incident.",
    ]))

    inner += section("Honest reality check")
    inner.append(body(
        "Tokyo Station is a maze; budget an extra 30&ndash;45 minutes the "
        "first time. Vegan/veg food isn't hard to find &mdash; it's just "
        "slightly pricier, and that's the cost of travel. And Akihabara "
        "rewards walking-around energy, not shopping-list energy &mdash; "
        "we spent four hours in BIC Camera and didn't see half the floors."
    ))
    return KeepTogether(inner) if False else inner  # keep flat for paging


def city_kyoto():
    inner = []
    inner.append(PageBreak())
    inner.append(Paragraph("Kyoto", S_PAGE_H))
    inner.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    inner.append(Paragraph(
        "<i>If Tokyo is acceleration, Kyoto is deceleration.</i> Three slow, "
        "rain-soft, matcha-soaked days. We arrived at Kyoto Station at 5:30 "
        "a.m. on a Willer overnight bus and watched the city slowly wake up.",
        S_BODY_J,
    ))

    inner += section("Top 5 things we did")
    inner.append(numbered([
        "<b>Uji matcha town</b> &mdash; the parfait, the bitter whisked tea, "
        "the matcha soba noodles, and the Murasaki Shikibu bronze statue at "
        "Uji-bashi.",
        "<b>Kiyomizu-dera</b> in soft rain, then Sannenzaka and Ninenzaka "
        "downhill with a warm apple pie.",
        "<b>Kinkaku-ji (Golden Temple)</b> &mdash; even better in the rain.",
        "<b>Fushimi Inari Taisha</b> &mdash; the vermilion Torii tunnels at "
        "1:15 p.m., up to a clearing where the city opens out.",
        "<b>Covered market hopping</b> through Nishiki, Shinkyogoku and "
        "Teramachi when the rain refuses to quit.",
    ]))

    inner += section("Where we stayed")
    inner.append(body(
        "<b>Kiori Exec</b> &mdash; small premium over a hostel, but the "
        "lobby is comfortable enough to nap in at 6:30 a.m. and the staff "
        "actually do bump you into a clean room early. Free umbrellas at "
        "the door (which we used hard on our anniversary day)."
    ))

    inner += section("Getting around")
    inner.append(body(
        "<b>Day Bus Pass</b> over Suica &mdash; Suica was costing us "
        "&yen;320 per ride, the day pass breaks even at four hops and goes "
        "into profit at five. Just don't lose it inside Kinkaku-ji like "
        "Ayushi did. Trains for Uji (about an hour) and Fushimi Inari."
    ))

    inner += section("Veg/vegan food picks")
    inner.append(bullets([
        "<b>Vegan Izakaya</b> &mdash; the gyoza was the best of our entire "
        "Japan trip; thin-skinned, crisp-bottomed, herby. Sake list to match.",
        "<b>Kyoto Engine</b> &mdash; the best ramen we have ever had, full "
        "stop. Vegetarian chilli ramen plus a parfait from a thousand-flavour "
        "display board.",
        "<b>Ain Soph Kyoto</b> &mdash; the burger holds up against the "
        "Ginza branch.",
        "<b>MACCHA HOUSE (\u62b9\u8336\u9928)</b> &mdash; matcha parfait and "
        "the seasonal sakura-strawberry-matcha latte. Outstanding.",
        "<b>Delhi Restaurant, Kyoto</b> &mdash; chole bhature and onion "
        "parantha, run by a Dehradun-wala for 20 years. The right answer for "
        "a rainy anniversary.",
    ]))

    inner += section("Day-by-day flow (compressed)")
    inner.append(bullets([
        "<b>Day 1 &mdash; Arrival &amp; Uji.</b> "
        "Morning: 5:30 a.m. Kyoto Station, lobby nap at Kiori Exec. "
        "Afternoon: late train to Uji (4:30 p.m. start), matcha parfait, "
        "Uji Shrine, Tale of Genji statues. "
        "Evening: Vegan Izakaya gyoza in Kyoto, switch from Suica to a "
        "Day Bus Pass.",
        "<b>Day 2 &mdash; Anniversary, in the rain.</b> "
        "Morning: Kiyomizu-dera, Sannenzaka, Yasaka Pagoda views, apple "
        "pie. "
        "Afternoon: Kinkaku-ji (lost bus pass moment), covered arcade and "
        "3 Coins. "
        "Evening: Delhi Restaurant for chole bhature.",
        "<b>Day 3 &mdash; Fushimi Inari.</b> "
        "Morning: lazy noon brunch at Ain Soph, MACCHA HOUSE parfait. "
        "Afternoon: Fushimi Inari from 1:15 p.m., walking up through the "
        "Torii tunnels. "
        "Evening: skincare run at OS Drugstore + Matsumoto Kiyoshi, then "
        "Kyoto Engine ramen for the road.",
    ]))

    inner += section("Honest reality check")
    inner.append(body(
        "Kyoto refuses to be rushed &mdash; even the rain in Kyoto walks. "
        "If your trip is short, give Kyoto three nights, not two. The kimono "
        "rental we'd planned for the anniversary fell to the rain; the "
        "money was honestly better spent on a second matcha parfait."
    ))
    return inner


def city_osaka():
    inner = []
    inner.append(PageBreak())
    inner.append(Paragraph("Osaka", S_PAGE_H))
    inner.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    inner.append(Paragraph(
        "<i>Tokyo is order. Kyoto is calm. Osaka is the friend who pulls you "
        "into the night with shopping bags and street food and laughs the "
        "loudest.</i> Two days, one castle, six pairs of shoes.",
        S_BODY_J,
    ))

    inner += section("Top 5 things we did")
    inner.append(numbered([
        "<b>Rinku Premium Outlet</b> &mdash; 250 shops, open-air, near "
        "Kansai airport. We walked out with three pairs of Nike at "
        "&#8377;4,000&ndash;6,000.",
        "<b>Osaka Castle grounds</b> on a Sunday &mdash; gold trim, green "
        "roofs, families spread out for picnic.",
        "<b>Don Quijote in Dotonbori</b> &mdash; 3.5 hours of skincare, "
        "snacks, KitKats, matcha lattes. Bring a strong bag.",
        "<b>Dotonbori at night</b> &mdash; Glico running man, the canal, "
        "the giant yellow Ferris wheel above Donki.",
        "<b>Rikuro's Cheesecake</b> at Daimaru Mall &mdash; reach before "
        "the 8 p.m. shutter; eat it in bed.",
    ]))

    inner += section("Where we stayed")
    inner.append(body(
        "<b>Garner Hotel, central Osaka</b> &mdash; loyalty signup got us "
        "free early check-in and two complimentary water bottles. "
        "<b>Quick warning:</b> Garner runs five hotels inside a 3 km radius. "
        "Drop the exact address into Maps before you walk back, otherwise "
        "you'll lobby-walk into the wrong one."
    ))

    inner += section("Getting around")
    inner.append(body(
        "Osaka is barely <b>1 hour 15 minutes from Kyoto</b>. The metro and "
        "the city buses got us everywhere; we used Suica throughout. For "
        "Hiroshima we pre-booked the <b>extra-space seats on the "
        "Shinkansen</b> &mdash; with one large, one medium and one small "
        "suitcase plus a fully-packed backpack, it was the right call."
    ))

    inner += section("Veg/vegan food picks")
    inner.append(bullets([
        "<b>Mercy Vegan Cafe</b> &mdash; small spot near Dotonbori, run "
        "by a lady and her daughter. Cosy, warm, great desserts.",
        "<b>Rikuro's Cheesecake (Daimaru)</b> &mdash; the famous jiggly "
        "Osaka cheesecake; closes at 8 p.m. sharp.",
        "<b>Nepalese roti and sabzi</b> stand near Don Quijote on a "
        "Sunday &mdash; the unplanned reset meal.",
    ]))

    inner += section("Day-by-day flow (compressed)")
    inner.append(bullets([
        "<b>Day 1 &mdash; Rinku Outlet &amp; Rikuro's.</b> "
        "Morning: Kyoto&rarr;Osaka, Garner Hotel check-in, brunch. "
        "Afternoon: Rinku Premium Outlet (2:30&ndash;6 p.m.) &mdash; Nike, "
        "Sketchers, ASICS, Onitsuka Tiger; the KitKat 14-flavour pack we "
        "still regret not buying. "
        "Evening: Rikuro's Cheesecake at Daimaru by 7:45 p.m., ramen "
        "we were too tired to finish.",
        "<b>Day 2 &mdash; Castle, Donki, Dotonbori.</b> "
        "Morning: Osaka Castle and gardens. "
        "Afternoon: Indian roti at the Nepalese spot, then 3.5 hours in "
        "Don Quijote (skincare, KitKats, matcha lattes). "
        "Evening: Mercy Vegan Cafe near Dotonbori, then Glico running man "
        "and a five-store KitKat price hunt (&yen;220&ndash;350 for the "
        "same packet).",
    ]))

    inner += section("Honest reality check")
    inner.append(body(
        "<b>Compare prices across at least two Matsumoto Kiyoshi stores</b> "
        "before bulk buying. Same product, sometimes 20&ndash;30% apart in "
        "the same lane. And if you spot a KitKat 14-flavour gift box, just "
        "buy it; we didn't, and we still talk about it."
    ))
    return inner


def city_hiroshima():
    inner = []
    inner.append(PageBreak())
    inner.append(Paragraph("Hiroshima", S_PAGE_H))
    inner.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    inner.append(Paragraph(
        "<i>If you only saw the rest of Hiroshima &mdash; the trams, the kids "
        "on bikes, the lemon sorbet by the lake &mdash; you'd never believe "
        "what this city has lived through.</i> One full day, packed.",
        S_BODY_J,
    ))

    inner += section("Top 5 things we did")
    inner.append(numbered([
        "<b>The A-Bomb Dome (Genbaku Dome)</b> &mdash; left exactly as it "
        "was on 6 August 1945. Stand in front of it. Read the plaque slowly.",
        "<b>Peace Memorial Museum</b> &mdash; the 3D projection sequence "
        "reconstructs the bombing minute by minute; the burnt tricycle and "
        "the stopped watch will stay with you.",
        "<b>Peace Memorial Park</b> &mdash; the Cenotaph arch frames the "
        "Dome by design; walk it slowly.",
        "<b>Hondori Arcade</b> &mdash; covered shopping street near the "
        "park; we found a Sketchers outlet here.",
        "<b>Lakeside lemon sorbet</b> at a Caff&egrave; Ponte by the river "
        "&mdash; the city's quiet way of telling you to breathe.",
    ]))

    inner += section("Where we stayed")
    inner.append(body(
        "<b>We didn't stay overnight in Hiroshima.</b> We came in by "
        "Shinkansen at 7:50 a.m. from Osaka, dumped luggage in a station "
        "locker, and left on the overnight Willer bus to Tokyo at 6:05 "
        "p.m. Hostels and Booking.com hotels around Hiroshima Station are "
        "your best bet if you want a slower visit (which, with hindsight, "
        "we recommend)."
    ))

    inner += section("Getting around")
    inner.append(body(
        "<b>Hiroshima Day Pass</b> + the friendly <b>red Hiroshima "
        "sightseeing loop bus</b> covers the Dome, Peace Park, museum and "
        "the regular city in one ticket. The trams are quietly wonderful "
        "if you have time to spare. Station lockers are reliable; ours held "
        "two suitcases and a backpack for the day."
    ))

    inner += section("Veg/vegan food picks")
    inner.append(bullets([
        "<b>Vegetarian onigiri</b> from the convenience stores at Osaka "
        "Station &mdash; carry these on the Shinkansen.",
        "<b>Indian restaurant near Peace Park</b> &mdash; not glamorous, "
        "but a reliable veg lunch when the okonomiyaki queue is around the "
        "block.",
        "<b>Hiroshima okonomiyaki</b> &mdash; the layered, noodle-stacked "
        "Hiroshima version is the city's signature; queue if you can.",
    ]))

    inner += section("Day flow (compressed)")
    inner.append(bullets([
        "<b>Morning:</b> 7:50 a.m. Shinkansen out of Osaka, vegetarian "
        "onigiri hunt before boarding; arrive Hiroshima just before 10. "
        "Lockers, day pass, red loop bus to the Dome.",
        "<b>Midday:</b> A-Bomb Dome, Cenotaph, full Peace Memorial Museum "
        "(3D projection at the heart of it).",
        "<b>Afternoon:</b> Indian-restaurant lunch by 2 p.m.; Hondori "
        "arcade, Sketchers; lemon sorbet by the river. Skip Miyajima if "
        "you must &mdash; we did, and regret it.",
        "<b>Evening:</b> 6:05 p.m. Willer overnight bus to Tokyo from a "
        "bus terminal on a mall's upper floor. Confirm the floor before "
        "you arrive.",
    ]))

    inner += section("Honest reality check")
    inner.append(body(
        "One day is too tight. Miyajima Island and the floating Itsukushima "
        "torii is a 2.5-hour round trip and we couldn't fit it before our "
        "overnight bus. Stay a night. Plan a half-day for Miyajima at "
        "minimum &mdash; it is the visit we will come back for."
    ))
    return inner


def city_sapporo():
    inner = []
    inner.append(PageBreak())
    inner.append(Paragraph("Sapporo", S_PAGE_H))
    inner.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    inner.append(Paragraph(
        "<i>Hokkaido is the version of Japan no one warns you about &mdash; "
        "quieter, colder, bigger, and somehow more generous.</i> Two days. "
        "Late-season sakura, sulphur volcanoes, and an indecent amount of "
        "ice cream.",
        S_BODY_J,
    ))

    inner += section("Top 5 things we did")
    inner.append(numbered([
        "<b>Hill of the Buddha (Tadao Ando)</b> &mdash; tunnel approach, "
        "lavender field, Buddha reveal. About 1.5 hours from central "
        "Sapporo; absolutely worth it.",
        "<b>Late-season sakura walk</b> &mdash; get off one bus stop "
        "before yours and just walk. Hokkaido blooms two to three weeks "
        "after Honshu.",
        "<b>Pole Town arcade</b> &mdash; a kilometre of underground shops, "
        "warm even in cold weather, gloriously easy to get lost in.",
        "<b>Noboribetsu Hell Valley</b> &mdash; sulphur, steam, red-orange "
        "rock; a film-set landscape.",
        "<b>Lake Toya + two surprise dairy farms</b> &mdash; calm "
        "mountain-ringed water, then yogurt and ice cream tastings.",
    ]))

    inner += section("Where we stayed")
    inner.append(body(
        "<b>Sapporo Park Hotel</b> &mdash; our first proper 5-star of the "
        "trip, but Japan's 5-star is service and finish, not amenity "
        "overload. Beautiful lobby, comfortable bed, no AC (it's Hokkaido "
        "in April), thin white curtains let the 4:30 a.m. sunrise wake us "
        "up the second morning. Recalibrate your expectations and you'll "
        "love it."
    ))

    inner += section("Getting around")
    inner.append(body(
        "<b>Airport Limousine Bus</b> from central Tokyo to Haneda at "
        "5 a.m. &mdash; quietly genius. <b>New Chitose Airport bus</b> on "
        "the other end (~1 hr 15 min into Sapporo). Inside the city, the "
        "metro and Pole Town walking will get you most places. For Day 2 "
        "we booked a <b>tour bus</b> for Noboribetsu, Bear Ranch, Mount "
        "Usu and Lake Toya &mdash; Hokkaido's modest public transport "
        "can't link those in a day; the guide carries the cognitive load."
    ))

    inner += section("Veg/vegan food picks")
    inner.append(bullets([
        "<b>Holistic Bio Caf&eacute; Veggy Way</b> &mdash; gentle, "
        "plant-forward; the right reset after a 5 a.m. start.",
        "<b>Kintoya Bake</b> &mdash; warm baked cheese tarts, almost "
        "custardy inside.",
        "<b>Donguri</b> &mdash; the legendary tray-and-tongs bakery; we "
        "raided it twice.",
        "<b>Hokkaido soft-serve ice cream</b> &mdash; Pole Town, Mount Usu "
        "stop, two surprise farms by Lake Toya. Each region's milk tastes "
        "a little different, so each cone is research.",
    ]))

    inner += section("Day-by-day flow (compressed)")
    inner.append(bullets([
        "<b>Day 1 &mdash; Hill of the Buddha + Pole Town.</b> "
        "Morning: 5 a.m. Limousine Bus, 7:20 a.m. flight Haneda&rarr;New "
        "Chitose. "
        "Afternoon: Hill of the Buddha, late-season sakura walk back. "
        "Evening: Holistic Bio Caf&eacute;, Pole Town wandering, Kintoya "
        "Bake + Donguri haul.",
        "<b>Day 2 &mdash; Tour bus through Hokkaido.</b> "
        "Morning: 8 a.m. departure from Sapporo Station, Noboribetsu Hell "
        "Valley. "
        "Afternoon: Bear Ranch / Mount Usu base (we shopped instead), "
        "vegan ramen, Lake Toya, two surprise dairy farms. "
        "Evening: back to Sapporo by 4 p.m., Odori Park, Sapporo TV Tower, "
        "second Donguri raid, pack for the 4 a.m. flight to Tokyo.",
    ]))

    inner += section("Honest reality check")
    inner.append(body(
        "Two days is not enough. Hokkaido feels like its own country. If "
        "you've already seen New Zealand's geothermal landscapes, "
        "Noboribetsu may feel a little thunder-stolen &mdash; which is on "
        "us, not the place. Also: skipping the Bear Ranch and Mount Usu "
        "ropeway tickets to shop instead is the call we don't regret."
    ))
    return inner


def costs_and_close():
    flow = []
    flow.append(PageBreak())
    flow.append(Paragraph("Costs &amp; closing", S_PAGE_H))
    flow.append(HRFlowable(
        width="100%", thickness=1.2, color=TERRACOTTA, spaceAfter=10,
    ))
    flow.append(Paragraph(
        "Per-person estimates in Indian Rupees, based on what we paid in "
        "April&ndash;May 2026 plus rounded-up ranges for things you might "
        "do differently. Treat <b>Mid</b> as the most realistic plan.",
        S_BODY_J,
    ))

    data = [
        ["Item", "Low", "Mid", "High"],
        ["Flights ex-India (return)", "55,000", "75,000", "1,10,000"],
        ["JR Pass 7-day", "25,000", "25,000", "32,000"],
        ["Hostel bunk / night", "3,000", "4,000", "5,000"],
        ["3-star hotel / night", "5,000", "6,500", "8,500"],
        ["Food / day per person", "1,500", "2,200", "3,000"],
        ["Attractions / day", "500", "1,000", "1,500"],
        ["Local transit / day", "500", "900", "1,500"],
        ["Tokyo\u2192Kyoto Willer bus", "2,500", "3,200", "4,500"],
        ["Hiroshima\u2192Tokyo Willer bus", "5,000", "6,500", "8,500"],
        ["Sapporo flight (one-way)", "4,000", "5,500", "8,000"],
    ]
    table = Table(
        data, colWidths=[7.0 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, TERRACOTTA),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.25, RULE_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(table)
    flow.append(Spacer(1, 6))
    flow.append(Paragraph(
        "<i>Numbers are estimates &mdash; exchange rate, season and your "
        "own pace will move them.</i>",
        S_FOOTNOTE,
    ))

    flow += section("Total for a 14-day Japan trip per person (mid-range)")
    flow.append(body(
        "Roughly <b>\u20b92,80,000&ndash;3,20,000 per person</b>, all-in "
        "&mdash; flights + JR Pass + accommodation + food + attractions + "
        "intercity buses + the Sapporo flight. Skew higher if you stay in "
        "4&ndash;5-star hotels or shop at Rinku Outlet the way we did. "
        "<b>This is an estimate, not a quote.</b>"
    ))

    flow += section("If this was useful")
    flow.append(body(
        "Follow <b>@desk2destinations_</b> on Instagram for new diaries "
        "and reels, or drop us a note via "
        "<font color='#c86446'><b>desk2destinations.com/contact.html</b></font>. "
        "We read every message. If you spot something off in this PDF or "
        "want a city we haven't covered yet, that's the place to tell us."
    ))
    flow.append(Spacer(1, 0.4 * cm))
    flow.append(Paragraph(
        "<font color='#5a5752'>Honesty over hype. Slow over rushed. "
        "Practical over pretty.</font><br/><b>&mdash; Ayushi &amp; Harshit "
        "Jain</b>",
        S_BODY,
    ))
    return flow


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build():
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Japan Itinerary | Desk2Destinations",
        author="Ayushi & Harshit Jain",
        subject="Two-week Japan itinerary, vegetarian-friendly",
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame],
                     onPage=_cover_decoration),
        PageTemplate(id="Body", frames=[frame], onPage=_footer),
    ])

    story = []
    story += cover()
    story.append(_NextTemplateMarker("Body"))
    story += at_a_glance()
    story += top_ten()
    story += city_tokyo()
    story += city_kyoto()
    story += city_osaka()
    story += city_hiroshima()
    story += city_sapporo()
    story += costs_and_close()

    doc.build(story)
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Wrote {OUTPUT} ({size_kb:.1f} KB)")


# Tiny helper flowable to switch page templates mid-story.
from reportlab.platypus.flowables import Flowable


class _NextTemplateMarker(Flowable):
    def __init__(self, template_id: str):
        super().__init__()
        self.template_id = template_id
        self.width = 0
        self.height = 0

    def draw(self):
        pass

    def wrap(self, *_):
        return 0, 0


# Reach into BaseDocTemplate to honour the marker.
from reportlab.platypus.doctemplate import NextPageTemplate


def build_v2():
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Japan Itinerary | Desk2Destinations",
        author="Ayushi & Harshit Jain",
    )
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame],
                     onPage=_cover_decoration),
        PageTemplate(id="Body", frames=[frame], onPage=_footer),
    ])

    story = []
    story += cover()  # ends with PageBreak
    # After cover page, switch to Body template for the rest.
    # We insert the NextPageTemplate before the cover's PageBreak so the
    # very next page uses Body.
    # Find the trailing PageBreak in cover and swap:
    if isinstance(story[-1], PageBreak):
        story.insert(len(story) - 1, NextPageTemplate("Body"))
    story += at_a_glance()
    story += top_ten()
    story += city_tokyo()
    story += city_kyoto()
    story += city_osaka()
    story += city_hiroshima()
    story += city_sapporo()
    story += costs_and_close()

    doc.build(story)
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Wrote {OUTPUT} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    build_v2()
