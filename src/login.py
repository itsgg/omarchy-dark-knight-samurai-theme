#!/usr/bin/env python3
"""Build the Samurai SDDM artwork and layout without starting an authentication session."""
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def samurai_kamon(cx, cy, radius, stroke, fill):
    parts = []
    r_outer = radius
    r_inner = radius - 6
    parts.append(f'<g stroke="{stroke}" fill="none" stroke-linecap="round" stroke-linejoin="round">')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" stroke-width="2.5"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" stroke-width="1.2" stroke-dasharray="5 3"/>')
    for angle in [-45, 45]:
        parts.append(f'<g transform="translate({cx},{cy}) rotate({angle})">')
        # Blade
        parts.append(f'<path d="M -3, -8 L -3, -60 Q -3, -68 0, -72 Q 3, -68 3, -60 L 3, -8 Z" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        parts.append(f'<line x1="0" y1="-10" x2="0" y2="-66" stroke="{stroke}" stroke-width="0.8"/>')
        # Tsuba
        parts.append(f'<ellipse cx="0" cy="-5" rx="10" ry="3.5" fill="{stroke}" stroke="{fill}" stroke-width="1"/>')
        # Tsuka
        parts.append(f'<rect x="-2.5" y="-1.5" width="5" height="38" rx="1.5" fill="{stroke}"/>')
        # Kashira
        parts.append(f'<ellipse cx="0" cy="38" rx="3.5" ry="2" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>')
        parts.append('</g>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="{stroke}" stroke="{fill}" stroke-width="1.5"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{fill}" stroke="none"/>')
    for deg in [0, 90, 180, 270]:
        parts.append(f'<g transform="translate({cx},{cy}) rotate({deg})">')
        parts.append(f'<polygon points="0,-72 3,-77 0,-82 -3,-77" fill="{fill}" stroke="none"/>')
        parts.append('</g>')
    parts.append('</g>')
    return ''.join(parts)


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

    kamon = samurai_kamon(300, 110, 80, palette["line"], palette["foreground"])
    logo = (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220" '
            f'viewBox="0 0 600 220">'
            f'<g opacity="0.75">{kamon}</g></svg>')
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
