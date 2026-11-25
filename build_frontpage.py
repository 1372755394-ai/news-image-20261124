#!/usr/bin/env python3
"""Render the 24 November 2026 front page of THE WORLD as a 1024x1024 PNG.

Every headline and figure follows the story list in README.md, checked
against live news on the morning of 25 November 2026 (Beijing time):
Just Security's Early Edition for 24 November, Reuters, Gulf Business /
Khaleej Times, the Kyiv Independent and the BBC. The only picture is the
pre-generated hero illustration in assets/; every word on the page is
drawn here with PIL. No network access, no secrets.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HERO_PATH = os.path.join(
    HERE,
    "assets",
    "media-generation-hero-naval-blockade-strait-0-8cb99087-db04-406d-b7be-e16827d7a76b.webp",
)
OUT_PATH = os.path.join(HERE, "entry.png")

SIZE = 1024
MARGIN = 40
CONTENT = SIZE - 2 * MARGIN
MAX_BYTES = 1_000_000

PAPER = (247, 241, 229)
INK = (17, 17, 17)
GREY = (68, 60, 52)
CRIMSON = (143, 29, 29)
DEEP_BLUE = (27, 42, 74)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"


def fnt(filename, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, filename), size)


def serif_bold(size):
    return fnt("LiberationSerif-Bold.ttf", size)


def serif_plain(size):
    return fnt("LiberationSerif-Regular.ttf", size)


def serif_italic(size):
    return fnt("LiberationSerif-Italic.ttf", size)


def sans_bold(size):
    return fnt("LiberationSans-Bold.ttf", size)


def fit_font(draw, text, filename, start_size, max_width):
    size = start_size
    while size > 10:
        candidate = fnt(filename, size)
        if draw.textlength(text, font=candidate) <= max_width:
            return candidate
        size -= 2
    return fnt(filename, 10)


def wrap_lines(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        attempt = (current + " " + word).strip()
        if not current or draw.textlength(attempt, font=font) <= max_width:
            current = attempt
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Page:
    def __init__(self):
        self.sheet = Image.new("RGB", (SIZE, SIZE), PAPER)
        self.draw = ImageDraw.Draw(self.sheet)
        self.y = 22

    def text_width(self, text, font):
        return self.draw.textlength(text, font=font)

    def centred(self, y, text, font, fill=INK):
        self.draw.text(
            (SIZE // 2 - self.text_width(text, font) / 2, y),
            text, font=font, fill=fill,
        )

    def spaced(self, y, text, font, gap, fill=INK):
        widths = [self.draw.textlength(ch, font=font) for ch in text]
        total = sum(widths) + gap * (len(text) - 1)
        x = SIZE // 2 - total / 2
        for ch, w in zip(text, widths):
            self.draw.text((x, y), ch, font=font, fill=fill)
            x += w + gap

    def hline(self, y, weight, x0=MARGIN, x1=SIZE - MARGIN):
        self.draw.line([(x0, y), (x1, y)], fill=INK, width=weight)

    def masthead(self):
        self.spaced(self.y, "ONE DAY · ONE PAGE", sans_bold(15), 6, GREY)
        self.y += 30
        title = fit_font(
            self.draw, "THE WORLD", "LiberationSerif-Bold.ttf", 118, CONTENT)
        self.centred(self.y - 14, "THE WORLD", title)
        self.y += 98
        self.hline(self.y, 3)
        self.y += 5
        self.hline(self.y, 1)
        self.y += 12
        self.centred(
            self.y, "TUESDAY,  24 NOVEMBER 2026", serif_bold(30), CRIMSON)
        self.y += 42
        self.hline(self.y, 1)
        self.y += 14

    def lead(self):
        headline = "IRAN VOWS TO FIGHT US BLOCKADE"
        head_font = fit_font(
            self.draw, headline, "LiberationSerif-Bold.ttf", 56, CONTENT)
        self.centred(self.y, headline, head_font)
        self.y += 56
        deck = ("Tehran says it will use \u201call available means\u201d "
                "against the US naval blockade as Vance and Rubio meet "
                "Qatar\u2019s prime minister at the White House")
        deck_font = serif_plain(22)
        for line in wrap_lines(self.draw, deck, deck_font, CONTENT - 40):
            self.centred(self.y, line, deck_font)
            self.y += 26
        self.y += 8

    def hero(self):
        photo = Image.open(HERO_PATH).convert("RGB")
        ratio = CONTENT / 140
        sw, sh = photo.size
        if sw / sh > ratio:
            nw = int(sh * ratio)
            left = (sw - nw) // 2
            photo = photo.crop((left, 0, left + nw, sh))
        else:
            nh = int(sw / ratio)
            top = (sh - nh) // 2
            photo = photo.crop((0, top, sw, top + nh))
        photo = photo.resize((CONTENT, 140), Image.LANCZOS)
        self.sheet.paste(photo, (MARGIN, self.y))
        self.draw.rectangle(
            [MARGIN, self.y, SIZE - MARGIN, self.y + 140],
            outline=INK, width=1)
        self.y += 140 + 8
        self.draw.text(
            (MARGIN, self.y),
            "A blockade at sea: warships enforce the cordon as Iran vows "
            "resistance. (Illustration)",
            font=serif_italic(16), fill=GREY)
        self.y += 14

    def ticker(self):
        height = 36
        self.draw.rectangle(
            [MARGIN, self.y, SIZE - MARGIN, self.y + height], fill=DEEP_BLUE)
        tick = ("ZAPORIZHZHIA: 2 KILLED, 40 WOUNDED  ·  GAZA: HAMAS "
                "SECURITY CHIEF KILLED  ·  UAE BUS CRASH: 13 DEAD")
        tick_font = fit_font(
            self.draw, tick, "LiberationSans-Bold.ttf", 19, CONTENT - 16)
        self.centred(self.y + 8, tick, tick_font, WHITE)
        self.y += height + 6

    def one_story(self, x, top, width, item):
        yy = top
        self.draw.text((x, yy), item["kicker"], font=sans_bold(15), fill=CRIMSON)
        yy += 22
        head_font = serif_bold(25)
        for line in wrap_lines(self.draw, item["headline"], head_font, width):
            self.draw.text((x, yy), line, font=head_font, fill=INK)
            yy += 28
        yy += 2
        body_font = serif_plain(17)
        for line in wrap_lines(self.draw, item["body"], body_font, width):
            self.draw.text((x, yy), line, font=body_font, fill=INK)
            yy += 21
        return yy + 10

    def grid(self):
        gutter = 30
        col = (CONTENT - gutter) // 2
        left_x = MARGIN
        right_x = MARGIN + col + gutter
        top = self.y

        left_column = [
            {"kicker": "UKRAINE",
             "headline": "Russian strike kills 2 in Zaporizhzhia",
             "body": "An overnight attack hits an apartment block: two "
                     "dead and 40 wounded, including four children, the "
                     "regional governor says."},
            {"kicker": "GAZA",
             "headline": "Israel kills Hamas security chief",
             "body": "Airstrikes kill Naeem Abu Nahel, director of Hamas\u2019 "
                     "internal security, and six others, including two "
                     "police officers, medics say."},
            {"kicker": "KOREA",
             "headline": "Russian jets enter Seoul\u2019s air zone",
             "body": "Several Russian aircraft fly into South Korea\u2019s air "
                     "defence identification zone over waters between the "
                     "peninsula and Japan."},
        ]
        right_column = [
            {"kicker": "UNITED ARAB EMIRATES",
             "headline": "Bus crash kills 13 in Ras Al Khaimah",
             "body": "A bus carrying 41 people hits a broken-down truck on "
                     "Al Watan Road in the early hours; 14 more are "
                     "injured, police say."},
            {"kicker": "NATO",
             "headline": "Rutte vows space defence after reports",
             "body": "The alliance will defend against threats in space, "
                     "its chief says, after reports Russia is preparing to "
                     "launch a nuclear-armed satellite."},
            {"kicker": "BERLIN",
             "headline": "Germany first to tap Ukraine\u2019s Delta",
             "body": "Berlin signs a letter of intent for access to "
                     "Ukraine\u2019s Delta battlefield system, with a "
                     "preliminary deal on interceptor missiles too."},
        ]
        yy = top
        for item in left_column:
            yy = self.one_story(left_x, yy, col, item)
        left_end = yy
        yy = top
        for item in right_column:
            yy = self.one_story(right_x, yy, col, item)
        right_end = yy
        mid = MARGIN + col + gutter // 2
        self.draw.line(
            [(mid, top), (mid, max(left_end, right_end) - 12)],
            fill=INK, width=1)
        self.y = max(left_end, right_end) + 2

    def footer(self):
        self.hline(self.y, 1)
        self.y += 10
        also = ("ALSO:   Pentagon says Canada falls short as a defence "
                "partner  ·  Democrats probe White House role in Huang\u2019s "
                "Nvidia return  ·  Pope Francis\u2019 diary released")
        also_font = sans_bold(16)
        for line in wrap_lines(self.draw, also, also_font, CONTENT):
            self.centred(self.y, line, also_font)
            self.y += 22
        self.y += 2
        self.centred(
            self.y,
            "Every story above was reported on "
            "Tuesday 24 November 2026.",
            serif_italic(15), GREY)
        self.y += 16

    def save(self):
        assert self.y <= SIZE, f"page overflowed: cursor at {self.y}"
        self.sheet.save(OUT_PATH, format="PNG", optimize=True)
        size = os.path.getsize(OUT_PATH)
        print(f"wrote {OUT_PATH}: {SIZE}x{SIZE}, {size} bytes, "
              f"cursor ended at y={self.y}")
        if size >= MAX_BYTES:
            raise SystemExit(
                f"entry.png is {size} bytes, over the 1 MiB limit")


def main():
    page = Page()
    page.masthead()
    page.lead()
    page.hero()
    page.ticker()
    page.grid()
    page.footer()
    page.save()


if __name__ == "__main__":
    main()
