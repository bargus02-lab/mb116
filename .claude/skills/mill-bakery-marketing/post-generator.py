#!/usr/bin/env python3
"""
Mill Bakery — Instagram post generator.

Renders 1080x1350 Instagram-ready PNGs from a list of post definitions.
Reads brand assets from this repo. Uses system fonts (no font installation needed).

Usage:
    python3 post-generator.py week-1.json output/week-1/

Run from the skill directory:
    cd .claude/skills/mill-bakery-marketing
    python3 post-generator.py calendar/week-1.json output/week-1/

Or call from the repo root:
    python3 .claude/skills/mill-bakery-marketing/post-generator.py \
        .claude/skills/mill-bakery-marketing/calendar/week-1.json \
        .claude/skills/mill-bakery-marketing/output/week-1/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# -------- Brand tokens (mirror styles.css) --------
COLORS = {
    "cream":      (248, 242, 230),
    "cream_deep": (239, 227, 204),
    "red":        (182, 55, 46),
    "red_deep":   (141, 36, 31),
    "gold":       (228, 171, 36),
    "gold_soft":  (244, 211, 109),
    "text":       (67, 43, 32),
    "muted":      (116, 88, 76),
    "cream_off":  (255, 250, 243),
}

SIZE = (1080, 1350)  # IG 4:5 portrait

# -------- Font discovery (uses macOS system fonts) --------
def _first_existing(*paths: str) -> str | None:
    for p in paths:
        if Path(p).exists():
            return p
    return None

FONT_SERIF = _first_existing(
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/Library/Fonts/Georgia Bold.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/System/Library/Fonts/Times.ttc",
)
FONT_SANS = _first_existing(
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
)
FONT_MONO = _first_existing(
    "/System/Library/Fonts/Monaco.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
)

if not (FONT_SERIF and FONT_SANS and FONT_MONO):
    raise SystemExit("Could not find required system fonts. Install Georgia and Helvetica.")


def _font(family: str, size: int) -> ImageFont.FreeTypeFont:
    path = {"serif": FONT_SERIF, "sans": FONT_SANS, "mono": FONT_MONO}[family]
    return ImageFont.truetype(path, size)


# -------- Repo asset paths --------
REPO = Path(__file__).resolve().parents[3]  # .claude/skills/mill-bakery-marketing/post-generator.py → repo root
ASSETS = REPO / "assets"
GALLERY = ASSETS / "gallery"
MARK_PATH = ASSETS / "logo-windmill-mark-2026.png"


# -------- Drawing helpers --------
def draw_text_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    line_spacing: float = 1.05,
    align: str = "left",
    stroke_width: int = 0,
) -> int:
    """Draw text wrapped to box width. Returns the y position after the last line."""
    x0, y0, x1, _ = box
    max_width = x1 - x0
    words = text.split(" ")
    lines: list[str] = []
    current: list[str] = []
    for w in words:
        trial = " ".join(current + [w])
        if draw.textlength(trial, font=font) <= max_width or not current:
            current.append(w)
        else:
            lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))

    y = y0
    asc, desc = font.getmetrics()
    line_h = int((asc + desc) * line_spacing)
    for line in lines:
        if align == "center":
            w = draw.textlength(line, font=font)
            x = x0 + (max_width - w) / 2
        else:
            x = x0
        draw.text((x, y), line, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=fill)
        y += line_h
    return y


def paste_watermark(canvas: Image.Image, *, scale: float = 0.10, opacity: int = 60) -> None:
    """Paste the windmill mark as a low-opacity watermark in the bottom-left corner."""
    if not MARK_PATH.exists():
        return
    mark = Image.open(MARK_PATH).convert("RGBA")
    target_w = int(SIZE[0] * scale)
    ratio = target_w / mark.size[0]
    mark = mark.resize((target_w, int(mark.size[1] * ratio)), Image.LANCZOS)
    # Fade
    alpha = mark.split()[3]
    alpha = alpha.point(lambda a: int(a * (opacity / 255)))
    mark.putalpha(alpha)
    canvas.alpha_composite(mark, dest=(60, SIZE[1] - mark.size[1] - 60))


def paste_corner_mark(canvas: Image.Image, *, scale: float = 0.12) -> None:
    """Paste the windmill mark fully opaque in the top-right corner."""
    if not MARK_PATH.exists():
        return
    mark = Image.open(MARK_PATH).convert("RGBA")
    target_w = int(SIZE[0] * scale)
    ratio = target_w / mark.size[0]
    mark = mark.resize((target_w, int(mark.size[1] * ratio)), Image.LANCZOS)
    canvas.alpha_composite(mark, dest=(SIZE[0] - mark.size[0] - 60, 60))


def draw_eyebrow(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], color: tuple) -> None:
    """Draw a mono uppercase eyebrow with a leading rule."""
    font = _font("mono", 28)
    text = text.upper()
    x, y = xy
    # Rule
    draw.rectangle([(x, y + 14), (x + 32, y + 16)], fill=color)
    draw.text((x + 48, y), text, font=font, fill=color)


# -------- Template renderers --------
def render_menu_spotlight(post: dict, out: Path) -> None:
    """Big headline + description + price on cream."""
    canvas = Image.new("RGBA", SIZE, COLORS["cream"] + (255,))
    draw = ImageDraw.Draw(canvas)

    # Top eyebrow
    draw_eyebrow(draw, post.get("eyebrow", "Fresh today"), (90, 120), COLORS["red"])

    # Big headline (serif, heavy) — auto-fit so it doesn't overflow vertically
    headline = post["headline"].upper()
    max_text_width = 900  # box width (990 - 90)
    longest_word = max(headline.split(), key=len)
    size = 260
    while size > 80:
        h_font = _font("serif", size)
        if draw.textlength(longest_word, font=h_font) <= max_text_width:
            break
        size -= 12
    draw_text_wrapped(
        draw, headline, (90, 260, 990, 900),
        h_font, COLORS["red"], line_spacing=0.95, stroke_width=2,
    )

    # Description
    if post.get("description"):
        desc_font = _font("serif", 44)
        draw_text_wrapped(
            draw, post["description"], (90, 920, 990, 1100),
            desc_font, COLORS["text"], line_spacing=1.25,
        )

    # Price
    if post.get("price"):
        price_font = _font("mono", 64)
        draw.text((90, 1180), post["price"], font=price_font, fill=COLORS["red_deep"])

    # Hours footer
    footer_font = _font("mono", 22)
    draw.text((90, SIZE[1] - 80), "DAILY 5 AM – 1 PM  ·  116 W MACARTHUR  ·  @MILLBAKERY.OC",
              font=footer_font, fill=COLORS["muted"])

    paste_corner_mark(canvas)
    canvas.save(out, "PNG", optimize=True)


def render_hours_card(post: dict, out: Path) -> None:
    """Hours / location, big simple."""
    bg = COLORS.get(post.get("bg", "red"), COLORS["red"])
    fg = COLORS["cream_off"]
    canvas = Image.new("RGBA", SIZE, bg + (255,))
    draw = ImageDraw.Draw(canvas)

    # Big number / phrase — auto-fit to canvas width
    headline = post["headline"].upper()
    max_text_width = SIZE[0] - 160  # 80px margin each side
    size = 360
    while size > 80:
        h_font = _font("serif", size)
        bbox = draw.textbbox((0, 0), headline, font=h_font)
        if (bbox[2] - bbox[0]) <= max_text_width:
            break
        size -= 12
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (SIZE[0] - text_w) / 2
    y = (SIZE[1] - text_h) / 2 - 40
    draw.text((x, y), headline, font=h_font, fill=fg, stroke_width=3, stroke_fill=fg)

    # Subtitle
    if post.get("subtitle"):
        sub_font = _font("mono", 28)
        sub = post["subtitle"].upper()
        sub_w = draw.textlength(sub, font=sub_font)
        draw.text(((SIZE[0] - sub_w) / 2, y + text_h + 60), sub, font=sub_font, fill=fg)

    paste_watermark(canvas, opacity=80)
    canvas.save(out, "PNG", optimize=True)


def render_personality_quote(post: dict, out: Path) -> None:
    """Quote-style serif on cream with a gold rule."""
    canvas = Image.new("RGBA", SIZE, COLORS["cream"] + (255,))
    draw = ImageDraw.Draw(canvas)

    # Opening quote mark
    quote_font = _font("serif", 280)
    draw.text((90, 80), "“", font=quote_font, fill=COLORS["gold"])

    # The quote
    quote_text = post["headline"]
    q_font = _font("serif", 96)
    end_y = draw_text_wrapped(
        draw, quote_text, (90, 350, 990, 1100),
        q_font, COLORS["red"], line_spacing=1.1, stroke_width=1,
    )

    # Gold rule
    draw.rectangle([(90, end_y + 60), (250, end_y + 64)], fill=COLORS["gold"])

    # Attribution
    if post.get("attribution"):
        attr_font = _font("mono", 24)
        draw.text((90, end_y + 110), post["attribution"].upper(),
                  font=attr_font, fill=COLORS["muted"])

    paste_watermark(canvas)
    canvas.save(out, "PNG", optimize=True)


def render_photo_post(post: dict, out: Path) -> None:
    """Full-bleed photo with bottom gradient + caption."""
    canvas = Image.new("RGBA", SIZE, COLORS["text"] + (255,))
    photo_path = GALLERY / post["photo"]
    if not photo_path.exists():
        raise FileNotFoundError(f"Photo not found: {photo_path}")
    photo = Image.open(photo_path).convert("RGBA")
    # cover-fit to canvas
    pw, ph = photo.size
    scale = max(SIZE[0] / pw, SIZE[1] / ph)
    new_size = (int(pw * scale), int(ph * scale))
    photo = photo.resize(new_size, Image.LANCZOS)
    px = (SIZE[0] - new_size[0]) // 2
    py = (SIZE[1] - new_size[1]) // 2
    canvas.paste(photo, (px, py))

    # Warm overlay + bottom gradient
    overlay = Image.new("RGBA", SIZE, (35, 12, 4, 70))
    canvas.alpha_composite(overlay)
    gradient = Image.new("L", (1, SIZE[1]), 0)
    for i in range(SIZE[1]):
        # fully transparent at top, opaque dark at bottom
        gradient.putpixel((0, i), int(200 * max(0, (i - SIZE[1] * 0.4) / (SIZE[1] * 0.6))))
    gradient = gradient.resize(SIZE)
    grad_layer = Image.new("RGBA", SIZE, (15, 6, 2, 0))
    grad_layer.putalpha(gradient)
    canvas.alpha_composite(grad_layer)

    draw = ImageDraw.Draw(canvas)

    # Mono "01" / eyebrow
    eye = post.get("eyebrow", "From the case")
    draw_eyebrow(draw, eye, (90, 1050), COLORS["gold_soft"])

    # Big headline
    headline = post["headline"].upper() if post.get("uppercase", True) else post["headline"]
    h_font = _font("serif", 140 if len(headline) < 18 else 110)
    draw_text_wrapped(
        draw, headline, (90, 1090, 990, 1280),
        h_font, COLORS["cream_off"], line_spacing=1.0, stroke_width=2,
    )

    paste_corner_mark(canvas, scale=0.10)
    canvas.save(out, "PNG", optimize=True)


def render_process_typographic(post: dict, out: Path) -> None:
    """Typographic 'made this morning' style — cream bg with gold rule + serif headline."""
    canvas = Image.new("RGBA", SIZE, COLORS["cream"] + (255,))
    draw = ImageDraw.Draw(canvas)

    # Top rule
    draw.rectangle([(90, 130), (990, 132)], fill=COLORS["gold"])
    # Top eyebrow centered
    eye_font = _font("mono", 28)
    eye_text = (post.get("eyebrow", "Process") or "").upper()
    eye_w = draw.textlength(eye_text, font=eye_font)
    draw.text(((SIZE[0] - eye_w) / 2, 160), eye_text, font=eye_font, fill=COLORS["red_deep"])

    # Big stacked headline (one word per line) — auto-fit longest word to canvas
    words = post["headline"].split(" ")
    max_text_width = SIZE[0] - 200
    size = 260
    while size > 80:
        h_font = _font("serif", size)
        longest = max((draw.textlength(w.upper(), font=h_font) for w in words), default=0)
        if longest <= max_text_width:
            break
        size -= 12
    line_h = int((h_font.getmetrics()[0] + h_font.getmetrics()[1]) * 0.95)
    total_h = line_h * len(words)
    y0 = (SIZE[1] - total_h) / 2
    for i, word in enumerate(words):
        word_up = word.upper()
        w = draw.textlength(word_up, font=h_font)
        x = (SIZE[0] - w) / 2
        draw.text((x, y0 + i * line_h), word_up, font=h_font, fill=COLORS["red"],
                  stroke_width=2, stroke_fill=COLORS["red"])

    # Bottom rule
    draw.rectangle([(90, SIZE[1] - 132), (990, SIZE[1] - 130)], fill=COLORS["gold"])
    # Bottom footer
    foot_font = _font("mono", 24)
    foot = (post.get("footer") or "Mill Bakery · Santa Ana").upper()
    foot_w = draw.textlength(foot, font=foot_font)
    draw.text(((SIZE[0] - foot_w) / 2, SIZE[1] - 100), foot, font=foot_font, fill=COLORS["muted"])

    paste_watermark(canvas, scale=0.08, opacity=50)
    canvas.save(out, "PNG", optimize=True)


# -------- Dispatcher --------
TEMPLATES = {
    "menu":        render_menu_spotlight,
    "hours":       render_hours_card,
    "personality": render_personality_quote,
    "photo":       render_photo_post,
    "process":     render_process_typographic,
}


def render_one(post: dict, output_dir: Path, index: int) -> Path:
    template = post["template"]
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template: {template}. Choose: {sorted(TEMPLATES)}")
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = post.get("slug") or post["headline"].lower().replace(" ", "-")[:40]
    slug = "".join(c for c in slug if c.isalnum() or c in "-_")
    out_path = output_dir / f"post-{index:02d}-{template}-{slug}.png"
    TEMPLATES[template](post, out_path)
    return out_path


def write_captions(posts: list[dict], output_dir: Path) -> Path:
    """Write a captions.md alongside the PNGs."""
    lines = ["# Captions for posts in this folder\n"]
    for i, post in enumerate(posts, start=1):
        slug = post.get("slug") or post["headline"].lower().replace(" ", "-")[:40]
        slug = "".join(c for c in slug if c.isalnum() or c in "-_")
        lines.append(f"## post-{i:02d} — {post['headline']} ({post['template']})\n")
        if post.get("caption"):
            lines.append(post["caption"] + "\n")
        if post.get("hashtags"):
            lines.append(" ".join("#" + h.lstrip("#") for h in post["hashtags"]) + "\n")
        lines.append("")
    out = output_dir / "captions.md"
    out.write_text("\n".join(lines))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: post-generator.py <calendar.json> <output_dir>")
        return 1
    calendar_path = Path(argv[1])
    output_dir = Path(argv[2])
    posts = json.loads(calendar_path.read_text())
    for i, post in enumerate(posts, start=1):
        path = render_one(post, output_dir, i)
        print(f"wrote {path}")
    cap_path = write_captions(posts, output_dir)
    print(f"wrote {cap_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
