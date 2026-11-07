#!/usr/bin/env python3
"""Build the Samurai SDDM artwork and layout without starting an authentication session."""
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent

OMA_PATH = '''M1620 3370 c-401 -71 -758 -305 -989 -648 -62 -93 -156 -293 -186 -397 -109 -385 -74 -763 102 -1108 208 -408 579 -692 1030 -788 125 -27 357 -36 487 -20 131 17 293 61 406 111 134 59 160 68 236 80 93 15 111 9 119 -39 6 -38 7 -38 58 -45 69 -8 2231 -8 2375 1 l112 6 0 109 c0 102 2 112 26 144 44 57 86 77 154 72 86 -6 139 -44 365 -262 l197 -189 141 139 c390 383 846 837 1088 1085 l269 277 -529 533 c-290 294 -628 630 -750 748 l-221 213 -208 -199 c-228 -219 -278 -253 -365 -253 -58 0 -102 23 -141 74 -24 33 -26 42 -26 144 l0 109 -46 7 c-26 3 -597 6 -1269 6 l-1223 0 -6 -44 c-8 -53 -19 -57 -115 -45 -70 8 -101 19 -250 83 -248 107 -569 144 -841 96z m1451 -675 c107 -70 207 -264 261 -506 20 -89 23 -131 23 -294 0 -163 -3 -205 -23 -294 -46 -206 -121 -369 -212 -462 -124 -127 -221 -95 -267 86 -16 63 -18 126 -18 665 0 438 3 611 13 654 35 169 115 223 223 151z m2187 -355 c81 -50 102 -141 102 -445 0 -304 -21 -395 -102 -445 -81 -49 -185 -5 -334 144 -129 130 -159 186 -159 301 0 115 30 171 159 301 149 149 253 193 334 144z'''


def enso_path(cx, cy, radius, stroke_scale=1.0):
    steps = 400
    outer, inner = [], []
    for i in range(steps + 1):
        t = i / steps
        theta = 0.26 * math.pi + t * 1.86 * math.pi
        w = (4 + 22 * (math.sin(t * math.pi) ** 0.85)) * stroke_scale
        ro = radius + w / 2
        ri = radius - w / 2
        outer.append(f'{cx + ro * math.cos(theta):.2f},{cy + ro * math.sin(theta):.2f}')
        inner.append(f'{cx + ri * math.cos(theta):.2f},{cy + ri * math.sin(theta):.2f}')
    pts = outer + inner[::-1]
    return 'M ' + ' L '.join(pts) + ' Z'


def enso_omarchy_svg(cx, cy, enso_r, oma_w, enso_fill, oma_fill):
    s = oma_w / 800.0
    oma_h = 378.0 * s
    tx = cx - oma_w / 2.0
    ty = cy + oma_h / 2.0
    enso_d = enso_path(cx, cy, enso_r, stroke_scale=enso_r / 180.0)
    return (f'<path d="{enso_d}" fill="{enso_fill}"/>'
            f'<g transform="translate({tx:.2f},{ty:.2f}) scale({0.1 * s:.5f},{-0.1 * s:.5f})">'
            f'<path d="{OMA_PATH}" fill="{oma_fill}"/>'
            f'</g>')


def build(destination):
    destination.mkdir(parents=True, exist_ok=True)
    palette = tomllib.loads((ROOT/'colors.toml').read_text())
    source = Path('/usr/share/sddm/themes/omarchy')
    shutil.copy2(ROOT/'assets/login/Main.qml', destination/'Main.qml')
    for name in ('entry.png', 'entry-failed.png', 'bullet.png', 'lock.png', 'lock-failed.png'):
        shutil.copy2(source/name, destination/name)
        colour = palette['red'] if 'failed' in name else palette['foreground']
        if name == 'entry.png':
            colour = palette['line']
        subprocess.run(['magick', str(destination/name), '-channel', 'RGB',
                        '+level-colors', f'{colour},{colour}', str(destination/name)], check=True)

    logo_content = enso_omarchy_svg(300, 110, enso_r=78, oma_w=110,
                                   enso_fill=palette['line'], oma_fill=palette['foreground'])
    logo = (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220" '
            f'viewBox="0 0 600 220">'
            f'<g opacity="0.85">{logo_content}</g></svg>')
    (destination/'logo.svg').write_text(logo)
    subprocess.run(['rsvg-convert', str(destination/'logo.svg'), '-o', str(destination/'logo.png')], check=True)
    (destination/'theme.conf').write_text('[General]\n')
    (destination/'metadata.desktop').write_text(
        '[SddmGreeterTheme]\nName=Dark Knight Samurai\nDescription=Dark Knight Samurai login\n'
        'Type=sddm-theme\nVersion=1.0\nQtVersion=6\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 src/login.py <output-directory>')
    build(Path(sys.argv[1]))
