# -*- coding: utf-8 -*-
"""Generate the four IntelliJ IDEA .icls colour schemes.

Palettes and role assignment live in roles.py. This module renders them to XML,
enforces a WCAG readability floor, and writes PALETTE.md so the documentation
cannot drift from what actually ships.

Run:  python build_themes.py
"""
import os

import roles as R
from roles import (ATTRS, ATTR_MAP, CONTEXTUAL, DEFAULT_TARGET, FG_ENTRIES, FILES,
                   TARGETS, THEMES, PLAIN, BOLD, ITALIC, BOLD_ITALIC)

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
#  XML emission
# --------------------------------------------------------------------------
def hexv(c):
    return c.lstrip("#").lower()


def _rgb(h):
    h = hexv(h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lum(h):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(c1, c2):
    a, b = _lum(c1), _lum(c2)
    hi, lo = max(a, b), min(a, b)
    return round((hi + 0.05) / (lo + 0.05), 2)


def _hls_hex(h, l, s):
    import colorsys
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, round(r * 255))),
        max(0, min(255, round(g * 255))),
        max(0, min(255, round(b * 255))))


def adjust(fg, bg, target):
    """Nudge lightness only, preserving hue and saturation, until fg/bg meets target.

    The search direction moves *away* from the background rather than assuming a
    light or dark theme: some backgrounds here are mid-tone (gold, vermilion) and
    a luminance threshold misjudges them.
    """
    if not bg or contrast(fg, bg) >= target:
        return fg
    import colorsys
    r, g, b = _rgb(fg)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    brighter = _lum(fg) >= _lum(bg)
    lo, hi = (l, 1.0) if brighter else (0.0, l)
    for _ in range(48):
        mid = (lo + hi) / 2.0
        if contrast(_hls_hex(h, mid, s), bg) >= target:
            if brighter:
                hi = mid      # legible already -- creep back toward the original
            else:
                lo = mid
        else:
            if brighter:
                lo = mid
            else:
                hi = mid
    found = _hls_hex(h, hi if brighter else lo, s)
    if contrast(found, bg) < target:                # saturation blocked the target
        for cand in ("#ffffff", "#000000", _hls_hex(h, 1.0 if brighter else 0.0, s)):
            if contrast(cand, bg) >= target:
                return cand
    return found


def polish(theme):
    """Raise every foreground to its readability floor. Returns the nudges made."""
    rr = theme["roles"]
    cc = theme["colors"]
    bg = rr["text"]["bg"]
    changes = []

    def note(where, old, new, ref_bg, target):
        changes.append((where, old, new, contrast(old, ref_bg),
                        contrast(new, ref_bg), target))

    for name, r in rr.items():
        if not r["fg"] or name in CONTEXTUAL:
            continue
        target = TARGETS.get(name, DEFAULT_TARGET)
        ref = r["bg"] or bg
        new = adjust(r["fg"], ref, target)
        if new != r["fg"]:
            note(name, r["fg"], new, ref, target)
            r["fg"] = new

    # a foreground must clear the floor against *every* background it is drawn on,
    # so collect all of them per role and converge before recording a change
    ctx_bgs = {}
    for attr, fg_role, bg_role, _f, _e, _ef in ATTRS:
        if fg_role and bg_role and rr[fg_role]["fg"] and rr[bg_role]["bg"]:
            ctx_bgs.setdefault(fg_role, []).append((attr, rr[bg_role]["bg"]))
    for fg_role, pairs in ctx_bgs.items():
        target = TARGETS.get(fg_role, DEFAULT_TARGET)
        original = rr[fg_role]["fg"]
        cur = original
        for _ in range(4):
            for _attr, abg in pairs:
                cur = adjust(cur, abg, target)
            if all(contrast(cur, abg) >= target for _a, abg in pairs):
                break
        if cur != original:
            worst = min(pairs, key=lambda p: contrast(original, p[1]))
            note(f"{fg_role} (on {len(pairs)} bg)", original, cur, worst[1], target)
            rr[fg_role]["fg"] = cur

    for name, (src, target) in FG_ENTRIES.items():
        fg = cc.get(name)
        if not isinstance(fg, str):
            continue
        ref = bg if src == "editor" else cc.get(src)
        if not isinstance(ref, str):
            continue
        new = adjust(fg, ref, target)
        if new != fg:
            note(name, fg, new, ref, target)
            cc[name] = new
    return changes


def _value_block(indent, fg=None, bg=None, font=None, effect=None, eff_fg=None):
    out = [f"{indent}<value>"]
    if fg:
        out.append(f'{indent}  <option name="FOREGROUND" value="{hexv(fg)}"/>')
    if bg:
        out.append(f'{indent}  <option name="BACKGROUND" value="{hexv(bg)}"/>')
    if font:
        out.append(f'{indent}  <option name="FONT_TYPE" value="{font}"/>')
    if effect is not None:
        out.append(f'{indent}  <option name="EFFECT_TYPE" value="{effect}"/>')
        if eff_fg:
            out.append(f'{indent}  <option name="EFFECT_COLOR" value="{hexv(eff_fg)}"/>')
    out.append(f"{indent}</value>")
    return out


def attr_xml(name, fg, bg, font=PLAIN, effect=None, eff_fg=None, indent="    "):
    if not any((fg, bg, font, effect is not None)):
        return ""
    lines = [f'{indent}<option name="{name}">']
    lines += _value_block(indent + "  ", fg, bg, font, effect, eff_fg)
    lines.append(f"{indent}</option>")
    return "\n".join(lines)


def render(theme):
    rr, cc = theme["roles"], theme["colors"]
    head = (
        f'<scheme name="{theme["name"]}" version="142" '
        f'parent_scheme="{theme["parent"]}">\n'
        f"  <metaInfo>\n"
        f'    <property name="created">{theme["created"]}</property>\n'
        f'    <property name="ide">Idea</property>\n'
        f'    <property name="ideVersion">2025.2</property>\n'
        f'    <property name="modified">{theme["created"]}</property>\n'
        f'    <property name="originalScheme">{theme["name"]}</property>\n'
        f"  </metaInfo>"
    )
    colours = [f'    <option name="{n}" value="{hexv(v)}"/>' for n, v in cc.items()]

    txt = rr["text"]
    attrs = [attr_xml("TEXT", txt["fg"], txt["bg"])]
    attrs.append(attr_xml("DEFAULT_IDENTIFIER", txt["fg"], None))
    for name, role in ATTR_MAP:
        if name == "DEFAULT_IDENTIFIER":
            continue
        r = rr[role]
        attrs.append(attr_xml(name, r["fg"], r["bg"], r["font"],
                              r["effect"], r["eff_fg"] or r["fg"]))
    for name, fr, br, font, eff, efr in ATTRS:
        fg = rr[fr]["fg"] if fr else None
        bg = rr[br]["bg"] if br else None
        eff_fg = rr[efr]["fg"] if efr else None
        attrs.append(attr_xml(name, fg, bg, font, eff, eff_fg))
    attrs = [a for a in attrs if a]
    return (head + "\n  <colors>\n" + "\n".join(colours)
            + "\n  </colors>\n  <attributes>\n" + "\n".join(attrs)
            + "\n  </attributes>\n</scheme>\n")


# --------------------------------------------------------------------------
#  reporting / documentation
# --------------------------------------------------------------------------
ROLE_LABELS = [
    ("text", "默认文本"), ("keyword", "关键字"), ("soft_keyword", "软关键字"),
    ("string", "字符串"), ("escape", "转义/插值"), ("number", "数字"),
    ("constant", "常量"), ("comment", "行/块注释"), ("doc", "文档注释"),
    ("doc_tag", "文档标签"), ("doc_markup", "文档标记"),
    ("function", "函数/方法"), ("class_name", "类/接口/类型"),
    ("type_parameter", "类型参数"), ("annotation", "注解"),
    ("field", "字段"), ("static_field", "静态字段"), ("static_method", "静态方法"),
    ("local", "局部变量"), ("parameter", "参数"), ("reassigned", "重新赋值变量"),
    ("operator", "运算符/括号"), ("label", "标签"), ("predefined", "内建/预定义"),
    ("tag", "标签名/键"), ("attribute", "属性名"), ("attribute_value", "属性值"),
    ("invalid", "非法元素"), ("error", "错误"), ("warning", "警告"),
    ("weak_warning", "弱警告"), ("info", "信息"), ("todo", "TODO"),
    ("link", "超链接"), ("inlay", "内联提示"), ("hint_fg", "参数提示文字"),
    ("bookmark", "书签"), ("breakpoint_fg", "断点文字"),
]
BG_LABELS = [
    ("selection_bg", "选中背景"), ("brace_bg", "匹配括号背景"),
    ("brace_bad_bg", "不匹配括号背景"), ("search_bg", "搜索命中背景"),
    ("search_write_bg", "写的搜索命中背景"), ("caret_id_bg", "标识符高亮背景"),
    ("caret_write_bg", "写标识符高亮背景"), ("fold_bg", "折叠/注入片段背景"),
    ("exec_bg", "执行点背景"), ("hint_bg", "提示背景"),
    ("inlay_bg", "内联提示背景"), ("breakpoint_bg", "断点背景"),
]
FONT_LABEL = {0: "", 1: "**加粗**", 2: "*斜体*", 3: "***加粗斜体***"}


def dump_palette(path):
    out = ["# 最终色值", "",
           "本文件由 `build_themes.py` 自动导出，反映 4 个 `.icls` 中的实际取值"
           "（含可读性合规微调后的结果）。改色请改 `roles.py` 后重新运行生成器。", ""]
    for t in THEMES:
        rr, cc = t["roles"], t["colors"]
        bg = rr["text"]["bg"]
        out += [f"## {t['name']}", "",
                f"- 母方案（parent_scheme）：`{t['parent']}`",
                f"- 编辑器背景：`{bg}`", "",
                "### 代码角色", "",
                "| 角色 | 色值 | 对比度 | 样式 |", "|---|---|---|---|"]
        for key, label in ROLE_LABELS:
            r = rr[key]
            if not r["fg"]:
                continue
            cr = contrast(r["fg"], r["bg"] or bg)
            out.append(f"| {label} | `{r['fg']}` | {cr} | "
                       f"{FONT_LABEL.get(r['font'], '')} |")
        out += ["", "### 背景类角色", "", "| 角色 | 色值 |", "|---|---|"]
        for key, label in BG_LABELS:
            r = rr[key]
            if r["bg"]:
                out.append(f"| {label} | `{r['bg']}` |")
        out += ["", "<details><summary>编辑器 / 界面颜色项</summary>", "",
                "| 项 | 值 |", "|---|---|"]
        for n in sorted(cc):
            out.append(f"| `{n}` | `{cc[n]}` |")
        out += ["", "</details>", ""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))
    print("  wrote PALETTE.md")


def report(theme):
    """Audit every foreground against the surface it is actually drawn on."""
    rr = theme["roles"]
    bg = rr["text"]["bg"]
    # contextual roles sit on a colour-surface, not on the editor background
    ctx_bg = {}
    for _attr, fg_role, bg_role, _f, _e, _ef in ATTRS:
        if fg_role in CONTEXTUAL and bg_role:
            ctx_bg.setdefault(fg_role, rr[bg_role]["bg"])
    print(f"\n  {theme['name']}  (bg {bg})")
    worst = []
    for key, label in ROLE_LABELS:
        r = rr[key]
        if not r["fg"]:
            continue
        floor = TARGETS.get(key, DEFAULT_TARGET)
        surface = r["bg"] or ctx_bg.get(key) or bg
        cr = contrast(r["fg"], surface)
        flag = f"  <-- below floor {floor}" if cr < floor else ""
        if cr < floor:
            worst.append(key)
        print(f"    {key:14s} {r['fg']} on {surface}  {cr:5.2f}{flag}")
    return worst


def main():
    import xml.etree.ElementTree as ET
    for t in THEMES:
        changes = polish(t)
        print(f"\n{t['name']}: {len(changes)} colour(s) nudged for readability")
        for where, old, new, c_old, c_new, target in changes:
            print(f"    {where:26s} {old} -> {new}   {c_old:5.2f} -> {c_new:5.2f}"
                  f"  (floor {target})")
        xml = render(t)
        path = os.path.join(HERE, FILES[t["name"]])
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(xml)
        ET.fromstring(xml.encode("utf-8"))
        n_attr = xml.count("<option name=")
        print(f"  wrote {FILES[t['name']]:28s} {len(xml):7d} bytes  "
              f"{n_attr} options  XML OK")
    dump_palette(os.path.join(HERE, "PALETTE.md"))
    print("\ncontrast audit -- roles still under 4.5 (comments sit at 3.9 by design):")
    for t in THEMES:
        low = report(t)
        if low:
            print(f"    under 4.5: {low}")


if __name__ == "__main__":
    main()
