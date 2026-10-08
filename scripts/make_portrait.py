#!/usr/bin/env python3
"""Turn a photo into ascii.svg — a self-typing, monochrome ASCII portrait.

This is the generator that produced the portrait at the top of the README.
Run it once; it is not on a schedule, unlike scripts/generate_stats.py.

    pip install pillow numpy opencv-python-headless rembg onnxruntime
    python3 scripts/make_portrait.py photo.png --crop 400,110,910,790
    python3 scripts/make_portrait.py photo.png ascii-dark.svg --dark \
        --crop 400,110,910,790
    python3 scripts/embed_portrait_font.py                  # light, see below
    python3 scripts/embed_portrait_font.py ascii-dark.svg   # and dark

The first run downloads a ~176 MB background-removal model, once.

Two things decide whether the output is any good, and neither is a parameter:

  * The photo. ASCII draws with shadow, not detail — about 13 brightness levels
    in total. You need side light (a window at ~45°, everything else off), a
    tight crop from chin to just above the hair, and real resolution. A 320px
    headshot fails: thin features like glasses frames are averaged away on
    downscale. Flat frontal light renders the face as a hole.
  * The darkening curve below. Without it the face comes out washed out and
    featureless — brows, glasses and lips all dissolve.

The grid bakes in an advance width of exactly 0.600 em (CHAR_W / FONT_SIZE), so
after generating, run scripts/embed_portrait_font.py to inline JetBrains Mono.
Otherwise a viewer whose default monospace is narrower — Consolas is ≈0.55 —
sees the portrait about 7% too narrow.

Dark mode needs its own file, not just a lighter ink. The ramp encodes shadow
as density, which only reads correctly when the ink is darker than the page;
recolour the same characters light-on-dark and the portrait turns into a
negative (bright hair, hollow eyes). --dark inverts the mapping instead: light
areas of the face get dense characters and the matte stays blank. It is one
continuous tone field: ink = matte coverage x tone, so the silhouette fades
into the page exactly as softly as the light one does, with no outline or halo,
and a mid-tone floor keeps dark hair from dissolving to dots. Each file bakes
its ink in with no media query, and the README picks one with <picture>, which
follows the GitHub theme rather than the OS.

Motion is SMIL, because GitHub strips <script> from READMEs: each row is
revealed by a clipPath wipe with a cursor block riding its edge, staggered top
to bottom, frozen at the end so it prints once and stops.
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

RAMP = " .`:-=+*cs#%@"     # bright/sparse -> dark/dense; leading space = blank
COLS = 90                  # below ~88 the face muddies; far above it dominates
CLAHE_CLIP = 3.0           # higher amplifies skin texture into noise
GAMMA = 1.0                # ramp mapping exponent
CURVE = 1.7                # the darkening curve — the difference-maker
DARK_FLOOR = 6             # --dark: lowest step inside the subject ("+")
DARK_GAMMA = 0.7           # --dark: lifts the face; ~74% of the light ink,
                           # which reads as equal weight light-on-dark
# ink coverage of each glyph (share of its cell), measured from rendered
# monospace glyphs; --dark matches density on this, not on ramp position
INK = {" ": 0.0, ".": 0.029, "`": 0.018, ":": 0.048, "-": 0.030, "=": 0.087,
       "+": 0.096, "*": 0.088, "c": 0.108, "s": 0.126, "#": 0.192, "%": 0.209,
       "@": 0.287}
CROP_BOTTOM = 0.0          # fraction to trim off the bottom (torso, chair)
ROW_RATIO = 0.48           # monospace cells are about twice as tall as wide

FG_LIGHT = "#6e7681"       # readable on GitHub light — the portrait's grey
FG_DARK = "#8b949e"        # muted on GitHub dark; brighter ink glares
CHAR_W = 7.74              # 0.600 em at FONT_SIZE — keep these in step
FONT_SIZE = 12.9
LINE_H = 15
ROW_DELAY = 0.09           # per-row stagger, seconds
FAMILY = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def prep(path, crop=None):
    """Cut out the background, even the local contrast, then darken."""
    src = Image.open(path).convert("RGBA")
    if crop:
        src = src.crop(crop)

    cut = remove(src)
    alpha = np.array(cut.split()[-1])

    # Composite onto white so everything outside the subject maps to the blank
    # end of the ramp. Skip this and the background fills with @ and %.
    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    gray = np.array(Image.alpha_composite(white, cut).convert("L"))

    gray = cv2.bilateralFilter(gray, 11, 50, 50)      # smooth skin, keep edges
    gray = cv2.createCLAHE(clipLimit=CLAHE_CLIP,
                           tileGridSize=(8, 8)).apply(gray)
    gray = (255.0 * (gray / 255.0) ** CURVE).astype("uint8")
    gray[alpha < 20] = 255                            # force the matte to white
    return Image.fromarray(gray), Image.fromarray(alpha)


def pick(cov, edge, r, c):
    """The glyph whose ink is nearest `cov`. At the edge a blank is allowed, and
    near-equal glyphs alternate by position so a fade never repeats one shape
    down a column — a stack of ":" or "`" reads as a drawn line."""
    pool = ([" "] if edge else []) + [ch for ch in RAMP if ch not in " `"]
    best = min(pool, key=lambda ch: abs(INK[ch] - cov))
    if not edge:
        return best
    near = [ch for ch in pool if abs(INK[ch] - INK[best]) <= 0.02]
    return near[(r * 7 + c * 3 + (r * c) % 5) % len(near)]


def dark_lines(px, subject, rows, cols):
    """Light-on-dark: one continuous tone field, density = coverage x tone.

    The light portrait's soft edge comes from the matte blending into the white
    page. Here the same blend fades into the dark page instead: each cell's ink
    is its matte coverage times the subject's own tone, so the silhouette
    softens exactly as much as in light mode and is never brighter than the
    figure beside it — no outline, no halo. The subject's tone is unblended from
    the white composite, and the floor holds dark hair at a visible mid-tone.
    """
    n = len(RAMP)
    target = [[0.0] * cols for _ in range(rows)]
    edge = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            a = subject[i] / 255.0
            if a < 0.08:
                continue
            v = min(1.0, max(0.0, (px[i] / 255.0 - (1 - a)) / a))   # unblend
            tone = INK[RAMP[round(DARK_FLOOR + v ** DARK_GAMMA * (n - 1 - DARK_FLOOR))]]
            target[r][c] = a * tone
            edge[r][c] = a < 0.98
    out = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            t = target[r][c]
            if t <= 0 and not edge[r][c]:
                line += " "
                continue
            ch = pick(t, edge[r][c], r, c)
            if edge[r][c]:          # diffuse the rounding error along the edge
                e = t - INK[ch]
                for dy, dx, w in ((0, 1, 7), (1, -1, 3), (1, 0, 5), (1, 1, 1)):
                    y, x = r + dy, c + dx
                    if 0 <= y < rows and 0 <= x < cols and edge[y][x]:
                        target[y][x] = max(0.0, target[y][x] + e * w / 16)
            line += ch
        out.append(line.rstrip())
    return out


def to_lines(img, matte, cols=COLS, gamma=GAMMA, dark=False):
    w, h = img.size
    if CROP_BOTTOM:
        box = (0, 0, w, int(h * (1 - CROP_BOTTOM)))
        img, matte = img.crop(box), matte.crop(box)
        w, h = img.size

    rows = int(cols * (h / w) * ROW_RATIO)
    px = list(img.resize((cols, rows), Image.LANCZOS).getdata())
    subject = list(matte.resize((cols, rows), Image.BOX).getdata())   # coverage
    n = len(RAMP)

    if not dark:
        out = ["".join(RAMP[min(n - 1, int((1 - px[r * cols + c] / 255.0) ** gamma
                                           * n))] for c in range(cols)).rstrip()
               for r in range(rows)]
    else:
        out = dark_lines(px, subject, rows, cols)

    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def build_svg(lines, cols=COLS, dark=False):
    pad = 14
    width = int(cols * CHAR_W + pad * 2)
    height = len(lines) * LINE_H + pad * 2

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
         f'height="{height}" viewBox="0 0 {width} {height}" '
         f'font-family="{FAMILY}">',
         f'<style>.a{{fill:{FG_DARK if dark else FG_LIGHT}}}</style>']

    for i, line in enumerate(lines):
        y = pad + i * LINE_H
        begin = f"{i * ROW_DELAY:.2f}s"
        end = f"{(i + 1) * ROW_DELAY:.2f}s"
        w = max(len(line), 1) * CHAR_W
        safe = (line.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))

        p.append(f'<clipPath id="c{i}"><rect x="{pad}" y="{y}" '
                 f'height="{LINE_H}" width="0">'
                 f'<animate attributeName="width" from="0" to="{w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'</rect></clipPath>')
        p.append(f'<g clip-path="url(#c{i})"><text xml:space="preserve" '
                 f'x="{pad}" y="{y + 11.2:.1f}" class="a" '
                 f'font-size="{FONT_SIZE}">{safe}</text></g>')
        # the cursor: a small block riding the wipe edge, gone once the row lands
        p.append(f'<rect y="{y + 1}" width="6" height="12" class="a" '
                 f'opacity="0">'
                 f'<animate attributeName="x" from="{pad}" to="{pad + w:.1f}" '
                 f'begin="{begin}" dur="{ROW_DELAY}s" fill="freeze"/>'
                 f'<set attributeName="opacity" to="0.8" begin="{begin}"/>'
                 f'<set attributeName="opacity" to="0" begin="{end}"/></rect>')

    p.append("</svg>")
    return "".join(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("photo")
    ap.add_argument("out", nargs="?", default="ascii.svg")
    ap.add_argument("--crop", help="left,top,right,bottom, applied first — crop "
                                   "tight to the head so the whole grid goes to "
                                   "the face")
    ap.add_argument("--cols", type=int, default=COLS)
    ap.add_argument("--dark", action="store_true",
                    help="inverted density for GitHub dark — write it to "
                         "ascii-dark.svg")
    ap.add_argument("--preview", action="store_true",
                    help="print the ASCII to the terminal as well")
    args = ap.parse_args()

    crop = None
    if args.crop:
        parts = [int(v) for v in args.crop.split(",")]
        if len(parts) != 4:
            sys.exit("--crop needs four numbers: left,top,right,bottom")
        crop = tuple(parts)

    gray, matte = prep(args.photo, crop)
    lines = to_lines(gray, matte, cols=args.cols, dark=args.dark)
    if args.preview:
        print("\n".join(lines))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(build_svg(lines, cols=args.cols, dark=args.dark))
    print(f"wrote {args.out} — {len(lines)} rows, {args.cols} columns")
    print(f"next: python3 scripts/embed_portrait_font.py {args.out}")


if __name__ == "__main__":
    main()
