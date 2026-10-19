"""Draw the site icon and the social preview image (run once; outputs are committed).

Writes site/icon.png (512x512), site/favicon.ico, site/apple-touch-icon.png and site/og-image.png (1280x640,
also used as the GitHub social preview). Needs Pillow.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SITE = Path(__file__).resolve().parent.parent / "site"
BLUE, DARK, WHITE, YELLOW = (37, 99, 235), (30, 58, 138), (255, 255, 255), (250, 204, 21)


def icon(size=512, scale=4):
    """Rounded blue square with a white house; its windows are a 2x2 calculator keypad."""
    s = size * scale
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=s * 0.22, fill=BLUE)
    u = s / 100
    w = 6 * u  # line width
    d.line([(18 * u, 50 * u), (50 * u, 20 * u), (82 * u, 50 * u)], fill=WHITE, width=round(w), joint="curve")
    d.rounded_rectangle([27 * u, 46 * u, 73 * u, 81 * u], radius=3 * u, outline=WHITE, width=round(w))
    for x in (37, 52):
        for y in (54, 66):
            d.rounded_rectangle([x * u, y * u, (x + 11) * u, (y + 8) * u], radius=1.5 * u,
                                fill=YELLOW if (x, y) == (52, 66) else WHITE)
    return im.resize((size, size), Image.LANCZOS)


def font(size, bold=True):
    for name in (("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def og_image():
    im = Image.new("RGB", (1280, 640), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1280, 16], fill=BLUE)
    im.paste(ic := icon(220), (80, 110), ic)
    d.text((340, 120), "Home Renovation", font=font(76), fill=DARK)
    d.text((340, 205), "Free Tools & Calculators", font=font(76), fill=BLUE)
    d.text((80, 390), "170 free tools: paint, tile, flooring and concrete calculators,", font=font(36, False), fill=(51, 65, 85))
    d.text((80, 440), "room planners, contract templates, contractor directories", font=font(36, False), fill=(51, 65, 85))
    d.text((80, 540), "English + Polish  ·  user ratings  ·  MCP server & Claude skill", font=font(32), fill=BLUE)
    return im


def main():
    SITE.mkdir(exist_ok=True)
    big = icon(512)
    big.save(SITE / "icon.png", optimize=True)
    big.resize((180, 180), Image.LANCZOS).save(SITE / "apple-touch-icon.png", optimize=True)
    big.save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    og_image().save(SITE / "og-image.png", optimize=True)


if __name__ == "__main__":
    main()
