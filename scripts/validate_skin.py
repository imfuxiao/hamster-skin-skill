#!/usr/bin/env python3
"""元书输入法皮肤校验器。

用法:
    python3 validate_skin.py <皮肤目录>

退出码: 0 = 无错误（可能有警告），1 = 有错误，2 = 用法/环境问题。

YAML 解析：优先使用 PyYAML；未安装时自动回退到系统 ruby（macOS 自带）
仅做 YAML→JSON 转换，全部校验逻辑均在本文件中。
"""

import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------- YAML 解析

try:
    import yaml as _pyyaml
except ImportError:
    _pyyaml = None

_RUBY = None


def _find_ruby():
    global _RUBY
    if _RUBY is not None:
        return _RUBY or None
    for cand in ("/usr/bin/ruby", "ruby"):
        try:
            subprocess.run(
                [cand, "-ryaml", "-e", ""],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            _RUBY = cand
            return cand
        except (OSError, subprocess.CalledProcessError):
            continue
    _RUBY = ""
    return None


class YamlError(Exception):
    pass


def load_yaml(path):
    """把 YAML 文件解析成 Python 对象（合并键 << 会被展开）。"""
    if _pyyaml is not None:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return _pyyaml.safe_load(fh)
        except _pyyaml.YAMLError as exc:
            raise YamlError(str(exc))

    ruby = _find_ruby()
    if ruby is None:
        sys.stderr.write(
            "错误：需要一个 YAML 解析器。\n"
            "  方案 A：pip install pyyaml（或在 venv 中安装）\n"
            "  方案 B：安装 ruby（macOS 自带 /usr/bin/ruby）\n"
        )
        sys.exit(2)

    script = (
        "require 'yaml'; require 'json'; "
        "begin; d = YAML.load_file(ARGV[0], aliases: true); "
        "rescue ArgumentError; d = YAML.load_file(ARGV[0]); end; "
        "print JSON.generate({'ok' => d})"
    )
    proc = subprocess.run(
        [ruby, "-e", script, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if proc.returncode != 0:
        raise YamlError(proc.stderr.decode("utf-8", "replace").strip().split("\n")[-1])
    return json.loads(proc.stdout.decode("utf-8"))["ok"]


# ---------------------------------------------------------------- 枚举与常量

BUTTON_STYLE_TYPES = ["geometry", "systemImage", "assetImage", "fileImage", "text"]

CELL_TYPES = [
    "button", "symbols", "classifiedSymbols", "subClassifiedSymbols",
    "horizontalSymbols", "horizontalCandidates", "verticalCandidates",
    "numericSymbols", "categorySymbols", "t9Symbols", "t9HorizontalSymbols",
]

ALIGNMENTS = [
    "leftTop", "left", "leftBottom", "centerTop", "center", "centerBottom",
    "rightTop", "right", "rightBottom",
]

CONTENT_MODES = ["scaleToFill", "scaleAspectFit", "scaleAspectFill", "center"]
GRADIENT_TYPES = ["axial", "conic", "radial"]
FONT_WEIGHTS = [
    "ultraLight", "thin", "light", "regular", "medium",
    "semibold", "bold", "heavy", "black",
]
NOTIFICATION_TYPES = ["rime", "keyboardAction", "returnKeyType", "preeditChanged"]
RIME_NOTIFICATION_TYPES = ["optionChanged", "schemaChanged"]
ANIMATION_TYPES = ["scale", "cartoon", "physics", "transform"]
ANIMATION_TRIGGERS = ["press", "release", "both"]
TIMING_FUNCTIONS = ["linear", "easeIn", "easeOut", "easeInEaseOut", "default"]
POSITION_UNITS = ["point", "layer", "button"]

# 根节点中的结构性 Key（其余值为映射的根 Key 都是样式名）
STRUCTURAL_KEYS = [
    "preeditHeight", "toolbarHeight", "keyboardHeight",
    "preeditStyle", "toolbarStyle", "toolbarLayout",
    "keyboardStyle", "keyboardLayout",
    "horizontalCandidatesStyle", "horizontalCandidatesLayout",
    "verticalCandidatesStyle", "verticalCandidatesLayout",
    "candidateContextMenu",
    "floatTargetScale", "floatKeyboardAlpha", "floatKeyboardLockedState",
]

LAYOUT_KEYS = [
    "toolbarLayout", "keyboardLayout",
    "horizontalCandidatesLayout", "verticalCandidatesLayout",
]

# 值为「样式名 / 样式名数组 / 条件样式数组」的 Key —— 需要检查引用是否存在
STYLE_REF_KEYS = [
    "backgroundStyle", "foregroundStyle",
    "uppercasedStateForegroundStyle", "capsLockedStateForegroundStyle",
    "swipeUpForegroundStyle", "swipeDownForegroundStyle",
    "hintStyle", "hintSymbolsStyle", "hintSymbolsGridStyle",
    "selectedBackgroundStyle", "cellStyle", "candidateStyle", "selectedStyle",
    "animation", "notification", "symbolStyles",
]

ACTION_KEYS = [
    "action", "uppercasedStateAction", "preeditStateAction", "repeatAction",
    "swipeUpAction", "swipeDownAction", "notificationKeyboardAction",
]

SHORTCUTS = [
    "#简繁切换", "#中英切换", "#RimeSwitcher", "#次选上屏", "#三选上屏", "#方案切换",
    "#行首", "#行尾", "#换行", "#Enter", "#重输", "#左手模式", "#右手模式",
    "#cut", "#copy", "#paste",
    "#subCollectionPageUp", "#subCollectionPageDown",
    "#verticalCandidatesPageUp", "#verticalCandidatesPageDown",
    "#showPhraseView", "#showPasteboardView", "#toggleScriptView",
    "#candidatesBarStateToggle", "#rimePreviousPage", "#rimeNextPage",
    "#toggleEmbeddedInputMode", "#keyboardPerformance", "#keyboardMenu",
    "#clearSystemPasteboard",
]

ACTION_SCALARS = [
    "backspace", "command", "control", "dictation", "dismissKeyboard", "escape",
    "function", "moveCursorBackward", "moveCursorForward", "nextKeyboard",
    "option", "settings", "space", "systemSettings", "tab", "shift", "enter",
    "returnPrimaryKeyboard", "returnLastKeyboard",
    "symbolicKeyboardLockStateToggle", "none",
]

ACTION_OBJECT_KEYS = [
    "combine", "character", "symbol", "shortcutCommand", "shortcut",
    "floatKeyboardType", "sendKeys", "openURL", "runScript", "openScript",
    "keyboardType", "switchRimeSchema",
]

# 只在本层查找、不会穿透 YAML 合并键 `<<` 的 Key
NO_MERGE_KEYS = [
    "maxColumns", "maxRows", "contentRightToLeft", "colorLocation",
    "colorStartPoint", "colorEndPoint", "colorGradientType", "shadowOpacity",
    "type", "floatKeyboardAlpha", "floatKeyboardLockedState", "floatTargetScale",
]

CONFIG_META_KEYS = ["name", "author", "fontFace", "keySound"]

COLOR_RE = re.compile(r"\A#?(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\Z")


# ---------------------------------------------------------------- 报告

class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, msg):
        self.errors.append("%s: %s" % (where, msg))

    def warn(self, where, msg):
        self.warnings.append("%s: %s" % (where, msg))

    def print_out(self):
        if self.warnings:
            print("\n警告 (%d)" % len(self.warnings))
            for w in self.warnings:
                print("  ! %s" % w)
        if self.errors:
            print("\n错误 (%d)" % len(self.errors))
            for e in self.errors:
                print("  x %s" % e)
        if not self.errors and not self.warnings:
            print("\n通过：未发现问题。")
        else:
            print("\n合计：%d 个错误，%d 个警告。" % (len(self.errors), len(self.warnings)))


# ---------------------------------------------------------------- 工具

def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def extract_style_names(value):
    """从「样式名 / 样式名数组 / 条件样式数组」中取出全部被引用的样式名。"""
    names = []
    if isinstance(value, str):
        names.append(value)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict) and "styleName" in item:
                names.extend(
                    [s for s in as_list(item["styleName"]) if isinstance(s, str)]
                )
    return names


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def scan_merge_traps(path):
    """文本扫描：找出被 `<<` 合并、但内部含有「不穿透合并键」的锚点。

    YAML 解析器会在加载时展开 `<<`，因此这一检查只能在原始文本上做。
    返回 [(锚点名, [命中的 Key, ...]), ...]
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return []

    merged = set(re.findall(r"<<\s*:\s*\*([A-Za-z0-9_\-]+)", "\n".join(lines)))
    if not merged:
        return []

    hits = []
    for idx, line in enumerate(lines):
        m = re.search(r"&([A-Za-z0-9_\-]+)", line)
        if not m or m.group(1) not in merged:
            continue
        anchor = m.group(1)
        base_indent = len(line) - len(line.lstrip())
        block = [line]
        for nxt in lines[idx + 1:]:
            if not nxt.strip():
                continue
            if len(nxt) - len(nxt.lstrip()) <= base_indent:
                break
            block.append(nxt)
        text = "\n".join(block)
        found = [k for k in NO_MERGE_KEYS if re.search(r"(?<![A-Za-z])%s\s*:" % k, text)]
        if found:
            hits.append((anchor, found))
    return hits


# ---------------------------------------------------------------- 校验器

class SkinValidator(object):
    def __init__(self, root, report):
        self.root = root
        self.r = report

    def validate(self):
        config_path = os.path.join(self.root, "config.yaml")
        if not os.path.isfile(config_path):
            self.r.error("config.yaml", "文件不存在，皮肤根目录必须包含 config.yaml")
            return

        try:
            config = load_yaml(config_path)
        except YamlError as exc:
            self.r.error("config.yaml", "YAML 语法错误：%s" % exc)
            return

        if not isinstance(config, dict):
            self.r.error("config.yaml", "内容不是一个映射（mapping）")
            return

        self.validate_config(config)
        for rel in self.keyboard_files(config):
            self.validate_keyboard_file(rel)
        self.check_demo_png()

    # -------------------------------------------------------- config.yaml

    def validate_config(self, config):
        kb_types = dict(
            (k, v) for k, v in config.items() if k not in CONFIG_META_KEYS
        )

        if not kb_types:
            self.r.error("config.yaml", "没有声明任何键盘类型")
        elif "pinyin" not in kb_types:
            self.r.warn("config.yaml", "未声明 pinyin 键盘，中文输入将无法使用")

        for ktype, entry in kb_types.items():
            where = "config.yaml/%s" % ktype
            if not isinstance(entry, dict):
                self.r.error(where, "值必须是包含 iPhone / iPad 的映射")
                continue
            if "iPhone" not in entry and "iPad" not in entry:
                self.r.error(where, "至少需要提供 iPhone 或 iPad 之一")

            for device, orientations in entry.items():
                if device not in ("iPhone", "iPad"):
                    self.r.warn(where, "未知设备键 `%s`（应为 iPhone / iPad）" % device)
                    continue
                dwhere = "%s/%s" % (where, device)
                if not isinstance(orientations, dict):
                    self.r.error(dwhere, "值必须是映射")
                    continue
                valid = (
                    ["portrait", "landscape", "floating"]
                    if device == "iPad"
                    else ["portrait", "landscape"]
                )
                for o in orientations:
                    if o not in valid:
                        self.r.warn(
                            dwhere, "未知方向键 `%s`（应为 %s）" % (o, " / ".join(valid))
                        )
                for o in ("portrait", "landscape"):
                    if not orientations.get(o):
                        self.r.warn(dwhere, "缺少 %s，该场景下键盘会显示空白" % o)

        if "fontFace" in config:
            self.validate_font_face(config["fontFace"])
        if "keySound" in config:
            self.validate_key_sound(config["keySound"])

    def validate_font_face(self, ff):
        if not isinstance(ff, list):
            self.r.error("config.yaml/fontFace", "必须是数组")
            return
        for i, face in enumerate(ff):
            where = "config.yaml/fontFace[%d]" % i
            if not isinstance(face, dict):
                self.r.error(where, "必须是映射")
                continue
            url = str(face.get("url") or "")
            name = str(face.get("name") or "")
            if not url and not name:
                self.r.error(where, "url 与 name 至少提供一个")
            if url and not os.path.isfile(os.path.join(self.root, "fonts", url)):
                self.r.error(where, "字体文件不存在：fonts/%s" % url)
            for j, rg in enumerate(as_list(face.get("ranges"))):
                if not isinstance(rg, dict):
                    continue
                if not isinstance(rg.get("location"), int) or not isinstance(
                    rg.get("length"), int
                ):
                    self.r.error(
                        "%s/ranges[%d]" % (where, j), "location 与 length 必须是整数"
                    )

    def validate_key_sound(self, ks):
        if not isinstance(ks, dict):
            self.r.error("config.yaml/keySound", "必须是映射")
            return
        for k in ("input", "delete", "system"):
            v = ks.get(k)
            if not v:
                continue
            if not os.path.isfile(os.path.join(self.root, "sound", str(v))):
                self.r.error("config.yaml/keySound", "音频文件不存在：sound/%s" % v)
        for i, a in enumerate(as_list(ks.get("actions"))):
            where = "config.yaml/keySound/actions[%d]" % i
            if not isinstance(a, dict) or not a.get("action") or not a.get("url"):
                self.r.error(where, "action 与 url 都是必填")
                continue
            if not os.path.isfile(os.path.join(self.root, "sound", str(a["url"]))):
                self.r.error(where, "音频文件不存在：sound/%s" % a["url"])

    def keyboard_files(self, config):
        names = set()
        for ktype, entry in config.items():
            if ktype in CONFIG_META_KEYS or not isinstance(entry, dict):
                continue
            for orientations in entry.values():
                if not isinstance(orientations, dict):
                    continue
                for n in orientations.values():
                    if n:
                        names.add(str(n))

        files = []
        for mode in ("light", "dark"):
            for n in sorted(names):
                rel = os.path.join(mode, "%s.yaml" % n)
                if os.path.isfile(os.path.join(self.root, rel)):
                    files.append(rel)
                else:
                    self.r.error("config.yaml", "引用的键盘文件不存在：%s" % rel)
        return files

    def check_demo_png(self):
        if not os.path.isfile(os.path.join(self.root, "demo.png")):
            self.r.warn("皮肤目录", "缺少 demo.png（应用中的皮肤预览图）")

    # ---------------------------------------------------- 键盘配置文件

    def validate_keyboard_file(self, rel):
        path = os.path.join(self.root, rel)
        try:
            node = load_yaml(path)
        except YamlError as exc:
            self.r.error(rel, "YAML 语法错误：%s" % exc)
            return

        if not isinstance(node, dict):
            self.r.error(rel, "内容不是一个映射（mapping）")
            return

        for k in ("preeditHeight", "toolbarHeight", "keyboardHeight"):
            if k not in node:
                self.r.error(rel, "缺少必填 Key `%s`" % k)
                continue
            v = node[k]
            ok = is_number(v)
            if not ok and isinstance(v, str):
                if v.endswith("vh"):
                    ok = True
                else:
                    try:
                        float(v)
                        ok = True
                    except ValueError:
                        ok = False
            if not ok:
                self.r.error(
                    "%s/%s" % (rel, k), "值 `%r` 无效，应为数值或 '<数值>vh'" % (v,)
                )

        if not node.get("keyboardStyle"):
            self.r.warn(rel, "未定义 keyboardStyle，按键区不会被创建")
        if not node.get("toolbarStyle"):
            self.r.warn(rel, "未定义 toolbarStyle，工具栏区不会被创建")

        # 先扫一遍，收集 dataSource 指向的根 Key（它们是数组，不是样式）
        self.data_sources = set()
        for value in node.values():
            if isinstance(value, dict) and isinstance(value.get("dataSource"), str):
                self.data_sources.add(value["dataSource"])

        # 只有值为映射的根 Key 才算「样式」；标量根 Key 是多余内容
        candidate_keys = [k for k in node if k not in STRUCTURAL_KEYS]
        style_names = set(k for k in candidate_keys if isinstance(node[k], dict))
        stray = [
            k for k in candidate_keys
            if not isinstance(node[k], dict) and k not in self.data_sources
        ]
        if stray:
            self.r.warn(
                rel,
                "根节点存在 %d 个多余的非映射 Key（不会被当作样式使用）：%s"
                % (len(stray), ", ".join(sorted(stray)[:6])),
            )

        referenced = set()

        # 预编辑前景样式只用于取字号 / 字重 / textColor，不渲染成文字图层，
        # 因此豁免「buttonStyleType 为 text 却没有 text」的检查。
        preedit_fg = set()
        if isinstance(node.get("preeditStyle"), dict):
            preedit_fg.update(
                extract_style_names(node["preeditStyle"].get("foregroundStyle"))
            )

        # 集合视图单元格（cellStyle）的文字由 dataSource 提供，同样豁免该检查。
        for value in node.values():
            if not isinstance(value, dict):
                continue
            for cell_name in extract_style_names(value.get("cellStyle")):
                cell = node.get(cell_name)
                if isinstance(cell, dict):
                    preedit_fg.update(extract_style_names(cell.get("foregroundStyle")))

        for lk in LAYOUT_KEYS:
            if lk in node:
                self.validate_layout("%s/%s" % (rel, lk), node[lk], referenced)

        for k in (
            "preeditStyle", "toolbarStyle", "keyboardStyle",
            "horizontalCandidatesStyle", "verticalCandidatesStyle",
        ):
            if node.get(k):
                self.collect_refs(node[k], referenced)

        for i, item in enumerate(as_list(node.get("candidateContextMenu"))):
            where = "%s/candidateContextMenu[%d]" % (rel, i)
            if not isinstance(item, dict):
                self.r.error(where, "必须是映射")
                continue
            if item.get("name") is None and item.get("text") is None:
                self.r.error(where, "name 与 text 至少提供一个")
            if not item.get("action"):
                self.r.error(where, "缺少 action")
            else:
                self.validate_action(where, item["action"])

        for name, value in node.items():
            if name in STRUCTURAL_KEYS or not isinstance(value, dict):
                continue
            self.validate_style_node(rel, name, value, referenced, name in preedit_fg)

        for missing in sorted(referenced - style_names):
            self.r.error(rel, "引用了不存在的样式 `%s`（该处会渲染为空白）" % missing)

        for name in sorted(self.data_sources):
            if name not in node:
                self.r.error(rel, "dataSource `%s` 在根节点不存在（符号列表会是空的）" % name)
            elif not isinstance(node[name], list):
                self.r.error(rel, "dataSource `%s` 必须是数组" % name)

        unused = [n for n in (style_names - referenced) if not n.startswith("_")]
        if unused:
            shown = ", ".join(sorted(unused)[:8])
            more = " …" if len(unused) > 8 else ""
            self.r.warn(rel, "有 %d 个样式从未被引用：%s%s" % (len(unused), shown, more))

        for anchor, keys in scan_merge_traps(path):
            self.r.warn(
                rel,
                "锚点 `%s` 被 `<<` 合并使用，但其中的 %s 不会穿透合并键，"
                "请直接写在使用它的节点内" % (anchor, " / ".join(keys)),
            )

    # ------------------------------------------------------------- 布局

    def validate_layout(self, path, layout, referenced):
        if layout is None or layout == {}:
            return  # 空布局合法，如 toolbarLayout: {}
        if not isinstance(layout, list):
            self.r.error(path, "布局必须是数组")
            return
        self.walk_layout(path, layout, "root", referenced)

    def walk_layout(self, path, nodes, container, referenced):
        def has(key):
            return [n for n in nodes if isinstance(n, dict) and key in n]

        hstacks, vstacks, cells = has("HStack"), has("VStack"), has("Cell")

        if hstacks and vstacks:
            self.r.error(path, "同级节点不能同时出现 HStack 与 VStack")
        if hstacks and cells:
            self.r.error(path, "同级节点不能同时出现 HStack 与 Cell")
        if vstacks and cells:
            self.r.error(path, "同级节点不能同时出现 VStack 与 Cell")
        if container == "root" and cells:
            self.r.error(
                path, "Cell 必须是 HStack 或 VStack 的子节点，不能直接放在布局根数组中"
            )

        for i, n in enumerate(nodes):
            where = "%s[%d]" % (path, i)
            if not isinstance(n, dict):
                self.r.error(where, "布局元素必须是映射（HStack / VStack / Cell）")
                continue
            unknown = [k for k in n if k not in ("HStack", "VStack", "Cell")]
            if unknown:
                self.r.warn(where, "未知布局 Key：%s" % ", ".join(unknown))

            for kind in ("HStack", "VStack"):
                if kind not in n:
                    continue
                stack = n[kind]
                kwhere = "%s/%s" % (where, kind)
                if not isinstance(stack, dict):
                    self.r.error(kwhere, "值必须是映射")
                    continue
                if isinstance(stack.get("style"), str):
                    referenced.add(stack["style"])
                subviews = stack.get("subviews")
                if subviews is None:
                    self.r.warn(kwhere, "没有 subviews，该容器不会渲染任何内容")
                elif not isinstance(subviews, list):
                    self.r.error("%s/subviews" % kwhere, "必须是数组")
                else:
                    self.walk_layout(
                        "%s/subviews" % kwhere,
                        subviews,
                        "hstack" if kind == "HStack" else "vstack",
                        referenced,
                    )

            if "Cell" in n:
                cell = n["Cell"]
                if isinstance(cell, str):
                    referenced.add(cell)
                else:
                    self.r.error(
                        "%s/Cell" % where,
                        "值必须是样式名字符串，当前为 %s" % type(cell).__name__,
                    )

    # --------------------------------------------------------- 样式节点

    def collect_refs(self, node, referenced):
        if not isinstance(node, dict):
            return
        for k in STYLE_REF_KEYS:
            if k in node:
                referenced.update(extract_style_names(node[k]))

    def validate_style_node(self, rel, name, node, referenced, is_preedit_fg=False):
        where = "%s/%s" % (rel, name)
        self.collect_refs(node, referenced)

        if "symbolRows" in node:
            rows = node["symbolRows"]
            if isinstance(rows, list):
                for row in rows:
                    for c in as_list(row):
                        if isinstance(c, str) and c:
                            referenced.add(c)
            else:
                self.r.error("%s/symbolRows" % where, "必须是二维数组")

        # dataSource 指向根节点下的一个「数组」，不是样式节点，单独记录后另行校验
        if isinstance(node.get("dataSource"), str):
            self.data_sources.add(node["dataSource"])

        self.validate_enum(where, node, "buttonStyleType", BUTTON_STYLE_TYPES)
        self.validate_enum(where, node, "type", CELL_TYPES)
        self.validate_enum(where, node, "contentMode", CONTENT_MODES)
        self.validate_enum(where, node, "colorGradientType", GRADIENT_TYPES)
        self.validate_enum(where, node, "fontWeight", FONT_WEIGHTS)
        self.validate_enum(where, node, "notificationType", NOTIFICATION_TYPES)
        self.validate_enum(
            where, node, "rimeNotificationType", RIME_NOTIFICATION_TYPES
        )
        self.validate_enum(where, node, "animationType", ANIMATION_TYPES)
        if isinstance(node.get("bounds"), dict):
            self.validate_enum(
                "%s/bounds" % where, node["bounds"], "alignment", ALIGNMENTS
            )

        self.validate_button_style_type(where, node, is_preedit_fg)
        self.validate_colors(where, node)
        self.validate_notification(where, node)
        self.validate_animation(where, node, referenced)
        self.validate_hint_symbols(where, node)

        for k in ACTION_KEYS:
            if k in node:
                self.validate_action("%s/%s" % (where, k), node[k])

        if "animation" in node and not isinstance(node["animation"], list):
            self.r.error(
                "%s/animation" % where, "必须是数组，写成单个字符串不会生效"
            )

    def validate_enum(self, where, node, key, allowed):
        if key not in node:
            return
        v = node[key]
        if v is None:
            return
        if str(v) not in allowed:
            self.r.error(
                "%s/%s" % (where, key),
                "值 `%s` 不是合法枚举，可选：%s" % (v, " / ".join(allowed)),
            )

    def validate_button_style_type(self, where, node, is_preedit_fg=False):
        t = node.get("buttonStyleType")
        if t is None:
            return

        if t == "systemImage":
            if not node.get("systemImageName"):
                self.r.error(where, "buttonStyleType 为 systemImage，但缺少 systemImageName")
        elif t == "assetImage":
            if not node.get("assetImageName"):
                self.r.error(where, "buttonStyleType 为 assetImage，但缺少 assetImageName")
        elif t == "fileImage":
            if node.get("normalImage") is None and node.get("highlightImage") is None:
                self.r.error(
                    where, "buttonStyleType 为 fileImage，但既没有 normalImage 也没有 highlightImage"
                )
            for k in ("normalImage", "highlightImage"):
                img = node.get(k)
                if img is None:
                    continue
                if not isinstance(img, dict) or not img.get("file") or not img.get("image"):
                    self.r.error(
                        "%s/%s" % (where, k), "fileImage 需要同时提供 file 与 image 两个子 Key"
                    )
        elif t == "text":
            if "text" not in node and not is_preedit_fg:
                self.r.warn(
                    where, "buttonStyleType 为 text，但没有 text，按键上不会显示任何文字"
                )

    def validate_colors(self, where, node):
        for k, v in node.items():
            if not isinstance(k, str):
                continue
            if not (k.lower().endswith("color") or k in ("normalColor", "highlightColor")):
                continue
            for c in as_list(v):
                if not isinstance(c, str):
                    continue
                if not COLOR_RE.match(c):
                    self.r.error(
                        "%s/%s" % (where, k),
                        "颜色 `%s` 格式非法，应为 #RRGGBB 或 #RRGGBBAA" % c,
                    )

    def validate_notification(self, where, node):
        t = node.get("notificationType")
        if t is None:
            return

        if t == "rime":
            rt = node.get("rimeNotificationType")
            if rt is None:
                self.r.error(where, "notificationType 为 rime，但缺少 rimeNotificationType")
            elif rt == "optionChanged":
                if not node.get("rimeOptionName"):
                    self.r.error(
                        where, "rimeNotificationType 为 optionChanged，但缺少 rimeOptionName"
                    )
                if "rimeOptionValue" not in node:
                    self.r.error(
                        where, "rimeNotificationType 为 optionChanged，但缺少 rimeOptionValue"
                    )
            elif rt == "schemaChanged":
                if node.get("rimeSchemaID") is None and node.get("rimeSchemaName") is None:
                    self.r.error(
                        where,
                        "rimeNotificationType 为 schemaChanged，但 rimeSchemaID 与 rimeSchemaName 都没有提供",
                    )
        elif t == "keyboardAction":
            if not node.get("notificationKeyboardAction"):
                self.r.error(
                    where, "notificationType 为 keyboardAction，但缺少 notificationKeyboardAction"
                )
        elif t == "returnKeyType":
            rk = node.get("returnKeyType")
            if rk is None:
                self.r.error(where, "notificationType 为 returnKeyType，但缺少 returnKeyType")
            elif not isinstance(rk, list) or any(
                not isinstance(x, int) or isinstance(x, bool) for x in rk
            ):
                self.r.error(
                    "%s/returnKeyType" % where, "必须是整数数组，如 [1, 4, 7]"
                )

        if node.get("backgroundStyle") is None and node.get("foregroundStyle") is None:
            self.r.warn(where, "通知节点没有定义任何样式，命中后按键会显示为空白")

    def validate_animation(self, where, node, referenced):
        t = node.get("animationType")
        if t is None:
            return
        if t in ("cartoon", "physics"):
            imgs = node.get("images")
            if not isinstance(imgs, list) or not imgs:
                self.r.error(where, "animationType 为 %s，但 images 为空，动画不会播放" % t)
        if "zPosition" in node and str(node["zPosition"]) not in ("above", "below"):
            self.r.error(
                "%s/zPosition" % where,
                "值 `%s` 无效，应为 above 或 below" % node["zPosition"],
            )
        if t == "transform":
            self.validate_enum(where, node, "trigger", ANIMATION_TRIGGERS)
            self.validate_enum(where, node, "positionUnit", POSITION_UNITS)
            # timing 既可以是预设枚举，也可以是四个数的三次贝塞尔控制点
            timing = node.get("timing")
            if isinstance(timing, list):
                if len(timing) != 4 or not all(
                    isinstance(v, (int, float)) for v in timing
                ):
                    self.r.error(
                        "%s/timing" % where,
                        "写成数组时必须是 4 个数的三次贝塞尔控制点，如 [0.34, 1.56, 0.64, 1]",
                    )
            elif timing is not None:
                self.validate_enum(where, node, "timing", TIMING_FUNCTIONS)
            # target 指向按键内的某个样式名，样式必须存在
            target = node.get("target")
            if isinstance(target, str):
                referenced.add(target)
            moved = any(
                node.get(k) is not None
                for k in ("startPosition", "endPosition", "startScale", "endScale")
            )
            if not moved and not node.get("useOpacity") and not node.get("useRotation"):
                self.r.warn(
                    where,
                    "transform 动画没有设置任何位移 / 缩放 / 旋转 / 透明度，不会有可见效果",
                )
            if node.get("detached") and not node.get("target"):
                self.r.warn(
                    where, "transform 用了 detached 但没有 target，会把整个按键复制一份浮起来"
                )
            if node.get("holdUntilRelease"):
                for key in ("trigger", "detached"):
                    if node.get(key) is not None:
                        self.r.warn(
                            "%s/%s" % (where, key),
                            "holdUntilRelease 开启时该项不生效（按下与抬起都要处理）",
                        )
            for key in ("startScale", "endScale"):
                v = node.get(key)
                if v is None:
                    continue
                if isinstance(v, dict):          # { x: , y: } 分轴缩放
                    bad = [
                        k
                        for k in ("x", "y")
                        if k in v and (not isinstance(v[k], (int, float)) or v[k] <= 0)
                    ]
                    if bad:
                        self.r.error(
                            "%s/%s" % (where, key), "x / y 必须是大于 0 的数值"
                        )
                elif not isinstance(v, (int, float)) or v <= 0:
                    self.r.error(
                        "%s/%s" % (where, key), "必须是大于 0 的数值，或 { x:, y: }"
                    )

    def validate_hint_symbols(self, where, node):
        if "symbolStyles" in node:
            v = node["symbolStyles"]
            if not isinstance(v, list) or not v:
                self.r.error(
                    "%s/symbolStyles" % where, "必须是非空数组，否则长按符号面板不会显示"
                )
        for k in ("anchor", "selected"):
            if k not in node:
                continue
            c = node[k]
            if (
                not isinstance(c, dict)
                or not isinstance(c.get("row"), int)
                or not isinstance(c.get("col"), int)
            ):
                self.r.error("%s/%s" % (where, k), "必须形如 { row: Int, col: Int }")

    # ------------------------------------------------------------- 动作

    def validate_action(self, where, action):
        if isinstance(action, str):
            if action not in ACTION_SCALARS:
                self.r.error(
                    where,
                    "动作 `%s` 不是合法的字符串动作；如果是快捷指令请写成 { shortcut: '%s' }"
                    % (action, action),
                )
        elif isinstance(action, dict):
            hit = [k for k in ACTION_OBJECT_KEYS if k in action]
            if not hit:
                self.r.error(
                    where,
                    "动作映射中没有任何可识别的 Key，可用：%s"
                    % " / ".join(ACTION_OBJECT_KEYS),
                )
                return
            if "combine" in action:
                c = action["combine"]
                if not isinstance(c, list) or not c:
                    self.r.error("%s/combine" % where, "必须是非空数组")
                else:
                    for i, sub in enumerate(c):
                        self.validate_action("%s/combine[%d]" % (where, i), sub)
            for k in ("shortcut", "shortcutCommand"):
                if k not in action:
                    continue
                v = str(action[k])
                if v not in SHORTCUTS:
                    self.r.error(
                        "%s/%s" % (where, k),
                        "快捷指令 `%s` 不存在，将被解析为「无动作」" % v,
                    )
        elif action is None:
            self.r.error(where, "动作为空")
        else:
            self.r.error(where, "动作类型非法：%s" % type(action).__name__)


# ---------------------------------------------------------------- 入口

def main(argv):
    if len(argv) < 2 or not argv[1]:
        sys.stderr.write("用法: python3 validate_skin.py <皮肤目录>\n")
        return 2
    root = argv[1]
    if not os.path.isdir(root):
        sys.stderr.write("目录不存在: %s\n" % root)
        return 2

    print("校验皮肤: %s" % os.path.abspath(root))
    report = Report()
    SkinValidator(root, report).validate()
    report.print_out()
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
