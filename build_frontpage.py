#!/usr/bin/env python3
"""Draw THE WORLD's front page for Tuesday 24 November 2026.

The page is a 1024x1024 PNG: masthead, lead story on the Iran-US naval
blockade standoff, a wide illustration strip, a numbers ticker, six
stories in two columns and an ALSO footer. All headlines and figures
come from the story list in README.md, verified against live reporting
on the morning of 25 November 2026 (Beijing time). The only picture is
the illustration already generated into assets/; all lettering is
drawn here with Pillow. Runs offline; no secrets anywhere.
"""

import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ILLUSTRATION = os.path.join(
    BASE,
    "assets",
    "media-generation-hero-naval-blockade-strait-0-8cb99087-db04-406d-b7be-e16827d7a76b.webp",
)
DESTINATION = os.path.join(BASE, "entry.png")

EDGE = 1024
SIDE = 40
INNER = EDGE - 2 * SIDE
BYTE_CAP = 1_000_000

CREAM = (247, 241, 229)
BLACK = (17, 17, 17)
SLATE = (68, 60, 52)
WINE = (143, 29, 29)
MIDNIGHT = (27, 42, 74)
SNOW = (255, 255, 255)

LIB = "/usr/share/fonts/truetype/liberation/"


def load(name, size):
    return ImageFont.truetype(os.path.join(LIB, name), size)


def bold_serif(size):
    return load("LiberationSerif-Bold.ttf", size)


def plain_serif(size):
    return load("LiberationSerif-Regular.ttf", size)


def italic_serif(size):
    return load("LiberationSerif-Italic.ttf", size)


def bold_sans(size):
    return load("LiberationSans-Bold.ttf", size)


def shrink_to_fit(draw, wording, name, top_size, widest):
    """Largest size at which wording fits widest, stepping down by 2."""
    size = top_size
    while size > 10:
        trial = load(name, size)
        if draw.textlength(wording, font=trial) <= widest:
            return trial
        size -= 2
    return load(name, 10)


def split_lines(draw, wording, face, widest):
    """Greedy word wrap measured with the real font."""
    rows = []
    current = ""
    for piece in wording.split():
        joined = f"{current} {piece}".strip()
        if not current or draw.textlength(joined, font=face) <= widest:
            current = joined
        else:
            rows.append(current)
            current = piece
    if current:
        rows.append(current)
    return rows


class Sheet:
    """A blank newsprint page with a vertical cursor."""

    def __init__(self):
        self.canvas = Image.new("RGB", (EDGE, EDGE), CREAM)
        self.pen = ImageDraw.Draw(self.canvas)
        self.cursor = 22

    def width_of(self, wording, face):
        return self.pen.textlength(wording, font=face)

    def put_centred(self, top, wording, face, colour=BLACK):
        self.pen.text(
            ((EDGE - self.width_of(wording, face)) / 2, top),
            wording, font=face, fill=colour,
        )

    def put_tracked(self, top, wording, face, tracking, colour=BLACK):
        spans = [self.width_of(ch, face) for ch in wording]
        whole = sum(spans) + tracking * (len(wording) - 1)
        x = EDGE // 2 - whole / 2
        for glyph, span in zip(wording, spans):
            self.pen.text((x, top), glyph, font=face, fill=colour)
            x += span + tracking

    def rule(self, top, thickness, left=SIDE, right=EDGE - SIDE):
        self.pen.line([(left, top), (right, top)], fill=BLACK, width=thickness)

    def banner(self):
        self.put_tracked(self.cursor, "ONE DAY · ONE PAGE", bold_sans(15), 6, SLATE)
        self.cursor += 30
        masthead = shrink_to_fit(
            self.pen, "THE WORLD", "LiberationSerif-Bold.ttf", 118, INNER)
        self.put_centred(self.cursor - 14, "THE WORLD", masthead)
        self.cursor += 98
        self.rule(self.cursor, 3)
        self.cursor += 5
        self.rule(self.cursor, 1)
        self.cursor += 12
        self.put_centred(
            self.cursor, "TUESDAY,  24 NOVEMBER 2026", bold_serif(30), WINE)
        self.cursor += 42
        self.rule(self.cursor, 1)
        self.cursor += 14

    def headline_block(self):
        top_story = "IRAN VOWS TO FIGHT US BLOCKADE"
        face = shrink_to_fit(
            self.pen, top_story, "LiberationSerif-Bold.ttf", 56, INNER)
        self.put_centred(self.cursor, top_story, face)
        self.cursor += 56
        standfirst = (
            "Tehran says it will use \u201call available means\u201d "
            "against the US naval blockade as Vance and Rubio meet "
            "Qatar\u2019s prime minister at the White House"
        )
        body = plain_serif(22)
        for row in split_lines(self.pen, standfirst, body, INNER - 40):
            self.put_centred(self.cursor, row, body)
            self.cursor += 26
        self.cursor += 8

    def picture_strip(self):
        shot = Image.open(ILLUSTRATION).convert("RGB")
        want = INNER / 140
        wide, tall = shot.size
        if wide / tall > want:
            keep = int(tall * want)
            start = (wide - keep) // 2
            shot = shot.crop((start, 0, start + keep, tall))
        else:
            keep = int(wide / want)
            start = (tall - keep) // 2
            shot = shot.crop((0, start, wide, start + keep))
        shot = shot.resize((INNER, 140), Image.LANCZOS)
        self.canvas.paste(shot, (SIDE, self.cursor))
        self.pen.rectangle(
            [SIDE, self.cursor, EDGE - SIDE, self.cursor + 140],
            outline=BLACK, width=1)
        self.cursor += 140 + 8
        self.pen.text(
            (SIDE, self.cursor),
            "A blockade at sea: warships enforce the cordon as Iran vows "
            "resistance. (Illustration)",
            font=italic_serif(16), fill=SLATE)
        self.cursor += 14

    def number_bar(self):
        tall = 36
        self.pen.rectangle(
            [SIDE, self.cursor, EDGE - SIDE, self.cursor + tall],
            fill=MIDNIGHT)
        figures = (
            "ZAPORIZHZHIA: 2 KILLED, 40 WOUNDED  ·  GAZA: HAMAS "
            "SECURITY CHIEF KILLED  ·  UAE BUS CRASH: 13 DEAD"
        )
        face = shrink_to_fit(
            self.pen, figures, "LiberationSans-Bold.ttf", 19, INNER - 16)
        self.put_centred(self.cursor + 8, figures, face, SNOW)
        self.cursor += tall + 6

    def story(self, left, top, wide, tag, head, text):
        y = top
        self.pen.text((left, y), tag, font=bold_sans(15), fill=WINE)
        y += 22
        head_face = bold_serif(25)
        for row in split_lines(self.pen, head, head_face, wide):
            self.pen.text((left, y), row, font=head_face, fill=BLACK)
            y += 28
        y += 2
        text_face = plain_serif(17)
        for row in split_lines(self.pen, text, text_face, wide):
            self.pen.text((left, y), row, font=text_face, fill=BLACK)
            y += 21
        return y + 10

    def columns(self):
        gap = 30
        wide = (INNER - gap) // 2
        first = SIDE
        second = SIDE + wide + gap
        start = self.cursor

        left_stories = [
            ("UKRAINE",
             "Russian strike kills 2 in Zaporizhzhia",
             "An overnight attack hits an apartment block: two dead and "
             "40 wounded, including four children, the regional governor "
             "says."),
            ("GAZA",
             "Israel kills Hamas security chief",
             "Airstrikes kill Naeem Abu Nahel, director of Hamas\u2019 "
             "internal security, and six others, including two police "
             "officers, medics say."),
            ("KOREA",
             "Russian jets enter Seoul\u2019s air zone",
             "Several Russian aircraft fly into South Korea\u2019s air "
             "defence identification zone over waters between the "
             "peninsula and Japan."),
        ]
        right_stories = [
            ("UNITED ARAB EMIRATES",
             "Bus crash kills 13 in Ras Al Khaimah",
             "A bus carrying 41 people hits a broken-down truck on Al "
             "Watan Road in the early hours; 14 more are injured, police "
             "say."),
            ("NATO",
             "Rutte vows space defence after reports",
             "The alliance will defend against threats in space, its "
             "chief says, after reports Russia is preparing to launch a "
             "nuclear-armed satellite."),
            ("BERLIN",
             "Germany first to tap Ukraine\u2019s Delta",
             "Berlin signs a letter of intent for access to Ukraine\u2019s "
             "Delta battlefield system, with a preliminary deal on "
             "interceptor missiles too."),
        ]
        y = start
        for tag, head, text in left_stories:
            y = self.story(first, y, wide, tag, head, text)
        left_bottom = y
        y = start
        for tag, head, text in right_stories:
            y = self.story(second, y, wide, tag, head, text)
        right_bottom = y
        divider = SIDE + wide + gap // 2
        self.pen.line(
            [(divider, start), (divider, max(left_bottom, right_bottom) - 12)],
            fill=BLACK, width=1)
        self.cursor = max(left_bottom, right_bottom) + 2

    def tail(self):
        self.rule(self.cursor, 1)
        self.cursor += 10
        extras = (
            "ALSO:   Pentagon says Canada falls short as a defence "
            "partner  ·  Democrats probe White House role in Huang\u2019s "
            "Nvidia return  ·  Pope Francis\u2019 diary released"
        )
        face = bold_sans(16)
        for row in split_lines(self.pen, extras, face, INNER):
            self.put_centred(self.cursor, row, face)
            self.cursor += 22
        self.cursor += 2
        self.put_centred(
            self.cursor,
            "Every story above was reported on "
            "Tuesday 24 November 2026.",
            italic_serif(15), SLATE)
        self.cursor += 16

    def finish(self):
        if self.cursor > EDGE:
            raise SystemExit(f"page overflowed: cursor at {self.cursor}")
        self.canvas.save(DESTINATION, format="PNG", optimize=True)
        size = os.path.getsize(DESTINATION)
        print(f"wrote {DESTINATION}: {EDGE}x{EDGE}, {size} bytes, "
              f"cursor ended at y={self.cursor}")
        if size >= BYTE_CAP:
            raise SystemExit(
                f"entry.png is {size} bytes, over the 1 MiB limit")


def build():
    sheet = Sheet()
    sheet.banner()
    sheet.headline_block()
    sheet.picture_strip()
    sheet.number_bar()
    sheet.columns()
    sheet.tail()
    sheet.finish()


if __name__ == "__main__":
    build()
