# -*- coding: utf-8 -*-
"""Render a mockup of the whole IDE for each UI theme.

The .icls previews only show the editor. This draws the surrounding chrome --
toolbar, project tree, editor tabs, status bar, scrollbars, a popup -- so the
UI theme can be judged before installing anything.

Run:  python ui_preview.py     (writes ui_preview_<theme>.png)
"""
import os

from PIL import Image, ImageDraw

import themes as TH
from build_themes import polish
from preview import hx, load_font, render_panel
from roles import THEMES

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1180, 720
TOOLBAR_H = 42
STATUS_H = 30
SIDEBAR_W = 300
TAB_H = 34
FS = 15
FS_SM = 13

CODE = [
    [("public class ", "keyword"), ("Main", "class_name"), (" {", "operator")],
    [("    // freeze the whole ocean", "comment")],
    [("    public static void ", "keyword"), ("main", "function"),
     ("(", "operator"), ("String[] args", "parameter"), (") {", "operator")],
    [("        var ", "keyword"), ("name", "local"), (" = ", "operator"),
     ('"Hatsune Miku"', "string"), (";", "operator")],
    [("        ", None), ("IO", "class_name"), (".", "operator"),
     ("println", "function"), ("(", "operator"), ("name", "local"), (");", "operator")],
    [("        for ", "keyword"), ("(", "operator"), ("int ", "keyword"),
     ("i", "local"), (" = ", "operator"), ("1", "number"), ("; ", "operator"),
     ("i", "local"), (" <= ", "operator"), ("5", "number"), ("; ", "operator"),
     ("i", "reassigned"), ("++) {", "operator")],
    [("            ", None), ("IO", "class_name"), (".", "operator"),
     ("println", "function"), ('("i = "', "string"), (" + ", "operator"),
     ("i", "local"), (");", "operator")],
    [("        }", "operator")],
    [("    }", "operator")],
    [("}", "operator")],
]

TREE = [
    (0, "java  F:\\nothing\\javamiao~", "fg2", False),
    (1, ".idea", "fg2", False),
    (1, "out", "fg2", False),
    (1, "src", "fg2", False),
    (2, "Main.java", "sel", True),
    (2, ".gitignore", "fg", False),
    (2, "java.iml", "fg", False),
    (1, "External Libraries", "fg2", False),
    (1, "Scratches and Consoles", "fg2", False),
]

POPUP = ["Cut", "Copy", "Paste", "Find Usages", "Reformat Code"]


def put(d, xy, text, font, fill):
    if fill:
        d.text(xy, text, font=font, fill=hx(fill))


def render(name, p, scheme):
    win, panel, raised = hx(p["win"]), hx(p["panel"]), hx(p["raised"])
    hover, border = hx(p["hover"]), hx(p["border"])
    fg, fg2, fg3 = hx(p["fg"]), hx(p["fg2"]), hx(p["fg3"])
    sel, accent, gold = hx(p["sel"]), hx(p["accent"]), hx(p["gold"])
    on_accent, on_gold = hx(p["onAccent"]), hx(p["onGold"])
    bg_editor = hx(scheme["roles"]["text"]["bg"])

    f, fb, fi, fsm, fsmb = (load_font(0, FS), load_font(1, FS), load_font(2, FS),
                            load_font(0, FS_SM), load_font(1, FS_SM))

    img = Image.new("RGB", (W, H), win)
    d = ImageDraw.Draw(img)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    # ---- main toolbar ----------------------------------------------------
    d.rectangle([0, 0, W, TOOLBAR_H], fill=panel)
    d.line([(0, TOOLBAR_H - 1), (W, TOOLBAR_H - 1)], fill=border)
    d.ellipse([14, 13, 30, 29], outline=accent, width=2)
    put(d, (38, 12), "java", fb, fg)
    put(d, (82, 13), "Project", fsm, fg2)
    x = W - 268
    for i in range(7):
        if i == 1:
            # a "run" affordance in the accent colour
            d.polygon([(x, 13), (x, 29), (x + 13, 21)], fill=accent)
        else:
            d.rounded_rectangle([x, 14, x + 13, 28], radius=3, fill=fg3)
        x += 34
    put(d, (W - 44, 13), "...", fsm, fg3)

    # ---- left tool window ------------------------------------------------
    top = TOOLBAR_H
    bottom = H - STATUS_H
    d.rectangle([0, top, SIDEBAR_W, bottom], fill=panel)
    d.line([(SIDEBAR_W, top), (SIDEBAR_W, bottom)], fill=border)
    put(d, (14, top + 12), "项目", fb, fg)
    put(d, (66, top + 13), "▾", fsm, fg3)
    put(d, (SIDEBAR_W - 26, top + 13), "⋯", fsm, fg3)
    d.line([(0, top + 38), (SIDEBAR_W, top + 38)], fill=border)

    ty = top + 46
    for indent, label, role, selected in TREE:
        rh = 26
        if selected:
            d.rectangle([0, ty, SIDEBAR_W, ty + rh], fill=sel)
        colour = fg if role == "sel" else (fg2 if role == "fg2" else fg)
        marker = "▾ " if indent == 1 and role == "fg2" else (
            "  " if indent != 1 else "▸ ")
        put(d, (12 + indent * 16, ty + 5), marker + label, fsm, colour)
        ty += rh

    # ---- editor tabs -----------------------------------------------------
    ex = SIDEBAR_W
    d.rectangle([ex, top, W, top + TAB_H], fill=win)
    d.line([(ex, top + TAB_H - 1), (W, top + TAB_H - 1)], fill=border)
    tab = "  Main.java  "
    tw = probe.textlength(tab, font=fsm) + 14
    d.rectangle([ex + 12, top, ex + 12 + tw, top + TAB_H], fill=win)
    d.line([(ex + 12, top + TAB_H - 4), (ex + 12 + tw, top + TAB_H - 4)],
           fill=accent, width=3)
    put(d, (ex + 19, top + 9), tab, fsm, fg)
    put(d, (ex + 30 + tw, top + 9), "  Main  ", fsm, fg2)

    # ---- editor ----------------------------------------------------------
    ey = top + TAB_H
    d.rectangle([ex, ey, W, bottom], fill=bg_editor)
    polish(scheme)
    panel_img = render_panel(scheme, CODE, "", chrome=False)
    img.paste(panel_img, (ex + 8, ey + 10))
    for k in range(3):
        d.ellipse([W - 44, ey + 12 + k * 6, W - 40, ey + 16 + k * 6], fill=fg3)
    d.rectangle([W - 13, ey + 4, W - 7, ey + 150], fill=win)
    d.rectangle([W - 13, ey + 4, W - 7, ey + 74], fill=border)

    # ---- popup menu overlay ---------------------------------------------
    px, py, pw = ex + 150, ey + 90, 250
    ph = 22 + len(POPUP) * 28
    d.rectangle([px + 3, py + 3, px + pw + 3, py + ph + 3], fill=win)
    d.rectangle([px, py, px + pw, py + ph], fill=raised, outline=border)
    iy = py + 11
    for i, item in enumerate(POPUP):
        if i == 1:
            d.rectangle([px + 1, iy - 4, px + pw - 1, iy + 22], fill=sel)
            put(d, (px + 14, iy), item, fsm, fg)
            put(d, (px + pw - 70, iy), "Ctrl+C", fsm, fg3)
        else:
            put(d, (px + 14, iy), item, fsm, fg2)
        iy += 28

    # ---- status bar ------------------------------------------------------
    d.rectangle([0, H - STATUS_H, W, H], fill=panel)
    d.line([(0, H - STATUS_H), (W, H - STATUS_H)], fill=border)
    put(d, (14, H - STATUS_H + 8), "java  ▸  src  ▸  Main.java", fsm, fg2)
    put(d, (W - 250, H - STATUS_H + 8), "9:1   LF   UTF-8   4 spaces", fsm, fg2)

    # ---- legend ----------------------------------------------------------
    ly = H - STATUS_H + 8
    lx = px + pw + 30
    for label, colour, fg_colour in (("accent", accent, on_accent),
                                     ("gold", gold, on_gold),
                                     ("selection", sel, fg)):
        w = probe.textlength(label, font=fsm) + 14
        d.rounded_rectangle([lx, ly - 1, lx + w, ly + 20], radius=4, fill=colour)
        put(d, (lx + 7, ly + 2), label, fsm, fg_colour)
        lx += w + 10
    return img


def main():
    for name, p in TH.PALETTES.items():
        TH.fix_palette(name, p)
        scheme = next(t for t in THEMES if t["name"] == name)
        img = render(name, p, scheme)
        out = os.path.join(HERE, "ui_preview_" + name.replace(" ", "") + ".png")
        img.save(out)
        print(f"wrote {os.path.basename(out)}")
        # stack them for a single-glance view
    names = list(TH.PALETTES)
    imgs = [Image.open(os.path.join(HERE, "ui_preview_" + n.replace(" ", "") + ".png"))
            for n in names]
    Wc = max(i.width for i in imgs) + 40
    Hc = sum(i.height for i in imgs) + 40 * (len(imgs) + 1)
    canvas = Image.new("RGB", (Wc, Hc), "#202225")
    y = 40
    for i in imgs:
        canvas.paste(i, (20, y))
        y += i.height + 40
    canvas.save(os.path.join(HERE, "ui_preview.png"))
    print(f"wrote ui_preview.png  {canvas.size[0]}x{canvas.size[1]}")


if __name__ == "__main__":
    main()
