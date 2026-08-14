#!/usr/bin/env python3
"""Generate Matrix-style SVG section panels for the GitHub profile README."""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]

SECTIONS = {
    "about": "about",
    "stack": "stack",
    "projects": "projects",
    "stats": "stats",
    "about-this-page": "about this page",
}

CODE = "01 10 01 11 00 10 11 01 10 00 11 01 01 10 00 11"


def make_panel(label: str) -> str:
    text = escape(label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="44" viewBox="0 0 620 44" role="img" aria-label="{text}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#020b07"/>
      <stop offset="0.52" stop-color="#062116"/>
      <stop offset="1" stop-color="#020b07"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="2.2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="1" y="1" width="618" height="42" rx="5" fill="url(#bg)" stroke="#16a34a" stroke-opacity=".55"/>
  <path d="M12 33H608" stroke="#0f6b35" stroke-opacity=".55"/>
  <g fill="#39ff88" opacity=".16" font-family="monospace" font-size="9">
    <text x="13" y="14">{CODE}</text>
    <text x="13" y="26">{CODE}</text>
    <text x="332" y="39">{CODE}</text>
  </g>
  <text x="16" y="28" fill="#39ff88" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" filter="url(#glow)">&gt;_ {text}</text>
  <circle cx="599" cy="13" r="3" fill="#39ff88" filter="url(#glow)"/>
</svg>
'''


for filename, label in SECTIONS.items():
    (ROOT / f"matrix-{filename}.svg").write_text(make_panel(label), encoding="utf-8")
    print(f"wrote matrix-{filename}.svg")
