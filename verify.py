# -*- coding: utf-8 -*-
"""Checks that the generated .icls files are structurally sane and complete.

Run after build_themes.py.  Exits non-zero if anything is wrong.
"""
import os
import sys
import xml.etree.ElementTree as ET

import roles as R
from roles import ATTRS, ATTR_MAP, FILES, THEMES

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED_ATTRS = ({n for n, _ in ATTR_MAP} | {a[0] for a in ATTRS}
                  | {"TEXT", "DEFAULT_IDENTIFIER"})

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


for theme in THEMES:
    path = os.path.join(HERE, FILES[theme["name"]])
    check(os.path.exists(path), f"{path} missing")
    if not os.path.exists(path):
        continue
    root = ET.parse(path).getroot()

    check(root.tag == "scheme", f"{path}: root is <{root.tag}>, expected <scheme>")
    check(root.get("name") == theme["name"],
          f"{path}: scheme name {root.get('name')!r} != {theme['name']!r}")
    check(root.get("parent_scheme") == theme["parent"],
          f"{path}: parent_scheme {root.get('parent_scheme')!r} != {theme['parent']!r}")
    check(root.get("version") == "142", f"{path}: version {root.get('version')!r}")

    colours = root.find("colors")
    attrs = root.find("attributes")
    check(colours is not None, f"{path}: no <colors>")
    check(attrs is not None, f"{path}: no <attributes>")

    # <colors> must hold only flat colour values, never nested <value> blocks
    seen = set()
    for opt in colours:
        name = opt.get("name")
        check(opt.get("value") is not None,
              f"{path}: colours/{name} has no value attribute")
        check(len(opt) == 0, f"{path}: colours/{name} unexpectedly nests <value>")
        check(name not in seen, f"{path}: duplicate colour option {name}")
        seen.add(name)
    for opt in attrs:
        name = opt.get("name")
        check(name not in seen, f"{path}: {name} appears in both <colors> and <attributes>")
        check(name not in {o.get("name") for o in attrs if o is not opt}
              or len([1 for o in attrs if o.get("name") == name]) == 1,
              f"{path}: duplicate attribute {name}")

    names = [o.get("name") for o in attrs]
    dupes = {n for n in names if names.count(n) > 1}
    check(not dupes, f"{path}: duplicate attributes {dupes}")

    got = set(names)
    missing = EXPECTED_ATTRS - got
    extra = got - EXPECTED_ATTRS
    check(not missing, f"{path}: missing attributes {sorted(missing)}")
    check(not extra, f"{path}: unexpected attributes {sorted(extra)}")

    for opt in attrs:
        if opt.get("name") != "TEXT":
            continue
        val = {o.get("name"): o.get("value") for o in opt.find("value")}
        check(val.get("BACKGROUND") == theme["roles"]["text"]["bg"].lstrip("#").lower(),
              f"{path}: TEXT/BACKGROUND {val.get('BACKGROUND')!r} != editor background")

    print(f"  {FILES[theme['name']]:28s} colours={len(seen):3d} "
          f"attributes={len(got):3d}")

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("   ", f)
    sys.exit(1)
print("all structural checks passed")
