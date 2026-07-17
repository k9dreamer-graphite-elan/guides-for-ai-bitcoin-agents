"""Bitflow Earnings Card — render-only module.

Draws a **card model** (see card_model.build_card_model) into a PNG in the
Bitflow "share" style. The hero is NET PnL after gas (from the ledger); the
Bitflow Earnings/Fee-TVL figures are subordinate chips under a divider that
states they are NOT additive to net.

Usage as library:
    from card_model import build_card_model
    from render_card import render_card
    render_card(build_card_model(report), "out.png")
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Fonts — fall back through common Linux / macOS paths
# ---------------------------------------------------------------------------
_FONT_CANDIDATES_REG = [
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
_FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _find_font(candidates: list[str]) -> str:
    for p in candidates:
        if Path(p).exists():
            return p
    return candidates[-1]


FONT_REG = _find_font(_FONT_CANDIDATES_REG)
FONT_BOLD = _find_font(_FONT_CANDIDATES_BOLD)

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BG = "#090c0b"
GREEN = "#24f07a"
RED = "#f0555f"
SOFT_GREEN = "#88a18f"
MUTED = "#879188"
DIM = "#525b53"
WHITE = "#f2f5f0"
LABEL = "#c7d2c7"
CHIP_BG = "#17211a"
CHIP_DEAD_BG = "#0f1512"
AMBER = "#d9b45a"  # context-only / attribution signal
DIVIDER = "#1d2320"

W, H = 1200, 675

# Official wordmark rasterized from app.bitflow.finance
# /assets/brand/bitflow-logo-main-application-dark-mode.svg (cream on dark).
LOGO_PATH = Path(__file__).parent / "icons" / "bitflow-logo-dark.png"
LOGO_HEIGHT = 30


def _font(path: str, size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        # No candidate font on this host — degrade to Pillow's built-in font
        # instead of crashing the render.
        try:
            return ImageFont.load_default(size=size)
        except TypeError:  # Pillow < 10.1 has no sized default
            return ImageFont.load_default()


def _text_size(draw, text, fnt):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=fnt)
    return right - left, bottom - top


def _fit(draw, text, path, size, max_w):
    """Shrink font until `text` fits within max_w (min 14px)."""
    while size > 14:
        f = _font(path, size)
        w, _ = _text_size(draw, text, f)
        if w <= max_w:
            return f
        size -= 2
    return _font(path, 14)


def _paste_circle_icon(base, icon_path, xy, size):
    icon = Image.open(icon_path).convert("RGBA").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    icon.putalpha(mask)
    base.alpha_composite(icon, xy)


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
def render_card(model: dict, output_path, icon_x_path=None, icon_y_path=None) -> Path:
    """Render a card model to a PNG. Returns the output Path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGBA", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # --- Header ---
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        lw = round(logo.width * LOGO_HEIGHT / logo.height)
        img.alpha_composite(logo.resize((lw, LOGO_HEIGHT), Image.LANCZOS), (26, 28))
    else:
        draw.text((26, 28), "BITFLOW", font=_font(FONT_BOLD, 28), fill=WHITE)
    url = "APP.BITFLOW.FINANCE"
    uf = _font(FONT_REG, 18)
    uw, _ = _text_size(draw, url, uf)
    draw.text((W - 26 - uw, 32), url, font=uf, fill=MUTED)

    # --- Campaign id + pool label ---
    cid = model.get("campaign_id") or ""
    if cid:
        draw.text((26, 74), cid, font=_font(FONT_REG, 18), fill=MUTED)
    draw.text((26, 104), "HODLMM", font=_font(FONT_BOLD, 24), fill=LABEL)

    # --- Token icons + pair ---
    icon_size = 50
    have_icons = False
    if icon_x_path and Path(icon_x_path).exists():
        _paste_circle_icon(img, Path(icon_x_path), (26, 150), icon_size)
        have_icons = True
    if icon_y_path and Path(icon_y_path).exists():
        _paste_circle_icon(img, Path(icon_y_path), (60, 150), icon_size)
        have_icons = True
    pair = model.get("pair", {})
    pair_text = f"{pair.get('x_symbol', 'X')} / {pair.get('y_symbol', 'Y')}"
    px = 128 if have_icons else 26
    draw.text((px, 156), pair_text, font=_fit(draw, pair_text, FONT_BOLD, 40, 470 - (px - 26)), fill=WHITE)

    # --- Hero: NET PnL after gas (from the ledger) ---
    draw.text((26, 236), model.get("hero_label", "NET PnL · after gas").upper(),
              font=_font(FONT_BOLD, 22), fill=LABEL)
    hero = model.get("hero", {})
    hero_color = GREEN if hero.get("positive", True) else RED
    draw.text((24, 268), hero.get("text", "$0.00"),
              font=_fit(draw, hero.get("text", "$0.00"), FONT_BOLD, 104, 560), fill=hero_color)
    draw.text((28, 392), model.get("pct_line", ""), font=_font(FONT_BOLD, 30), fill=hero_color)

    # --- Core rows (right column) — all ledger-sourced ---
    rx, ry = 640, 232
    for label, value in model.get("rows", []):
        draw.text((rx, ry), label.upper(), font=_font(FONT_BOLD, 17), fill=MUTED)
        # baseline value may carry a native sub-line after "  ·  "
        if "  ·  " in value:
            main, sub = value.split("  ·  ", 1)
            draw.text((rx, ry + 24), main, font=_fit(draw, main, FONT_BOLD, 26, 534), fill=WHITE)
            draw.text((rx, ry + 58), sub, font=_fit(draw, sub, FONT_REG, 20, 534), fill=SOFT_GREEN)
            ry += 100
        else:
            draw.text((rx, ry + 24), value, font=_fit(draw, value, FONT_BOLD, 26, 534), fill=WHITE)
            ry += 78

    # --- Divider + non-additive caption ---
    draw.line((26, 500, W - 26, 500), fill=DIVIDER, width=2)
    draw.text((26, 512), model.get("context_divider", ""), font=_font(FONT_REG, 17), fill=MUTED)

    # --- Footer caveat (fee_confidence · period source) — right-aligned ---
    footer = model.get("footer", "")
    if footer:
        ff = _font(FONT_REG, 17)
        fw, _ = _text_size(draw, footer, ff)
        # Warning color only when the guardrail is actually engaged (low
        # confidence); a high-confidence caveat is informational, not a warning.
        low = str(model.get("fee_confidence") or "").strip().lower() == "low"
        draw.text((W - 26 - fw, 512), footer, font=ff, fill=AMBER if low else MUTED)

    # --- Subordinate chips ---
    x, y = 26, 566
    cf = _font(FONT_BOLD, 20)
    for chip in model.get("chips", []):
        text = chip.get("label", "")
        w, _ = _text_size(draw, text, cf)
        available = chip.get("available", True)
        if not available:
            bg, fg = CHIP_DEAD_BG, DIM
        elif chip.get("context_only"):
            bg, fg = CHIP_BG, AMBER
        else:
            bg, fg = CHIP_BG, SOFT_GREEN
        draw.rounded_rectangle((x, y, x + w + 30, y + 44), radius=22, fill=bg)
        draw.text((x + 15, y + 11), text, font=cf, fill=fg)
        x += w + 44

    img.save(output_path)
    return output_path


# ---------------------------------------------------------------------------
# CLI: render_card.py report.json out.png
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 render_card.py <report.json> <out.png>")
        sys.exit(1)
    from card_model import build_card_model

    report = json.loads(Path(sys.argv[1]).read_text())
    out = render_card(build_card_model(report), sys.argv[2])
    print(f"Saved: {out}")
