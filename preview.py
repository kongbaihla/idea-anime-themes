# -*- coding: utf-8 -*-
"""Render a visual preview of the four schemes.

Produces preview.png (rasterised, so the result can actually be eyeballed) and
preview.html (interactive, openable in a browser).
"""
import os
import build_themes as bt
from roles import THEMES
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

FONT_DIR = "C:/Windows/Fonts"
FACES = {
    0: ("consola.ttf", "consolab.ttf"),
    1: ("consolab.ttf", "consolab.ttf"),
    2: ("consolai.ttf", "consolaz.ttf"),
    3: ("consolaz.ttf", "consolaz.ttf"),
}

# (text, role) -- role is a key in theme["roles"], or a pseudo role:
#   "sel" selection background, "search" search highlight, "err" error,
#   "warn" warning, "underline" debug underline
SAMPLE = [
    [("/**", "doc")],
    [(" * ", "doc"), ("Model of the ice queen.", "doc")],
    [(" * ", "doc"), ("@param", "doc_tag"), (" name the character name", "doc")],
    [(" */", "doc")],
    [("@Serializable", "annotation")],
    [("data class ", "keyword"), ("SnowMiku", "class_name"), ("(", "operator")],
    [("    val ", "keyword"), ("name", "local"), (": ", "operator"),
     ("String", "class_name"), (" = ", "operator"), ('"Hatsune Miku"', "string"), (",", "operator")],
    [("    val ", "keyword"), ("age", "local"), (": ", "operator"),
     ("Int", "class_name"), (" = ", "operator"), ("16", "number"), (",", "operator")],
    [("    private var ", "keyword"), ("frozen", "reassigned"), (": ", "operator"),
     ("Boolean", "class_name"), (" = ", "operator"), ("false", "keyword"), (",", "operator")],
    [(") {", "operator")],
    [("    // freeze the whole ocean", "comment")],
    [("    fun ", "keyword"), ("freeze", "function"), ("(", "operator"),
     ("level", "parameter"), (": ", "operator"), ("Int", "class_name"),
     (" = ", "operator"), ("3", "number"), (")", "operator"), (": ", "operator"),
     ("Result", "class_name"), ("<", "operator"), ("List", "class_name"),
     ("<", "operator"), ("Ice", "class_name"), (">>", "operator"), (" {", "operator")],
    [("        ", None), ("println", "function"), ("(", "operator"),
     ('"[debug] level=', "string"), ("$level", "escape"), ('"', "string"), (")", "operator")],
    [("        return ", "keyword"), ("world", "local"), (".", "operator"),
     ("apply", "function"), (" { ", "operator"), ("temperature", "field"),
     (" -= ", "operator"), ("40", "number"), (" }", "operator")],
    [("    }", "operator")],
    [("}", "operator")],
]
# pseudo-role overlay lines, appended so the diagnostics are visible
EXTRA = [
    [("    val ", "keyword"), ("temperture", "err"), (" = ", "operator"),
     ("world", "local"), (".", "operator"), ("temperature", "field"),
     ("   // typo -> error", "comment")],
    [("    val ", "keyword"), ("magic", "warn"), (" = ", "operator"),
     ("42", "number"), ("   // magic number -> warning", "comment")],
    [("    val ", "keyword"), ("search", "search"), (" = ", "operator"),
     ('"hit"', "string"), ("   // search match highlight", "comment")],
    [("    val ", "keyword"), ("picked", "sel"), (" = ", "operator"),
     ("1.5", "number"), ("   // selection", "comment")],
]

SWATCHES = ["keyword", "string", "number", "constant", "function", "class_name",
            "annotation", "local", "parameter", "comment", "doc", "error",
            "warning", "inlay", "todo", "link", "operator"]

FONT_SIZE = 17
LINE_H = 26
PAD = 18
GUTTER_W = 52


def hx(v):
    """PIL wants a leading '#'; the theme tables store bare hex."""
    if not v:
        return None
    return v if v.startswith("#") else "#" + v


def rgb(v):
    h = hx(v).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_font(font_type, size=FONT_SIZE, bold=False):
    key = 1 if bold else font_type
    reg, _bold = FACES.get(key, FACES[0])
    path = os.path.join(FONT_DIR, reg)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def resolve(theme, role):
    """Return (fg, bg, font_type, underline_colour_or_None)."""
    roles = theme["roles"]
    colors = theme["colors"]
    if role is None:
        return roles["text"]["fg"], None, 0, None
    if role == "sel":
        return None, roles["selection_bg"]["bg"], 0, None
    if role == "search":
        return roles["search_fg"]["fg"], roles["search_bg"]["bg"], 0, None
    if role == "err":
        r = roles["error"]
        return r["fg"], None, r["font"], r["eff_fg"] or r["fg"]
    if role == "warn":
        r = roles["warning"]
        return r["fg"], None, r["font"], r["eff_fg"] or r["fg"]
    r = roles.get(role)
    if not r:
        return roles["text"]["fg"], None, 0, None
    return r["fg"], r["bg"], r["font"], (r["eff_fg"] or r["fg"]) if r["effect"] is not None else None


def wavy(draw, x0, x1, y, colour, amp=2):
    step = 4
    pts = []
    up = True
    x = x0
    while x <= x1:
        pts.append((x, y - (amp if up else 0)))
        up = not up
        x += step
    if len(pts) > 1:
        draw.line(pts, fill=colour, width=1)


def render_panel(theme, lines, title, record=None, chrome=True):
    fonts = {(t, b): load_font(t, FONT_SIZE, b) for t in (0, 1, 2, 3) for b in (False, True)}
    body_font = fonts[(0, False)]
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    width = 0
    for toks in lines:
        w = sum(probe.textlength(t, font=fonts.get((resolve(theme, r)[2], False), body_font))
                for t, r in toks)
        width = max(width, w)

    sw_w = 0
    if chrome:
        for s in SWATCHES:
            sw_w += probe.textlength(s, font=body_font) + 14

    W = int(max(width, sw_w) + GUTTER_W + PAD * 2)
    if chrome:
        H = PAD * 2 + 34 + LINE_H * len(lines) + 16 + LINE_H + 24
    else:
        H = PAD * 2 + LINE_H * len(lines)
    img = Image.new("RGB", (W, H), hx(theme["roles"]["text"]["bg"]))
    d = ImageDraw.Draw(img)

    if chrome:
        d.text((PAD, PAD - 4), title, font=fonts[(0, True)],
               fill=hx(theme["roles"]["class_name"]["fg"]))
        y0 = PAD + 30
    else:
        y0 = PAD

    gn_font = fonts[(0, False)]
    for i, toks in enumerate(lines):
        y = y0 + i * LINE_H
        caret_row = (i == len(lines) - 4)
        if caret_row:
            d.rectangle([0, y, W, y + LINE_H], fill=hx(theme["colors"]["CARET_ROW_COLOR"]))
        # line number
        num = f"{i + 1:>3}"
        d.text((PAD, y + 4), num, font=gn_font,
               fill=hx(theme["colors"]["LINE_NUMBER_ON_CARET_ROW_COLOR"] if caret_row
                       else theme["colors"]["LINE_NUMBERS_COLOR"]))
        d.line([(PAD + GUTTER_W - 10, y0), (PAD + GUTTER_W - 10, y0 + LINE_H * len(lines))],
               fill=hx(theme["colors"]["INDENT_GUIDE"]), width=1)

        x = PAD + GUTTER_W
        for text, role in toks:
            fg, bg, ftype, ul = resolve(theme, role)
            font = fonts.get((ftype, False), body_font)
            w = probe.textlength(text, font=font)
            if bg:
                d.rectangle([x - 1, y + 2, x + w + 1, y + LINE_H - 2], fill=hx(bg))
            if fg:
                d.text((x, y + 4), text, font=font, fill=hx(fg))
            if ul and text.strip():
                wavy(d, x, x + w, y + LINE_H - 4, hx(ul))
            if record is not None and text.strip() and fg:
                record.append(dict(theme=title, text=text, role=role, fg=fg,
                                   x=x, y=y + 4, w=w, h=LINE_H))
            x += w

    if not chrome:
        return img

    # swatch strip
    sy = y0 + LINE_H * len(lines) + 14
    d.line([(0, sy - 8), (W, sy - 8)], fill=hx(theme["colors"]["INDENT_GUIDE"]), width=1)
    d.text((PAD, sy), "swatches:", font=fonts[(0, True)], fill=hx(theme["roles"]["text"]["fg"]))
    x = PAD + probe.textlength("swatches: ", font=fonts[(0, True)])
    for s in SWATCHES:
        fg, bg, ftype, _ = resolve(theme, s)
        font = fonts.get((ftype, False), body_font)
        w = probe.textlength(s, font=font)
        d.text((x, sy), s, font=font, fill=hx(fg) or hx(theme["roles"]["text"]["fg"]))
        x += w + 14
    return img


def render_html(themes, path):
    out = ["""<!doctype html><meta charset="utf-8">
<title>IDEA themes preview</title>
<style>
 body{margin:0;background:#202225;color:#ddd;
      font:14px/1.5 "Segoe UI",system-ui,sans-serif;padding:28px}
 h2{font-weight:600;margin:34px 0 10px;font-size:16px}
 .panel{border-radius:10px;overflow:hidden;border:1px solid #3a3d42}
 pre{margin:0;padding:16px 20px 16px 0;font:15px/1.65 Consolas,"Cascadia Mono",monospace;
     white-space:pre;overflow-x:auto}
 .ln{display:inline-block;width:48px;text-align:right;margin-right:18px;
     user-select:none;opacity:.75}
 .sw{display:flex;flex-wrap:wrap;gap:14px;padding:12px 20px;border-top:1px solid rgba(128,128,128,.25);
     font:13px Consolas,monospace}
 em{font-style:italic} b{font-weight:700}
 .wavy{text-decoration:underline wavy;text-underline-offset:3px}
</style>"""]
    for t in themes:
        roles, colors = t["roles"], t["colors"]
        bg = roles["text"]["bg"]

        def st(role, pseudo=None):
            if pseudo == "sel":
                return f'background:{hx(roles["selection_bg"]["bg"])}'
            if pseudo == "search":
                return (f'background:{hx(roles["search_bg"]["bg"])};'
                        f'color:{hx(roles["search_fg"]["fg"])}')
            if pseudo in ("err", "warn"):
                r = roles["error" if pseudo == "err" else "warning"]
                css = f'color:{hx(r["fg"])}'
                if r["font"] in (1, 3):
                    css += ";font-weight:700"
                return css
            r = roles.get(role) or roles["text"]
            css = f'color:{hx(r["fg"])}' if r["fg"] else ""
            if r["bg"]:
                css += f';background:{hx(r["bg"])}'
            if r["font"] in (2, 3):
                css += ";font-style:italic"
            if r["font"] in (1, 3):
                css += ";font-weight:700"
            return css

        out.append(f'<h2>{t["name"]} &nbsp;<code>bg {hx(bg)}</code> '
                   f'<span style="opacity:.6">parent {t["parent"]}</span></h2>')
        out.append(f'<div class="panel" style="background:{hx(bg)}"><pre>')
        all_lines = SAMPLE + EXTRA
        for i, toks in enumerate(all_lines):
            caret = (i == len(all_lines) - 4)
            row = f'background:{hx(colors["CARET_ROW_COLOR"])};' if caret else ""
            lncol = hx(colors["LINE_NUMBER_ON_CARET_ROW_COLOR"] if caret
                       else colors["LINE_NUMBERS_COLOR"])
            out.append(f'<div style="{row}margin:0 -20px 0 0">'
                       f'<span class="ln" style="color:{lncol}">{i + 1}</span>')
            for text, role in toks:
                esc = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
                pseudo = role if role in ("sel", "search", "err", "warn") else None
                css = st(None if pseudo else role, pseudo)
                cls = ""
                if pseudo in ("err", "warn") and text.strip():
                    cls = ' class="wavy"'
                out.append(f'<span style="{css}"{cls}>{esc}</span>')
            out.append("</div>")
        out.append("</pre>")
        out.append('<div class="sw">')
        for s in SWATCHES:
            out.append(f'<span style="{st(s)}">{s}</span>')
        out.append("</div></div>")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


def main():
    themes = THEMES
    for t in themes:
        bt.polish(t)

    all_lines = SAMPLE + EXTRA
    panels = [render_panel(t, all_lines, t["name"]) for t in themes]
    W = max(p.width for p in panels) + 40
    H = sum(p.height for p in panels) + 40 * (len(panels) + 1)
    canvas = Image.new("RGB", (W, H), "#202225")
    y = 40
    for p in panels:
        canvas.paste(p, (20, y))
        y += p.height + 40
    for t, p in zip(themes, panels):
        slug = t["name"].replace(" ", "")
        out = os.path.join(HERE, f"preview_{slug}.png")
        p.resize((p.width * 2, p.height * 2), Image.LANCZOS).save(out)
        print(f"wrote {os.path.basename(out)}  (2x)")
    png = os.path.join(HERE, "preview.png")
    canvas.save(png)
    print(f"wrote preview.png  {canvas.size[0]}x{canvas.size[1]}")
    render_html(themes, os.path.join(HERE, "preview.html"))
    print("wrote preview.html")


if __name__ == "__main__":
    main()
