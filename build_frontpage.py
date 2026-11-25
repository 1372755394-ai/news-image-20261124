#!/usr/bin/env python3
"""Draw the front page of THE WORLD for Tuesday 24 November 2026.

Everything on the page comes from README.md: the Iran-US blockade
standoff as the lead, the Zaporizhzhia strike, the Gaza strikes, the
Ras Al Khaimah bus crash, Russian jets in Seoul's air zone, NATO's
space warning and Germany's Delta deal, each verified against live
reporting on the morning of 25 November 2026 (Beijing time). The
picture strip uses the illustration already sitting in assets/;
every letter is drawn here. The result is a 1024x1024 PNG under
1 MiB. Pillow only, no network, no secrets.
"""

import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
PICTURE = os.path.join(
    ROOT,
    "assets",
    "media-generation-hero-naval-blockade-strait-0-8cb99087-db04-406d-b7be-e16827d7a76b.webp",
)
TARGET = os.path.join(ROOT, "entry.png")

CANVAS_EDGE = 1024
EDGE_GAP = 40
TEXT_WIDTH = CANVAS_EDGE - 2 * EDGE_GAP
SIZE_CAP = 1_000_000
STRIP_HEIGHT = 140

PALETTE = {
    "paper": (247, 241, 229),
    "ink": (17, 17, 17),
    "grey": (68, 60, 52),
    "red": (143, 29, 29),
    "navy": (27, 42, 74),
    "white": (255, 255, 255),
}

FACES = {
    "serif_b": "LiberationSerif-Bold.ttf",
    "serif": "LiberationSerif-Regular.ttf",
    "serif_i": "LiberationSerif-Italic.ttf",
    "sans_b": "LiberationSans-Bold.ttf",
}
FONT_HOME = "/usr/share/fonts/truetype/liberation/"


def face(kind, size):
    return ImageFont.truetype(os.path.join(FONT_HOME, FACES[kind]), size)


def measure(draw, text, font):
    return draw.textlength(text, font=font)


def fit_to_width(draw, text, kind, biggest, width):
    """Shrink the point size until the text fits, two points at a time."""
    size = biggest
    while size > 10:
        candidate = face(kind, size)
        if measure(draw, text, candidate) <= width:
            return candidate
        size -= 2
    return face(kind, 10)


def break_text(draw, text, font, width):
    """Greedy pixel-exact wrap, walked with an index pointer.

    Words are consumed left to right; each row takes the longest run
    of words that still measures within the width.
    """
    words = text.split()
    rows = []
    first = 0
    while first < len(words):
        last = first
        row = ""
        while last < len(words):
            trial = (row + " " + words[last]).strip()
            if row and measure(draw, trial, font) > width:
                break
            row, last = trial, last + 1
        rows.append(row)
        first = last
    return rows


def centred(draw, top, text, font, colour):
    x = (CANVAS_EDGE - measure(draw, text, font)) / 2
    draw.text((x, top), text, font=font, fill=colour)


def letterspaced(draw, top, text, font, step, colour):
    spans = [measure(draw, ch, font) for ch in text]
    total = sum(spans) + step * (len(text) - 1)
    x = CANVAS_EDGE / 2 - total / 2
    for glyph, span in zip(text, spans):
        draw.text((x, top), glyph, font=font, fill=colour)
        x += span + step


def rule(draw, top, weight):
    draw.line(
        [(EDGE_GAP, top), (CANVAS_EDGE - EDGE_GAP, top)],
        fill=PALETTE["ink"], width=weight,
    )


def draw_masthead(draw, y):
    letterspaced(draw, y, "ONE DAY · ONE PAGE", face("sans_b", 15), 6,
                 PALETTE["grey"])
    y += 30
    title = fit_to_width(draw, "THE WORLD", "serif_b", 118, TEXT_WIDTH)
    centred(draw, y - 14, "THE WORLD", title, PALETTE["ink"])
    y += 98
    rule(draw, y, 3)
    y += 5
    rule(draw, y, 1)
    y += 12
    centred(draw, y, "TUESDAY,  24 NOVEMBER 2026", face("serif_b", 30),
            PALETTE["red"])
    y += 42
    rule(draw, y, 1)
    return y + 14


def draw_lead(draw, y):
    headline = "IRAN VOWS TO FIGHT US BLOCKADE"
    big = fit_to_width(draw, headline, "serif_b", 56, TEXT_WIDTH)
    centred(draw, y, headline, big, PALETTE["ink"])
    y += 56
    deck = (
        "Tehran says it will use \u201call available means\u201d against "
        "the US naval blockade as Vance and Rubio meet Qatar\u2019s prime "
        "minister at the White House"
    )
    small = face("serif", 22)
    for line in break_text(draw, deck, small, TEXT_WIDTH - 40):
        centred(draw, y, line, small, PALETTE["ink"])
        y += 26
    return y + 8


def draw_picture(page, draw, y):
    shot = Image.open(PICTURE).convert("RGB")
    fitted = ImageOps.fit(shot, (TEXT_WIDTH, STRIP_HEIGHT))
    page.paste(fitted, (EDGE_GAP, y))
    draw.rectangle(
        [EDGE_GAP, y, CANVAS_EDGE - EDGE_GAP, y + STRIP_HEIGHT],
        outline=PALETTE["ink"], width=1)
    y += STRIP_HEIGHT + 8
    draw.text(
        (EDGE_GAP, y),
        "A blockade at sea: warships enforce the cordon as Iran vows "
        "resistance. (Illustration)",
        font=face("serif_i", 16), fill=PALETTE["grey"])
    return y + 14


def draw_ticker(draw, y):
    bar = 36
    draw.rectangle(
        [EDGE_GAP, y, CANVAS_EDGE - EDGE_GAP, y + bar],
        fill=PALETTE["navy"])
    parts = [
        "ZAPORIZHZHIA: 2 KILLED, 40 WOUNDED",
        "GAZA: HAMAS SECURITY CHIEF KILLED",
        "UAE BUS CRASH: 13 DEAD",
    ]
    line = "  ·  ".join(parts)
    font = fit_to_width(draw, line, "sans_b", 19, TEXT_WIDTH - 16)
    centred(draw, y + 8, line, font, PALETTE["white"])
    return y + bar + 6


def draw_story(draw, x, y, width, tag, headline, body):
    draw.text((x, y), tag, font=face("sans_b", 15), fill=PALETTE["red"])
    y += 22
    head_font = face("serif_b", 25)
    for line in break_text(draw, headline, head_font, width):
        draw.text((x, y), line, font=head_font, fill=PALETTE["ink"])
        y += 28
    y += 2
    body_font = face("serif", 17)
    for line in break_text(draw, body, body_font, width):
        draw.text((x, y), line, font=body_font, fill=PALETTE["ink"])
        y += 21
    return y + 10


STORIES = [
    ("UKRAINE", "Russian strike kills 2 in Zaporizhzhia",
     "An overnight attack hits an apartment block: two dead and 40 "
     "wounded, including four children, the regional governor says."),
    ("UNITED ARAB EMIRATES", "Bus crash kills 13 in Ras Al Khaimah",
     "A bus carrying 41 people hits a broken-down truck on Al Watan "
     "Road in the early hours; 14 more are injured, police say."),
    ("GAZA", "Israel kills Hamas security chief",
     "Airstrikes kill Naeem Abu Nahel, director of Hamas\u2019 internal "
     "security, and six others, including two police officers, medics "
     "say."),
    ("NATO", "Rutte vows space defence after reports",
     "The alliance will defend against threats in space, its chief "
     "says, after reports Russia is preparing to launch a "
     "nuclear-armed satellite."),
    ("KOREA", "Russian jets enter Seoul\u2019s air zone",
     "Several Russian aircraft fly into South Korea\u2019s air defence "
     "identification zone over waters between the peninsula and Japan."),
    ("BERLIN", "Germany first to tap Ukraine\u2019s Delta",
     "Berlin signs a letter of intent for access to Ukraine\u2019s Delta "
     "battlefield system, with a preliminary deal on interceptor "
     "missiles too."),
]


def draw_columns(draw, y):
    gap = 30
    col_width = (TEXT_WIDTH - gap) // 2
    starts = [EDGE_GAP, EDGE_GAP + col_width + gap]
    bottoms = [y, y]
    for index, (tag, headline, body) in enumerate(STORIES):
        column = index % 2
        bottoms[column] = draw_story(
            draw, starts[column], bottoms[column], col_width,
            tag, headline, body)
    middle = EDGE_GAP + col_width + gap // 2
    draw.line(
        [(middle, y), (middle, max(bottoms) - 12)],
        fill=PALETTE["ink"], width=1)
    return max(bottoms) + 2


def draw_footer(draw, y):
    rule(draw, y, 1)
    y += 10
    extras = (
        "ALSO:   Pentagon says Canada falls short as a defence partner  ·  "
        "Democrats probe White House role in Huang\u2019s Nvidia return  ·  "
        "Pope Francis\u2019 diary released"
    )
    small = face("sans_b", 16)
    for line in break_text(draw, extras, small, TEXT_WIDTH):
        centred(draw, y, line, small, PALETTE["ink"])
        y += 22
    y += 2
    centred(
        draw, y,
        "Every story above was reported on Tuesday 24 November 2026.",
        face("serif_i", 15), PALETTE["grey"])
    return y + 16


def main():
    page = Image.new("RGB", (CANVAS_EDGE, CANVAS_EDGE), PALETTE["paper"])
    draw = ImageDraw.Draw(page)
    y = 22
    y = draw_masthead(draw, y)
    y = draw_lead(draw, y)
    y = draw_picture(page, draw, y)
    y = draw_ticker(draw, y)
    y = draw_columns(draw, y)
    y = draw_footer(draw, y)
    if y > CANVAS_EDGE:
        raise SystemExit(f"page overflowed: cursor at {y}")
    page.save(TARGET, format="PNG", optimize=True)
    size = os.path.getsize(TARGET)
    print(f"wrote {TARGET}: {CANVAS_EDGE}x{CANVAS_EDGE}, {size} bytes, "
          f"cursor ended at y={y}")
    if size >= SIZE_CAP:
        raise SystemExit(f"entry.png is {size} bytes, over the 1 MiB limit")


if __name__ == "__main__":
    main()
