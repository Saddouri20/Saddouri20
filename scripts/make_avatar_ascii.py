#!/usr/bin/env python3
"""Convert a square GitHub avatar into a self-typing ASCII SVG portrait."""
from pathlib import Path
import io
import html
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageOps
from rembg import remove


RAMP = " .`:-=+*cs#%@"
COLS = 90
ROW_RATIO = 0.48
CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_H = 15
ROW_DELAY = 0.09
PAD = 14
FAMILY = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FG_LIGHT = "#6e7681"
FG_DARK = "#c9d1d9"


def remove_background(image: Image.Image) -> Image.Image:
    """Cut out the person and place them on white for a clean ASCII portrait."""
    source = io.BytesIO()
    image.save(source, format="PNG")
    cutout = remove(source.getvalue())
    foreground = Image.open(io.BytesIO(cutout)).convert("RGBA")
    white = Image.new("RGBA", foreground.size, (255, 255, 255, 255))
    white.alpha_composite(foreground)
    return white.convert("RGB")


def lines_from_image(path: Path) -> list[str]:
    image = remove_background(Image.open(path).convert("RGB"))
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.25)
    rows = max(1, int(COLS * (gray.height / gray.width) * ROW_RATIO))
    small = gray.resize((COLS, rows), Image.Resampling.LANCZOS)
    px = np.asarray(small, dtype=np.uint8)
    result = []
    for row in px:
        chars = []
        for value in row:
            level = min(len(RAMP) - 1, int((1 - value / 255.0) ** 1.15 * len(RAMP)))
            chars.append(RAMP[level])
        result.append("".join(chars).rstrip())
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return result or [""]


def build_svg(lines: list[str]) -> str:
    width = int(COLS * CHAR_W + PAD * 2)
    height = len(lines) * LINE_H + PAD * 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FAMILY}">',
        f'<style>.a{{fill:{FG_LIGHT}}}@media(prefers-color-scheme:dark){{.a{{fill:{FG_DARK}}}}}</style>',
    ]
    for index, line in enumerate(lines):
        y = PAD + index * LINE_H
        begin = f"{index * ROW_DELAY:.2f}s"
        end = f"{(index + 1) * ROW_DELAY:.2f}s"
        line_width = max(len(line), 1) * CHAR_W
        safe = html.escape(line)
        out.append(
            f'<clipPath id="c{index}"><rect x="{PAD}" y="{y}" height="{LINE_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{line_width:.1f}" begin="{begin}" '
            f'dur="{ROW_DELAY}s" fill="freeze"/></rect></clipPath>'
        )
        out.append(
            f'<g clip-path="url(#c{index})"><text xml:space="preserve" x="{PAD}" '
            f'y="{y + 11.2:.1f}" class="a" font-size="{FONT_SIZE}">{safe}</text></g>'
        )
        out.append(
            f'<rect y="{y + 1}" width="6" height="12" class="a" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + line_width:.1f}" '
            f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.8" begin="{begin}"/>'
            f'<set attributeName="opacity" to="0" begin="{end}"/></rect>'
        )
    out.append("</svg>")
    return "".join(out)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: make_avatar_ascii.py AVATAR.png ascii.svg")
    source, target = map(Path, sys.argv[1:])
    Path(target).write_text(build_svg(lines_from_image(source)), encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
