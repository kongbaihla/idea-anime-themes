# -*- coding: utf-8 -*-
"""Regression test: every token must land on the canvas in its declared colour.

Guards the drawing path against silently falling back to the default text
colour (a wrong role name, a missing palette entry, a font-type mix-up).

Run after build_themes.py.  Exits non-zero on any mismatch.
"""
import sys
from collections import Counter

import build_themes as bt
import preview as pv
from roles import THEMES

LINES = pv.SAMPLE + pv.EXTRA
failures = []

for t in THEMES:
    bt.polish(t)
    rec = []
    panel = pv.render_panel(t, LINES, t["name"], record=rec)
    ok = Counter()
    bad = Counter()
    for r in rec:
        want = pv.rgb(pv.hx(r["fg"]))
        hits = 0
        for y in range(r["y"], min(r["y"] + r["h"], panel.height)):
            for x in range(int(r["x"]), min(int(r["x"] + r["w"]), panel.width)):
                px = panel.getpixel((x, y))
                if sum((a - b) ** 2 for a, b in zip(px, want)) < 220:
                    hits += 1
        key = r["role"] if isinstance(r["role"], str) else "text"
        (ok if hits else bad)[key] += 1
    print(f"\n{t['name']}")
    for role, n in sorted(ok.items()):
        print(f"   ok   {role:12s} {n:4d} token(s) rendered in colour")
    for role, n in sorted(bad.items()):
        print(f"   FAIL {role:12s} {n:4d} token(s) with no pixel of the declared colour")
        failures.append(f"{t['name']}: {role}")

print()
if failures:
    print(f"FAILED: {failures}")
    sys.exit(1)
print("all tokens rendered in their declared colours")
