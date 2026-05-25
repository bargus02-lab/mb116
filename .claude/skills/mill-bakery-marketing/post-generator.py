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


def _recolor_mark(target_rgb: tuple[int, int, int]) -> Image.Image:
    """Return the windmill mark recolored to target_rgb (preserving alpha)."""
    mark = Image.open(MARK_PATH).convert("RGBA")
    alpha = mark.split()[3]
    color = Image.new("RGB", mark.size, target_rgb)
    return Image.merge("RGBA", (*color.split(), alpha))


def paste_brand_icon(
    canvas: Image.Image,
    *,
    position: str | tuple[int, int] = "top-right",
    mode: str = "on_light",
    scale: float = 0.11,
) -> None:
    """
    Paste just the windmill icon (no pill, no wordmark) in a corner.

    modes:
      - "on_light"  red+gold original windmill   (use on cream backgrounds)
      - "on_dark"   cream-recolored windmill     (use on photo / dark backgrounds)
      - "on_red"    gold-recolored windmill      (use on the red hours-card bg)
    """
    if not MARK_PATH.exists():
        return

    if mode == "on_dark":
        mark = _recolor_mark((248, 242, 230))  # cream
    elif mode == "on_red":
        mark = _recolor_mark((244, 211, 109))  # gold soft
    else:  # on_light
        mark = Image.open(MARK_PATH).convert("RGBA")  # original red + gold

    target_w = int(SIZE[0] * scale)
    ratio = target_w / mark.size[0]
    mark = mark.resize((target_w, int(mark.size[1] * ratio)), Image.LANCZOS)

    margin = 56
    if position == "top-right":
        dest = (SIZE[0] - mark.size[0] - margin, margin)
    elif position == "top-left":
        dest = (margin, margin)
    elif position == "bottom-right":
        dest = (SIZE[0] - mark.size[0] - margin, SIZE[1] - mark.size[1] - margin)
    elif position == "bottom-left":
        dest = (margin, SIZE[1] - mark.size[1] - margin)
    else:
        dest = position  # raw tuple

    canvas.alpha_composite(mark, dest=dest)


def paste_brand_stamp(
    canvas: Image.Image,
    *,
    position: str | tuple[int, int] = "top-right",
    variant: str = "pill",
) -> None:
    """
    Composite a Mill Bakery brand stamp onto the canvas.

    variants:
      - "pill"          cream rounded pill, windmill + red wordmark.
                        Use on photo backgrounds and cream backgrounds.
      - "outlined_pill" same as pill plus a gold border. Use on cream backgrounds
                        when the stamp needs more visual separation.
      - "icon_only"     just the windmill mark recolored cream/gold, no pill.
                        Use on red backgrounds.
    """
    if not MARK_PATH.exists():
        return

    margin = 50

    if variant == "icon_only":
        mark = _recolor_mark((244, 211, 109))  # gold soft
        target_w = 96
        ratio = target_w / mark.size[0]
        mark = mark.resize((target_w, int(mark.size[1] * ratio)), Image.LANCZOS)
        if position == "top-right":
            dest = (SIZE[0] - mark.size[0] - margin, margin)
        elif position == "top-left":
            dest = (margin, margin)
        elif position == "bottom-right":
            dest = (SIZE[0] - mark.size[0] - margin, SIZE[1] - mark.size[1] - margin)
        elif position == "bottom-left":
            dest = (margin, SIZE[1] - mark.size[1] - margin)
        else:
            dest = position  # tuple
        canvas.alpha_composite(mark, dest=dest)
        return

    # Pill variants
    mark = Image.open(MARK_PATH).convert("RGBA")
    mark_h = 56
    ratio = mark_h / mark.size[1]
    mark = mark.resize((max(1, int(mark.size[0] * ratio)), mark_h), Image.LANCZOS)

    text = "MILL BAKERY"
    text_font = _font("serif", 28)

    temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    text_w = int(temp_draw.textlength(text, font=text_font))

    pad_h = 22
    pad_v = 14
    gap = 12
    stamp_w = pad_h + mark.size[0] + gap + text_w + pad_h
    stamp_h = pad_v * 2 + max(mark.size[1], 32)

    stamp = Image.new("RGBA", (stamp_w, stamp_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    pill_bg = (255, 252, 245, 240)
    radius = stamp_h // 2
    if variant == "outlined_pill":
        sd.rounded_rectangle(
            [(0, 0), (stamp_w, stamp_h)],
            radius=radius,
            fill=pill_bg,
            outline=(228, 171, 36, 220),
            width=2,
        )
    else:
        sd.rounded_rectangle(
            [(0, 0), (stamp_w, stamp_h)],
            radius=radius,
            fill=pill_bg,
        )

    mark_y = (stamp_h - mark.size[1]) // 2
    stamp.paste(mark, (pad_h, mark_y), mark)

    # Wordmark — use Bree Serif at its natural weight (no stroke, no faux-bold)
    # so the stamp reads as a clean lockup, not a clunky shouty label
    text_color = (141, 36, 31)  # red deep
    ascent, descent = text_font.getmetrics()
    text_y = (stamp_h - (ascent + descent)) // 2 - 2
    sd.text(
        (pad_h + mark.size[0] + gap, text_y),
        text,
        font=text_font,
        fill=text_color,
    )

    if position == "top-right":
        dest = (SIZE[0] - stamp_w - margin, margin)
    elif position == "top-left":
        dest = (margin, margin)
    elif position == "bottom-right":
        dest = (SIZE[0] - stamp_w - margin, SIZE[1] - stamp_h - margin)
    elif position == "bottom-left":
        dest = (margin, SIZE[1] - stamp_h - margin)
    else:
        dest = position  # tuple

    canvas.alpha_composite(stamp, dest=dest)


def paste_corner_mark(canvas: Image.Image, *, scale: float = 0.12) -> None:
    """Legacy helper — now routes to the unified brand stamp."""
    paste_brand_stamp(canvas, position="top-right", variant="pill")


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

    paste_brand_icon(canvas, position="top-right", mode="on_light")
    canvas.save(out, "PNG", optimize=True)


def render_hours_card(post: dict, out: Path) -> None:
    """Hours / location, big simple."""
    bg = COLORS.get(post.get("bg", "red"), COLORS["red"])
    fg = COLORS["cream_off"]
    canvas = Image.new("RGBA", SIZE, bg + (255,))
    draw = ImageDraw.Draw(canvas)

    # Big number / phrase — auto-fit to canvas width.
    # Use textlength (advance width) so the autofit accounts for the rendered
    # stroke, not just the bare bbox.
    headline = post["headline"].upper()
    max_text_width = SIZE[0] - 160  # 80px margin each side
    size = 360
    while size > 70:
        h_font = _font("serif", size)
        if draw.textlength(headline, font=h_font) + 12 <= max_text_width:
            break
        size -= 12
    bbox = draw.textbbox((0, 0), headline, font=h_font, stroke_width=3)
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

    paste_brand_icon(canvas, position="top-right", mode="on_red")
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

    paste_brand_icon(canvas, position="bottom-right", mode="on_light")
    canvas.save(out, "PNG", optimize=True)


def _load_photo_covered(photo_filename: str) -> Image.Image:
    """Load a photo and scale to cover the canvas."""
    photo_path = GALLERY / photo_filename
    if not photo_path.exists():
        raise FileNotFoundError(f"Photo not found: {photo_path}")
    photo = Image.open(photo_path).convert("RGBA")
    pw, ph = photo.size
    scale = max(SIZE[0] / pw, SIZE[1] / ph)
    new_size = (int(pw * scale), int(ph * scale))
    photo = photo.resize(new_size, Image.LANCZOS)
    bg = Image.new("RGBA", SIZE, COLORS["text"] + (255,))
    px = (SIZE[0] - new_size[0]) // 2
    py = (SIZE[1] - new_size[1]) // 2
    bg.paste(photo, (px, py))
    return bg


def _photo_warmth_overlay(canvas: Image.Image, top_fade: float = 0.4) -> None:
    """Apply warm dim overlay + bottom gradient to a photo canvas."""
    overlay = Image.new("RGBA", SIZE, (35, 12, 4, 70))
    canvas.alpha_composite(overlay)
    gradient = Image.new("L", (1, SIZE[1]), 0)
    for i in range(SIZE[1]):
        gradient.putpixel((0, i), int(220 * max(0, (i - SIZE[1] * top_fade) / (SIZE[1] * (1 - top_fade)))))
    gradient = gradient.resize(SIZE)
    grad_layer = Image.new("RGBA", SIZE, (15, 6, 2, 0))
    grad_layer.putalpha(gradient)
    canvas.alpha_composite(grad_layer)


def _autofit_serif(draw: ImageDraw.ImageDraw, text: str, max_width: int,
                   start: int = 200, min_size: int = 60, step: int = 10) -> ImageFont.FreeTypeFont:
    """Pick the largest serif size where the longest word fits in max_width."""
    longest = max(text.upper().split(), key=len, default=text)
    size = start
    while size > min_size:
        font = _font("serif", size)
        if draw.textlength(longest, font=font) <= max_width:
            return font
        size -= step
    return _font("serif", min_size)


def _wrap_lines_count(draw: ImageDraw.ImageDraw, text: str,
                     font: ImageFont.FreeTypeFont, max_width: int) -> int:
    """Return the number of lines the text will wrap to at max_width."""
    words = text.split()
    if not words:
        return 0
    lines = 0
    current_w = draw.textlength(words[0], font=font)
    for w in words[1:]:
        trial = draw.textlength(" " + w, font=font)
        if current_w + trial <= max_width:
            current_w += trial
        else:
            lines += 1
            current_w = draw.textlength(w, font=font)
    lines += 1
    return lines


def _autofit_serif_to_box(draw: ImageDraw.ImageDraw, text: str,
                         box_width: int, box_height: int,
                         line_spacing: float = 1.0,
                         start: int = 160, min_size: int = 56, step: int = 6
                         ) -> ImageFont.FreeTypeFont:
    """Pick the largest serif size where the wrapped text fits in BOTH width and height."""
    text_upper = text.upper() if isinstance(text, str) else text
    size = start
    while size > min_size:
        font = _font("serif", size)
        # Check longest word fits horizontally
        longest = max(text_upper.split(), key=len, default=text_upper)
        if draw.textlength(longest, font=font) <= box_width:
            # Count lines + check vertical
            lines = _wrap_lines_count(draw, text_upper, font, box_width)
            asc, desc = font.getmetrics()
            total_h = int((asc + desc) * line_spacing) * lines
            if total_h <= box_height:
                return font
        size -= step
    return _font("serif", min_size)


def render_photo_post(post: dict, out: Path) -> None:
    """Full-bleed photo with bottom gradient + caption."""
    canvas = _load_photo_covered(post["photo"])
    _photo_warmth_overlay(canvas)

    draw = ImageDraw.Draw(canvas)

    # Mono "01" / eyebrow — sits 60px above headline box
    eye = post.get("eyebrow", "From the case")
    draw_eyebrow(draw, eye, (90, 1000), COLORS["gold_soft"])

    # Big headline — auto-fit so wrapped lines fit BOTH width and height
    headline = post["headline"].upper() if post.get("uppercase", True) else post["headline"]
    box_top, box_bottom = 1050, 1320
    h_font = _autofit_serif_to_box(
        draw, headline,
        box_width=900, box_height=box_bottom - box_top,
        line_spacing=0.98, start=130, min_size=58, step=6,
    )
    draw_text_wrapped(
        draw, headline, (90, box_top, 990, box_bottom),
        h_font, COLORS["cream_off"], line_spacing=0.98, stroke_width=2,
    )

    paste_brand_icon(canvas, position="top-right", mode="on_dark")
    canvas.save(out, "PNG", optimize=True)


def render_menu_photo(post: dict, out: Path) -> None:
    """Menu card layout (eyebrow + headline + description + price) over a darkened photo."""
    canvas = _load_photo_covered(post["photo"])
    # Slightly stronger warm overlay + gradient top-down + bottom-up
    canvas.alpha_composite(Image.new("RGBA", SIZE, (25, 10, 4, 130)))
    # Top gradient (darker at top for eyebrow)
    top_grad = Image.new("L", (1, SIZE[1]), 0)
    for i in range(SIZE[1]):
        top_grad.putpixel((0, i), int(140 * max(0, 1 - (i / (SIZE[1] * 0.35)))))
    top_grad = top_grad.resize(SIZE)
    top_layer = Image.new("RGBA", SIZE, (15, 6, 2, 0))
    top_layer.putalpha(top_grad)
    canvas.alpha_composite(top_layer)
    # Bottom gradient (darker at bottom for price footer)
    _photo_warmth_overlay(canvas, top_fade=0.55)

    draw = ImageDraw.Draw(canvas)

    # Top eyebrow — leave room above for the brand stamp
    draw_eyebrow(draw, post.get("eyebrow", "Fresh today"), (90, 240), COLORS["gold_soft"])

    # Big headline (auto-fit width + height so wrapped lines stay in their box)
    headline = post["headline"].upper()
    box_top, box_bottom = 320, 820
    h_font = _autofit_serif_to_box(
        draw, headline,
        box_width=900, box_height=box_bottom - box_top,
        line_spacing=0.95, start=200, min_size=100, step=8,
    )
    draw_text_wrapped(
        draw, headline, (90, box_top, 990, box_bottom),
        h_font, COLORS["cream_off"], line_spacing=0.95, stroke_width=2,
    )

    # Description — sits in the lower middle band, white-on-dark
    if post.get("description"):
        desc_font = _font("serif", 40)
        draw_text_wrapped(
            draw, post["description"], (90, 970, 990, 1150),
            desc_font, COLORS["cream_off"], line_spacing=1.25,
        )

    # Price + footer
    if post.get("price"):
        price_font = _font("mono", 64)
        draw.text((90, 1180), post["price"], font=price_font, fill=COLORS["gold_soft"])

    footer_font = _font("mono", 22)
    draw.text((90, SIZE[1] - 80), "DAILY 5 AM – 1 PM  ·  116 W MACARTHUR  ·  @MILLBAKERY.OC",
              font=footer_font, fill=(255, 247, 239, 180))

    paste_brand_icon(canvas, position="top-right", mode="on_dark")
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

    paste_brand_icon(canvas, position="top-right", mode="on_light")
    canvas.save(out, "PNG", optimize=True)


# -------- Dispatcher --------
TEMPLATES = {
    "menu":        render_menu_spotlight,
    "menu_photo":  render_menu_photo,
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


def _file_for(post: dict, index: int) -> str:
    slug = post.get("slug") or post["headline"].lower().replace(" ", "-")[:40]
    slug = "".join(c for c in slug if c.isalnum() or c in "-_")
    return f"post-{index:02d}-{post['template']}-{slug}.png"


def write_captions(posts: list[dict], output_dir: Path) -> Path:
    """Write a captions.md alongside the PNGs."""
    lines = ["# Captions for posts in this folder\n"]
    for i, post in enumerate(posts, start=1):
        lines.append(f"## post-{i:02d} — {post['headline']} ({post['template']})\n")
        if post.get("location"):
            lines.append(f"**Location tag:** {post['location']}")
        if post.get("tag_accounts"):
            lines.append(f"**Tag in post:** {', '.join(post['tag_accounts'])}")
        lines.append("")
        if post.get("caption"):
            lines.append("```")
            lines.append(post["caption"])
            if post.get("hashtags"):
                lines.append("")
                lines.append(" ".join("#" + h.lstrip("#") for h in post["hashtags"]))
            lines.append("```")
        lines.append("")
    out = output_dir / "captions.md"
    out.write_text("\n".join(lines))
    return out


PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mill Bakery — {week_label} Preview</title>
<style>
:root {{
  --cream:#f8f2e6; --cream-deep:#efe3cc; --red:#b6372e; --red-deep:#8d241f;
  --gold:#e4ab24; --text:#432b20; --muted:#74584c;
  --rule:rgba(228,171,36,.32); --shadow:0 12px 36px rgba(106,61,33,.16);
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif;
  background:
    radial-gradient(ellipse 60% 40% at 0 0,rgba(228,171,36,.18) 0,transparent 60%),
    radial-gradient(ellipse 50% 35% at 100% 0,rgba(182,55,46,.1) 0,transparent 55%),
    linear-gradient(170deg,#fffaf3 0,#f8f2e6 45%,#f2e5cf 100%);
  color:var(--text); min-height:100vh; padding:2rem 1rem 4rem;
}}
header {{ max-width:1280px; margin:0 auto 2.4rem; padding:0 1rem; }}
.crumb {{ font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; color:var(--muted); }}
h1 {{ font-family:Georgia,"Bree Serif",serif; font-weight:900;
  font-size:clamp(2rem,4.5vw,3rem); color:var(--red); margin:.4rem 0 .6rem; letter-spacing:-.01em; }}
.lede {{ max-width:60ch; margin:0; color:var(--muted); line-height:1.6; font-size:1rem; }}
.view-toggle {{
  max-width:1280px; margin:0 auto 1.2rem; padding:0 1rem;
  display:flex; align-items:center; gap:.5rem;
  font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; color:var(--muted);
}}
.view-toggle button {{
  appearance:none; background:rgba(255,251,244,.88); border:1px solid var(--rule);
  color:var(--text); padding:.55rem .9rem; border-radius:4px; cursor:pointer;
  font:inherit; letter-spacing:.18em; text-transform:uppercase;
}}
.view-toggle button.is-active {{ background:var(--red); color:#fff7ef; border-color:var(--red); }}
.grid {{
  max-width:1280px; margin:0 auto; display:grid; gap:1.4rem;
  grid-template-columns:repeat(3,1fr); padding:0 1rem;
}}
@media (max-width:900px) {{ .grid {{ grid-template-columns:repeat(2,1fr); gap:1rem; }} }}
@media (max-width:560px) {{ .grid {{ grid-template-columns:1fr; }} }}
.post {{
  background:rgba(255,251,244,.85); border:1px solid var(--rule);
  border-radius:16px; overflow:hidden; box-shadow:var(--shadow);
  transition:transform 200ms ease,box-shadow 200ms ease;
}}
.post:hover {{ transform:translateY(-3px); box-shadow:0 24px 56px rgba(106,61,33,.20); }}
.post-media {{ position:relative; background:var(--cream-deep); aspect-ratio:4/5; }}
.post-media img {{ width:100%; height:100%; display:block; object-fit:cover; }}
.post-num {{
  position:absolute; top:.8rem; left:.8rem;
  background:rgba(255,251,244,.94); color:var(--red-deep);
  font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.72rem; letter-spacing:.18em; padding:.35rem .7rem; border-radius:999px; z-index:2;
}}
.post-meta {{ padding:1rem 1.1rem 1.2rem; }}
.post-template {{
  font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.7rem; letter-spacing:.18em; text-transform:uppercase; color:var(--red); margin:0 0 .4rem;
}}
.post-title {{
  font-family:Georgia,"Bree Serif",serif; font-weight:700;
  font-size:1.05rem; color:var(--text); margin:0 0 .6rem; line-height:1.25;
}}
.post-caption {{
  margin:0 0 .7rem; font-size:.86rem; line-height:1.55; color:var(--text);
  white-space:pre-line;
}}
.post-hashtags {{ margin:0 0 .5rem; font-size:.78rem; color:var(--muted); line-height:1.5; }}
.post-tag-row {{
  margin:0 0 .35rem; font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.66rem; letter-spacing:.14em; text-transform:uppercase; color:var(--muted);
}}
.post-tag-row strong {{ color:var(--red); }}
.post-actions {{ margin-top:.7rem; display:flex; gap:.4rem; flex-wrap:wrap; }}
.post-actions a, .post-actions button {{
  font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.68rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--red); text-decoration:none; padding:.4rem .7rem;
  border:1px solid var(--rule); border-radius:4px; background:transparent; cursor:pointer;
}}
.post-actions a:hover, .post-actions button:hover {{ background:rgba(228,171,36,.08); }}
body.feed-view .grid {{ grid-template-columns:1fr; max-width:560px; }}
body.feed-view .post-media {{ aspect-ratio:4/5; }}
body.ig-grid-view .grid {{ grid-template-columns:repeat(3,1fr); gap:4px; max-width:720px; }}
body.ig-grid-view .post {{ border-radius:0; border:0; box-shadow:none; background:transparent; }}
body.ig-grid-view .post-media {{ aspect-ratio:1/1; }}
body.ig-grid-view .post-meta {{ display:none; }}
body.ig-grid-view .post-num {{ display:none; }}
body.ig-grid-view .post:hover {{ transform:none; box-shadow:none; }}
footer {{
  max-width:1280px; margin:3rem auto 0; padding:0 1rem; text-align:center;
  font-family:ui-monospace,"DM Mono",Menlo,monospace;
  font-size:.7rem; letter-spacing:.18em; text-transform:uppercase; color:var(--muted);
}}
</style>
</head>
<body>
<header>
  <p class="crumb">Mill Bakery · Marketing · {week_label}</p>
  <h1>{week_label} — {post_count} Posts</h1>
  <p class="lede">{lede}</p>
</header>
<div class="view-toggle">
  <span>View:</span>
  <button data-view="cards" class="is-active">Cards + Captions</button>
  <button data-view="feed">Feed (single column)</button>
  <button data-view="ig-grid">IG Profile Grid</button>
</div>
<main class="grid">
{cards}
</main>
<footer>© Mill Bakery · Santa Ana · @millbakery.oc</footer>
<script>
const buttons = document.querySelectorAll(".view-toggle button");
buttons.forEach((b) => {{
  b.addEventListener("click", () => {{
    buttons.forEach((x) => x.classList.remove("is-active"));
    b.classList.add("is-active");
    document.body.classList.remove("feed-view", "ig-grid-view");
    if (b.dataset.view === "feed") document.body.classList.add("feed-view");
    if (b.dataset.view === "ig-grid") document.body.classList.add("ig-grid-view");
  }});
}});
document.querySelectorAll("[data-copy]").forEach((btn) => {{
  btn.addEventListener("click", () => {{
    const text = btn.getAttribute("data-copy");
    navigator.clipboard.writeText(text).then(() => {{
      const original = btn.textContent;
      btn.textContent = "Copied!";
      setTimeout(() => {{ btn.textContent = original; }}, 1500);
    }});
  }});
}});
</script>
</body>
</html>
"""


def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def _build_card(post: dict, index: int) -> str:
    filename = _file_for(post, index)
    template_label = post["template"].replace("_", " · ").title()
    title = _html_escape(post.get("headline", ""))
    if post.get("price"):
        title += f" · {_html_escape(post['price'])}"

    caption = _html_escape(post.get("caption") or "")
    hashtags = " ".join("#" + h.lstrip("#") for h in (post.get("hashtags") or []))
    hashtags_html = _html_escape(hashtags)

    # For clipboard: caption + blank line + hashtags
    clipboard = (post.get("caption") or "").strip()
    if hashtags:
        clipboard = (clipboard + "\n\n" + hashtags).strip()

    tag_rows = []
    if post.get("location"):
        tag_rows.append(f'<p class="post-tag-row"><strong>Location:</strong> {_html_escape(post["location"])}</p>')
    if post.get("tag_accounts"):
        accts = ", ".join(post["tag_accounts"])
        tag_rows.append(f'<p class="post-tag-row"><strong>Tag accounts:</strong> {_html_escape(accts)}</p>')

    return f"""<article class="post">
  <div class="post-media">
    <span class="post-num">{index:02d}</span>
    <img src="{filename}" alt="{title}">
  </div>
  <div class="post-meta">
    <p class="post-template">{_html_escape(template_label)}</p>
    <h3 class="post-title">{title}</h3>
    {"".join(tag_rows)}
    <p class="post-caption">{caption}</p>
    <p class="post-hashtags">{hashtags_html}</p>
    <div class="post-actions">
      <a href="{filename}" target="_blank">Open PNG</a>
      <button type="button" data-copy="{_html_escape(clipboard)}">Copy Caption</button>
    </div>
  </div>
</article>"""


def write_preview(posts: list[dict], output_dir: Path, week_label: str = "Week 1") -> Path:
    """Write a preview.html that displays the posts in card / feed / IG-grid views."""
    cards = "\n".join(_build_card(p, i) for i, p in enumerate(posts, start=1))
    html = PREVIEW_TEMPLATE.format(
        week_label=week_label,
        post_count=len(posts),
        lede="Hover any tile for a lift. Click 'Open PNG' to view the upload-ready image. "
             "Click 'Copy Caption' to grab caption + hashtags as one block. "
             "Toggle the view above to see how these will look in feed or on your profile grid.",
        cards=cards,
    )
    out = output_dir / "preview.html"
    out.write_text(html)
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
    week_label = "Week " + (calendar_path.stem.replace("week-", "").strip() or "1")
    preview_path = write_preview(posts, output_dir, week_label.title())
    print(f"wrote {preview_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
