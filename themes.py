# -*- coding: utf-8 -*-
"""UI-theme half of the deliverable: four .theme.json files plus the plugin jar.

A .icls can only colour the editor. Panels, tool windows, tabs, toolbars, the
status bar, popups, scrollbars and icons come from a *UI theme*, which only a
plugin can provide. This module builds that plugin -- a jar with no code in it.

Layout follows the theme plugins already installed on this machine
(one-dark-theme 6.2.2, GitHub Theme 1.2.2), which IDEA accepts:
    META-INF/MANIFEST.MF          <- without this IDEA reports "not a valid plugin"
    META-INF/plugin.xml
    META-INF/pluginIcon.svg
    <Name>.theme.json             <- at the jar root, referenced as "/<Name>.theme.json"
    <Name>.xml                    <- the editor scheme, referenced by editorScheme

Key names come from the themes bundled with IntelliJ IDEA 2025.2
(lib/app-client.jar, themes/*.theme.json); see _ref/ui_keys.json for the
whitelist. IDEA ignores unknown keys silently, so a typo would otherwise just
look like "that part didn't change".

Run:  python themes.py      (writes the json files and dist/*.jar)
"""
import json
import os
import xml.etree.ElementTree as ET
import zipfile

from build_themes import adjust, contrast
from roles import FILES, THEMES

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
WHITELIST = os.path.join(HERE, "_ref", "ui_keys.json")

PLUGIN_ID = "com.kb.anime.idea.themes"
JAR_NAME = "AnimeIDEAThemes.jar"

# parentTheme values that exist in the 2025.2 bundle, with their dark flag.
# Mismatching `dark` against the parent makes IDEA pick the wrong icon set.
VALID_PARENTS = {"Darcula": True, "HighContrast": True, "ExperimentalDark": True,
                 "IntelliJ": False, "ExperimentalLight": False,
                 "ExperimentalLightWithLightHeader": False}

# ---------------------------------------------------------------- palettes --
PALETTES = {
    "Kurumi Tokisaki Dark": dict(
        dark=True, parent="Darcula",
        win="#1E1C22", panel="#26232E", raised="#2E2B36", hover="#3A3644",
        border="#43404E", fg="#D8D4DE", fg2="#B8B4C2", fg3="#8E8A98",
        sel="#4A2430", accent="#E8604F", gold="#E0A838", info="#7AB8E8",
        err="#FF4D4D", warn="#D8A03C",
        errBg="#5E2A36", warnBg="#4A3A1E", infoBg="#14293C",
        overlay="#FFFFFF1A", onAccent="#1E1C22", onGold="#1E1C22",
    ),
    "Kurumi Tokisaki Light": dict(
        dark=False, parent="IntelliJ",
        win="#FBF9F7", panel="#F4F0ED", raised="#FFFFFF", hover="#EDE7E3",
        border="#DED7D3", fg="#2B2933", fg2="#4A4650", fg3="#8A858F",
        sel="#F6D9D4", accent="#B03A22", gold="#8C6414", info="#2E6E9E",
        err="#D6192F", warn="#A96200",
        errBg="#F8DCD8", warnBg="#F3E7D4", infoBg="#E4F0F8",
        overlay="#00000012", onAccent="#FFFFFF", onGold="#FFFFFF",
    ),
    "Hatsune Miku Dark": dict(
        dark=True, parent="Darcula",
        win="#0B1A2A", panel="#102436", raised="#16304A", hover="#1D3D5C",
        border="#22496E", fg="#C0D6E4", fg2="#9EBDD0", fg3="#5A7B95",
        sel="#1B4A6E", accent="#48C0F8", gold="#F0B8CC", info="#48C0F8",
        err="#FF5F56", warn="#E8B84A",
        errBg="#5E2A36", warnBg="#3E3418", infoBg="#14293C",
        overlay="#FFFFFF1A", onAccent="#0B1A2A", onGold="#0B1A2A",
    ),
    "Hatsune Miku Light": dict(
        dark=False, parent="IntelliJ",
        win="#FBF7FA", panel="#F4EFF5", raised="#FFFFFF", hover="#EAE3EF",
        border="#DBD2E0", fg="#2A3B45", fg2="#3D5A6B", fg3="#8299A9",
        sel="#D6EBFA", accent="#0777BF", gold="#B05C7A", info="#005EA8",
        err="#D32F2F", warn="#A76200",
        errBg="#F8E0E6", warnBg="#F3E7D4", infoBg="#E4F0F8",
        overlay="#00000012", onAccent="#FFFFFF", onGold="#FFFFFF",
    ),
}

THEME_FILES = {
    "Kurumi Tokisaki Dark": "KurumiTokisaki_Dark.theme.json",
    "Kurumi Tokisaki Light": "KurumiTokisaki_Light.theme.json",
    "Hatsune Miku Dark": "HatsuneMiku_Dark.theme.json",
    "Hatsune Miku Light": "HatsuneMiku_Light.theme.json",
}
SCHEME_FILES = {
    "Kurumi Tokisaki Dark": "KurumiTokisaki_Dark.xml",
    "Kurumi Tokisaki Light": "KurumiTokisaki_Light.xml",
    "Hatsune Miku Dark": "HatsuneMiku_Dark.xml",
    "Hatsune Miku Light": "HatsuneMiku_Light.xml",
}

# Manifest lines are CRLF-terminated and wrap at 72 bytes. Built with chr() so
# no shell/JSON escape layer can mangle the line endings.
_CRLF = chr(13) + chr(10)
MANIFEST = _CRLF.join([
    "Manifest-Version: 1.0",
    "Created-By: kb theme generator (python zipfile)",
    "Version: 1.0.0",
    "Platform-Build: 252.28539.97",
    "", "",
])

PLUGIN_ICON = (
    '<svg width="40" height="40" viewBox="0 0 40 40" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<rect width="40" height="40" rx="8" fill="#1E1C22"/>'
    '<circle cx="15" cy="20" r="6" fill="#E8604F"/>'
    '<circle cx="25" cy="20" r="6" fill="#48C0F8"/></svg>')


def ui(p):
    """The UI override set. Colours only -- no UI class names or metrics, which
    are inherited from the parent theme and are version-sensitive."""
    return {
        # the catch-all carries most of the identity
        "*": {
            "foreground": p["fg"], "background": p["panel"], "borderColor": p["win"],
            "disabledText": p["fg3"], "disabledForeground": p["fg3"],
            "inactiveForeground": p["fg3"], "disabledBorderColor": p["border"],
            "selectionBackground": p["sel"], "lightSelectionBackground": p["sel"],
            "hoverBackground": p["hover"], "selectionForeground": p["fg"],
            "selectionInactiveForeground": p["fg2"],
            "selectionInactiveBackground": p["raised"],
            "infoForeground": p["fg3"], "acceleratorForeground": p["fg3"],
            "shortcutForeground": p["fg3"], "underlineColor": p["accent"],
            "inactiveUnderlineColor": p["fg3"], "focusColor": p["accent"],
            "separatorColor": p["border"], "separatorForeground": p["fg3"],
            "modifiedItemForeground": p["gold"],
        },
        "MainWindow.background": p["win"],
        "MainWindow.Tab": {
            "selectedForeground": p["fg"], "selectedBackground": p["win"],
            "selectedInactiveBackground": p["panel"], "foreground": p["fg2"],
            "background": p["win"], "hoverForeground": p["fg"],
            "hoverBackground": p["panel"], "separatorColor": p["win"],
            "borderColor": p["win"],
        },
        "EditorTabs": {
            "background": p["win"], "underlinedTabBackground": p["win"],
            "hoverBackground": p["win"] + "00", "hoverInactiveBackground": p["win"] + "00",
            "inactiveColoredFileBackground": p["win"] + "80",
            "underTabsBorderColor": p["border"], "underlineHeight": 4, "underlineArc": 4,
        },
        "TabbedPane": {"hoverColor": p["hover"], "contentAreaColor": p["win"],
                       "focusColor": p["sel"]},
        "ToolWindow": {
            "Header": {"inactiveBackground": p["panel"]},
            "HeaderTab": {"hoverInactiveBackground": p["hover"]},
            "Button": {"foreground": p["fg3"], "selectedForeground": p["fg"],
                       "selectedBackground": p["sel"]},
            "Stripe": {"separatorColor": p["border"]},
            "DragAndDrop": {"areaBackground": p["accent"] + "4D"},
        },
        "MainToolbar": {
            "background": p["panel"], "separatorColor": p["border"],
            "Icon": {"background": p["panel"], "pressedBackground": p["hover"]},
            "Dropdown": {"pressedBackground": p["hover"], "maxWidth": 350,
                         "transparentHoverBackground": p["overlay"]},
        },
        "StatusBar": {
            "background": p["panel"], "borderColor": p["border"],
            "Widget": {"foreground": p["fg2"], "hoverForeground": p["fg"],
                       "pressedBackground": p["hover"]},
            "Breadcrumbs": {"foreground": p["fg2"], "hoverForeground": p["fg"],
                            "chevronInset": 0},
        },
        "List": {
            "rowHeight": 24, "border": "4,0,4,0",
            "Button": {"separatorColor": p["overlay"], "separatorInset": 4,
                       "hoverBackground": p["sel"], "leftRightInset": 8},
            "Tag": {"background": p["hover"], "foreground": p["fg2"]},
        },
        "Tree": {"rowHeight": 24, "hash": p["border"], "border": "4,12,4,12",
                 "modifiedItemForeground": p["gold"]},
        "Table": {"gridColor": p["win"], "stripeColor": p["panel"]},
        "TableHeader": {"bottomSeparatorColor": p["win"], "separatorColor": p["win"],
                        "background": p["panel"]},
        "Button": {
            "arc": 8, "startBackground": p["raised"], "endBackground": p["raised"],
            "startBorderColor": p["border"], "endBorderColor": p["border"],
            "focusedBorderColor": p["raised"], "shadowColor": "#00000000",
            "default": {"foreground": p["onAccent"],
                        "startBackground": p["accent"], "endBackground": p["accent"],
                        "startBorderColor": p["accent"], "endBorderColor": p["accent"],
                        "focusedBorderColor": p["win"], "shadowColor": "#00000000"},
        },
        "Component": {"borderColor": p["border"], "focusedBorderColor": p["accent"],
                      "arc": 8},
        "TextField": {"background": p["raised"]},
        "ComboBox": {"ArrowButton": {"background": p["raised"],
                                     "nonEditableBackground": p["hover"]},
                     "nonEditableBackground": p["hover"], "padding": "1,9,1,6"},
        "Popup": {"paintBorder": True, "borderColor": p["border"],
                  "inactiveBorderColor": p["panel"]},
        "Menu": {"separatorColor": p["border"], "borderColor": p["border"]},
        "MainMenu": {"selectionForeground": p["fg"], "selectionBackground": p["hover"],
                     "transparentSelectionBackground": p["overlay"]},
        "Notification": {
            "background": p["raised"], "borderColor": p["border"],
            "foreground": p["fg"], "linkForeground": p["accent"],
            "iconHoverBackground": p["overlay"],
            "MoreButton": {"background": p["panel"], "innerBorderColor": p["border"],
                           "foreground": p["fg2"]},
            "ToolWindow": {"errorForeground": p["fg"], "warningForeground": p["fg"],
                           "informativeForeground": p["fg"],
                           "errorBackground": p["errBg"], "errorBorderColor": p["err"],
                           "warningBackground": p["warnBg"],
                           "warningBorderColor": p["warn"],
                           "informativeBackground": p["infoBg"],
                           "informativeBorderColor": p["info"]},
        },
        "Link": {"activeForeground": p["accent"], "hoverForeground": p["accent"],
                 "pressedForeground": p["accent"], "visitedForeground": p["accent"],
                 "secondaryForeground": p["accent"], "focusedBorderColor": p["accent"]},
        "Label": {"errorForeground": p["err"], "warningForeground": p["warn"]},
        "ProgressBar": {"progressColor": p["accent"],
                        "indeterminateStartColor": p["gold"],
                        "indeterminateEndColor": p["accent"], "trackColor": p["border"]},
        "SearchEverywhere": {"List.settingsBackground": p["raised"],
                             "Tab": {"selectedBackground": p["sel"],
                                     "selectedForeground": p["fg"]},
                             "Advertiser": {"foreground": p["fg3"],
                                            "background": p["panel"]}},
        "CompletionPopup": {"foreground": p["fg2"], "matchForeground": p["gold"],
                            "Advertiser": {"foreground": p["fg3"],
                                           "background": p["panel"]}},
        "ParameterInfo": {"background": p["raised"], "currentOverloadBackground": p["sel"],
                          "borderColor": p["border"], "foreground": p["fg2"],
                          "currentParameterForeground": p["fg"],
                          "disabledForeground": p["fg3"], "infoForeground": p["fg2"],
                          "lineSeparatorColor": p["raised"]},
        "SearchMatch": {"startBackground": p["gold"], "endBackground": p["gold"]},
        "OnePixelDivider.background": p["border"],
        "Borders.color": p["win"],
        "Borders.ContrastBorderColor": p["win"],
        "Counter": {"background": p["border"], "foreground": p["fg"]},
        "DragAndDrop": {"borderColor": p["accent"], "rowBackground": p["accent"] + "26"},
        "ValidationTooltip": {"errorBackground": p["errBg"], "errorBorderColor": p["err"],
                             "errorForeground": p["fg"],
                             "warningBackground": p["warnBg"],
                             "warningBorderColor": p["warn"],
                             "warningForeground": p["fg"]},
        "Window.border": "1,1,1,1," + p["border"],
        "Window.undecorated.border": "1,1,1,1," + p["border"],
        "SpeedSearch": {"background": p["win"], "borderColor": p["border"],
                        "errorForeground": p["err"]},
        "Slider": {"buttonColor": p["fg2"], "buttonBorderColor": p["panel"],
                   "tickColor": p["fg3"], "trackColor": p["border"]},
        "Tag.background": p["hover"],
        "Tag": {"foreground": p["fg2"]},
        "MemoryIndicator": {"allocatedBackground": p["panel"],
                            "usedBackground": p["accent"] + "80"},
        "WelcomeScreen": {"background": p["win"], "Details.background": p["win"],
                          "SidePanel.background": p["panel"]},
        "WelcomeScreen.Details.background": p["win"],
        "ToolTip": {"background": p["raised"], "borderColor": p["border"],
                    "foreground": p["fg"], "infoForeground": p["fg2"],
                    "shortcutForeground": p["fg2"]},
        "Editor": {"SearchField": {"background": p["win"]},
                   "Toolbar": {"borderColor": p["border"]}},
        "Editor.SearchField.background": p["win"],
        "Editor.ToolTip": {"foreground": p["fg"], "background": p["raised"],
                           "border": p["border"]},
        "GotItTooltip": {"background": p["accent"], "borderColor": p["accent"],
                         "foreground": p["onAccent"],
                         "Header.foreground": p["onAccent"],
                         "shortcutForeground": p["onAccent"],
                         "shortcutBackground": p["sel"],
                         "codeForeground": p["onAccent"],
                         "codeBackground": p["accent"],
                         "linkForeground": p["onAccent"],
                         "imageBorderColor": p["border"],
                         "animationBackground": p["win"],
                         "iconFillColor": p["accent"],
                         "iconBorderColor": p["onAccent"]},
        "VersionControl": {
            "Log": {"Commit": {"currentBranchBackground": p["sel"],
                               "unmatchedForeground": p["fg3"],
                               "Reference.foreground": p["fg3"]},
                    "Graph": {"saturation": 0.6, "brightness": 0.6}},
            "GitLog": {"headIconColor": p["gold"], "localBranchIconColor": p["accent"],
                       "otherIconColor": p["fg2"],
                       "remoteBranchIconColor": p["info"], "tagIconColor": p["fg2"]},
            "MarkerPopup": {"borderColor": p["border"]},
        },
        "Bookmark": {"Mnemonic.iconForeground": p["fg"],
                     "MnemonicAvailable.borderColor": p["border"],
                     "MnemonicAssigned.background": p["gold"],
                     "MnemonicAssigned.foreground": p["onGold"],
                     "MnemonicCurrent.background": p["accent"]},
        "Separator": {"separatorColor": p["border"], "foreground": p["fg3"]},
        "Shortcut": {"foreground": p["fg2"], "borderColor": p["border"],
                     "backgroundOpacity": 0},
        "Shortcut.borderColor": p["border"],
        "StatusBar.borderColor": p["border"],
        "VersionControl.MarkerPopup.borderColor": p["border"],
        "TabbedPane.hoverColor": p["hover"],
        "List.Tag.background": p["hover"],
        "SearchMatch.startBackground": p["gold"],
        "SearchMatch.endBackground": p["gold"],
        "Component.borderColor": p["border"],
        "DragAndDrop.borderColor": p["accent"],
    }


# --------------------------------------------------------------- validation --
def collect_keys(node, prefix=""):
    out = set()
    for k, v in node.items():
        out.add(k)
        if isinstance(v, dict):
            out |= collect_keys(v, k)
    return out


def flatten(node, prefix=""):
    for k, v in node.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            yield from flatten(v, key)
        else:
            yield key, v


def is_colour(v):
    return isinstance(v, str) and v.startswith("#")


def valid_colour(v):
    if not is_colour(v):
        return True
    body = v[1:]
    return len(body) in (6, 8) and all(c in "0123456789abcdefABCDEF" for c in body)


def validate(name, p, theme):
    """Two-level key check against the bundled themes.

    Component names must be known top-level keys, and every leaf property name
    must appear as a leaf somewhere in the bundled themes.  Nesting is not
    compared path-by-path: each bundled theme overrides a different subset, so
    an absent path is not evidence of a typo, but a misspelled property is.
    """
    problems = []
    ui_tree = theme["ui"]
    ref = json.load(open(WHITELIST, encoding="utf-8"))
    top_allowed, leaf_allowed = set(ref["top"]), set(ref["leaf"])

    parent = p["parent"]
    if parent not in VALID_PARENTS:
        problems.append(f"parentTheme {parent!r} is not a bundled theme")
    elif VALID_PARENTS[parent] != p["dark"]:
        problems.append(f"dark={p['dark']} disagrees with parent {parent!r} "
                        f"(dark={VALID_PARENTS[parent]})")

    unknown_top = sorted(set(ui_tree) - top_allowed)
    if unknown_top:
        problems.append(f"unknown top-level ui keys: {unknown_top}")

    bad_leaf = {}
    for path, v in flatten(ui_tree):
        parts = path.split(".")
        # a legal property name may itself contain dots
        # (SearchEverywhere uses "List.settingsBackground")
        if not any(".".join(parts[i:]) in leaf_allowed for i in range(len(parts))):
            bad_leaf[path] = path.rsplit(".", 1)[-1]
    if bad_leaf:
        problems.append(f"unknown property names: {sorted(bad_leaf)}")

    for k, v in flatten(ui_tree):
        if not valid_colour(v):
            problems.append(f"{k}: malformed colour {v!r}")

    floor = 4.5
    checks = [
        ("* foreground on panel", p["fg"], p["panel"], floor),
        ("* foreground on window", p["fg"], p["win"], floor),
        ("secondary fg on panel", p["fg2"], p["panel"], floor),
        ("muted fg on panel", p["fg3"], p["panel"], 3.0),
        ("button text on accent", p["onAccent"], p["accent"], floor),
        ("bookmark text on gold", p["onGold"], p["gold"], floor),
        ("selection text on selection bg", p["fg"], p["sel"], floor),
        ("error label", p["err"], p["panel"], floor),
        ("warning label", p["warn"], p["panel"], floor),
        ("link on panel", p["accent"], p["panel"], floor),
        ("breadcrumb fg on statusbar", p["fg2"], p["panel"], floor),
    ]
    for label, fg, bg, f in checks:
        c = contrast(fg, bg)
        if c < f:
            problems.append(f"{label}: {fg} on {bg} = {c}, needs {f}")
    return problems


def fix_palette(name, p):
    """Raise the pairs the checks care about until they clear their floor."""
    changes = []
    pairs = [("onAccent", "accent", 4.5), ("onGold", "gold", 4.5),
             ("fg", "panel", 4.5), ("fg", "win", 4.5), ("fg2", "panel", 4.5),
             ("fg3", "panel", 3.0), ("err", "panel", 4.5), ("warn", "panel", 4.5),
             ("accent", "panel", 4.5), ("fg", "sel", 4.5)]
    for fg_key, bg_key, floor in pairs:
        old = p[fg_key]
        new = adjust(old, p[bg_key], floor)
        if new.lower() != old.lower():
            changes.append(f"    {name} {fg_key:9s} {old} -> {new}  "
                           f"({contrast(old, p[bg_key])} -> {contrast(new, p[bg_key])} "
                           f"on {bg_key}, floor {floor})")
            p[fg_key] = new
    return changes


def build_json(name, p):
    return {
        "name": name,
        "dark": p["dark"],
        "author": "kb",
        "parentTheme": p["parent"],
        "editorScheme": "/" + SCHEME_FILES[name],
        "colors": {k: v for k, v in p.items()
                   if is_colour(v) and k not in ("dark", "parent")},
        "ui": ui(p),
    }


PLUGIN_XML = """<idea-plugin>
  <id>{pid}</id>
  <name>Anime Themes - Kurumi &amp; Miku</name>
  <version>1.0.0</version>
  <category>UI</category>
  <vendor>kb</vendor>
  <description><![CDATA[
    四个 IntelliJ IDEA 主题，配色取自两张动漫原图（时崎狂三 / 初音未来），
    每张各出浅色与深色一版：界面主题（面板、工具窗、标签页、工具栏、状态栏、
    弹窗、滚动条）+ 配套编辑器配色方案，选中一个主题即整套生效。<br/>
    Four IntelliJ IDEA themes (Kurumi Tokisaki / Hatsune Miku, light + dark each).
    Each carries a matching editor colour scheme via <code>editorScheme</code>.
  ]]></description>
  <idea-version since-build="243"/>
  <depends>com.intellij.modules.platform</depends>
  <extensions defaultExtensionNs="com.intellij">
{providers}
  </extensions>
</idea-plugin>
"""

PROVIDER = '    <themeProvider id="{pid}.{slug}" path="/{file}"/>'


def slugify(name):
    return "".join(c.lower() if c.isalnum() else "." for c in name).strip(".")


def write_outputs():
    os.makedirs(DIST, exist_ok=True)
    problems_total = []
    for name, p in PALETTES.items():
        print(f"\n{name}")
        for line in fix_palette(name, p):
            print(line)
        body = build_json(name, p)
        problems = validate(name, p, body)
        for pr in problems:
            print(f"    PROBLEM {pr}")
            problems_total.append(f"{name}: {pr}")
        with open(os.path.join(DIST, THEME_FILES[name]), "w",
                  encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"    wrote {THEME_FILES[name]}   "
              f"parentTheme={p['parent']}  editorScheme=/{SCHEME_FILES[name]}")
    providers = "\n".join(PROVIDER.format(pid=PLUGIN_ID, slug=slugify(n),
                                          file=THEME_FILES[n]) for n in PALETTES)
    with open(os.path.join(DIST, "plugin.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(PLUGIN_XML.format(pid=PLUGIN_ID, providers=providers))
    return problems_total


# Zip entries carry a timestamp, so a rebuild would otherwise produce different
# bytes for identical contents and no checksum in the docs could be trusted.
# Pinning it makes the build reproducible: same inputs, same sha256.
ZIP_DATE = (2026, 9, 18, 12, 0, 0)


def zip_entry(z, arcname, data):
    info = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def zip_file(z, path, arcname):
    with open(path, "rb") as f:
        zip_entry(z, arcname, f.read())


def build_jar():
    """Assemble the jar with the same layout as the theme plugins IDEA accepted."""
    jar = os.path.join(DIST, JAR_NAME)
    if os.path.exists(jar):
        os.remove(jar)
    with zipfile.ZipFile(jar, "w") as z:
        # the manifest must come first
        zip_entry(z, "META-INF/MANIFEST.MF", MANIFEST)
        zip_entry(z, "META-INF/", b"")
        zip_file(z, os.path.join(DIST, "plugin.xml"), "META-INF/plugin.xml")
        zip_entry(z, "META-INF/pluginIcon.svg", PLUGIN_ICON)
        for name, fn in THEME_FILES.items():
            zip_file(z, os.path.join(DIST, fn), fn)
        # editor schemes: the generator writes .icls, the jar carries .xml
        for name, fn in SCHEME_FILES.items():
            zip_file(z, os.path.join(HERE, FILES[name]), fn)
    return jar


def verify_jar(jar):
    """Check the jar the way IDEA will: descriptor, manifest, referenced paths."""
    bad = []
    with zipfile.ZipFile(jar) as z:
        entries = z.namelist()
        names = set(entries)

    for want in ("META-INF/MANIFEST.MF", "META-INF/plugin.xml",
                 "META-INF/pluginIcon.svg"):
        if want not in names:
            bad.append(f"{want} missing from jar")

    with zipfile.ZipFile(jar) as z:
        manifest = z.read("META-INF/MANIFEST.MF").decode("utf-8")
        descriptor = z.read("META-INF/plugin.xml").decode("utf-8")
    if not manifest.startswith("Manifest-Version: 1.0" + _CRLF):
        bad.append("manifest does not start with 'Manifest-Version: 1.0' + CRLF")

    try:
        root = ET.fromstring(descriptor.encode("utf-8"))
    except ET.ParseError as e:
        return [f"plugin.xml is not well-formed XML: {e}"]
    if root.tag != "idea-plugin":
        bad.append(f"descriptor root is <{root.tag}>")

    providers = [e for e in root.iter() if e.tag == "themeProvider"]
    if len(providers) != len(PALETTES):
        bad.append(f"{len(providers)} themeProvider entries, expected {len(PALETTES)}")
    for e in providers:
        path = (e.get("path") or "").lstrip("/")
        if path not in names:
            bad.append(f"themeProvider path /{path} not in jar")
        if not e.get("id"):
            bad.append("themeProvider without an id")

    if not any(e.tag == "depends" for e in root.iter()):
        bad.append("descriptor declares no <depends>")

    # every theme json must parse and point at a scheme that is really in the jar
    for name, fn in THEME_FILES.items():
        if fn not in names:
            bad.append(f"{fn} missing from jar")
            continue
        with zipfile.ZipFile(jar) as z:
            body = json.loads(z.read(fn).decode("utf-8"))
        scheme = (body.get("editorScheme") or "").lstrip("/")
        if scheme not in names:
            bad.append(f"{fn}: editorScheme /{scheme} not in jar")
        for key in ("name", "dark", "parentTheme", "editorScheme", "ui"):
            if key not in body:
                bad.append(f"{fn}: missing {key!r}")
        if body.get("dark") != VALID_PARENTS.get(body.get("parentTheme")):
            bad.append(f"{fn}: dark flag disagrees with parentTheme")
    return bad


def main():
    problems = write_outputs()
    jar = build_jar()
    with zipfile.ZipFile(jar) as z:
        entries = sorted(z.namelist())
    print(f"\n{os.path.relpath(jar, HERE)}  {os.path.getsize(jar):,} bytes, "
          f"{len(entries)} entries")
    for e in entries:
        print(f"    {e}")
    problems += verify_jar(jar)
    print()
    if problems:
        print(f"FAILED ({len(problems)}):")
        for p in problems:
            print("   ", p)
        raise SystemExit(1)
    print("all theme checks passed")


if __name__ == "__main__":
    main()
