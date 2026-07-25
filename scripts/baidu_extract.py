#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把百度输入法图片皮肤（.bdi / .bds 解包后）的资源转成元书能用的形式。

用法:
    python3 baidu_extract.py <百度 skin 目录> <元书皮肤目录>/<light|dark> [布局 ini...]

    <百度 skin 目录>   含 port/ 与 res/ 的那一层，例如 .../如果坠落/dark/skin
    布局 ini           默认 py_26 py_9，可写多个（不带 .ini）

产出（写进 <元书皮肤目录>/resources/）:
    * 背景拼合图原样复制 + 同名 .yaml 图片描述文件（由 .til 翻译而来）
    * fg_<布局>.png / fg_<布局>ax.png —— 每个键的全部前景层按 gen.ini 的 [OFFSET*]
      预合成成一张与按键等大的贴图，小图名即 ini 里的段名（KEY4、TIP1 …）
    * <布局>.json —— 每个键的结构化信息（矩形、背景图、动作、长按符号…），
      写键盘 yaml 时照着它填即可

为什么要预合成：百度是「小图按原始尺寸 + 相对键心偏移」，元书的 fileImage 只能铺满
整个可视区，没有偏移概念。详见 references/baidu-skin.md。

依赖 Pillow；缺少时只跳过图片合成，仍会输出 json 与背景描述文件。
"""
import json
import os
import re
import shutil
import sys

try:
    from PIL import Image
except ImportError:
    Image = None


# --------------------------------------------------------------------------- 解析

def parse_ini(path):
    """百度的 ini / til / css 都是 [SECTION] + key=value。"""
    out, cur = {}, None
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            m = re.match(r"^\[([^\]]+)\]$", line)
            if m:
                cur = m.group(1)
                out.setdefault(cur, {})
                continue
            if cur and "=" in line:
                k, v = line.split("=", 1)
                out[cur][k.strip()] = v.strip()
    return out


def ints(s):
    return [int(float(x)) for x in s.split(",")] if s else []


class Skin:
    def __init__(self, root):
        self.root = root
        self.res = os.path.join(root, "res")
        self.port = os.path.join(root, "port")
        if not os.path.isdir(self.port):          # 有些皮肤布局文件直接放在 skin/ 下
            self.port = root
        self.css = parse_ini(os.path.join(self.res, "default.css"))
        self.gen = parse_ini(os.path.join(self.port, "gen.ini"))
        self._til, self._img = {}, {}

    # -- 资源 ------------------------------------------------------------
    def til(self, name):
        if name not in self._til:
            path = os.path.join(self.res, name + ".til")
            rects = {}
            if os.path.exists(path):
                for sec, kv in parse_ini(path).items():
                    m = re.match(r"^IMG(\d+)$", sec)
                    if m and kv.get("SOURCE_RECT"):
                        rects[int(m.group(1))] = ints(kv["SOURCE_RECT"])
            self._til[name] = rects
        return self._til[name]

    def til_insets(self, name, idx):
        """INNER_RECT（绝对坐标的九宫格内框）-> 元书的 insets 保护区。

        没有 INNER_RECT、或它与 SOURCE_RECT 一致 = 整张拉伸，返回 None。
        """
        path = os.path.join(self.res, name + ".til")
        if not os.path.exists(path):
            return None
        kv = parse_ini(path).get("IMG%d" % idx, {})
        src, inner = ints(kv.get("SOURCE_RECT", "")), ints(kv.get("INNER_RECT", ""))
        if len(src) != 4 or len(inner) != 4 or inner[2] <= 0 or inner[3] <= 0:
            return None
        left, top = inner[0] - src[0], inner[1] - src[1]
        right, bottom = src[2] - left - inner[2], src[3] - top - inner[3]
        if min(left, top, right, bottom) < 0 or max(left, top, right, bottom) == 0:
            return None
        return [max(left, 0), max(top, 0), max(right, 0), max(bottom, 0)]

    def img(self, name):
        if name not in self._img:
            self._img[name] = Image.open(os.path.join(self.res, name + ".png")).convert("RGBA")
        return self._img[name]

    def tile(self, name, idx):
        x, y, w, h = self.til(name)[idx]
        return self.img(name).crop((x, y, x + w, y + h))

    # -- 样式 ------------------------------------------------------------
    def style_img(self, sid, pressed=False):
        """STYLE 号 -> (拼合图名, 小图序号)，该样式不画图时返回 None。

        只写了 NM_IMG 的样式，按下时沿用普通态的图；
        只写了 HL_IMG 的样式（按下才出现的角标 / 水印）普通态**不画**——
        这里不能反向回退，否则那层会漏进普通态。
        """
        s = self.css.get("STYLE%s" % sid, {})
        v = s.get("HL_IMG") if pressed else None
        if not v:
            v = s.get("NM_IMG")
        if not v or "," not in v:
            return None
        f, i = v.split(",", 1)
        return f.strip(), int(i)

    def offset(self, n):
        pos = self.gen.get("OFFSET%s" % n, {}).get("POS")
        return tuple(ints(pos)) if pos else (0, 0)

    def panel_size(self, layout):
        for src in (layout, self.gen):
            v = (src.get("PANEL") or {}).get("SIZE")
            if v:
                return ints(v)
        return [1125, 595]


# --------------------------------------------------------------------------- 前景合成

def compose(skin, sec, pressed):
    """把一个 [KEY*]/[TIP*] 的全部 FORE_STYLE 层合成到与 VIEW_RECT 等大的透明画布上。"""
    rect = ints(sec.get("VIEW_RECT", ""))
    if len(rect) != 4:
        return None
    w, h = rect[2], rect[3]
    canvas = Image.new("RGBA", (max(w, 1), max(h, 1)), (0, 0, 0, 0))
    fore = [s for s in sec.get("FORE_STYLE", "").split(",") if s.strip()]
    pos = [s for s in sec.get("POS_TYPE", "").split(",") if s.strip()]
    drew = False
    for i, sid in enumerate(fore):
        ref = skin.style_img(sid, pressed)
        if not ref:
            continue                              # 空样式 / 该状态不画
        fname, idx = ref
        if idx not in skin.til(fname):
            continue
        layer = skin.tile(fname, idx)
        ox, oy = skin.offset(pos[i]) if i < len(pos) else (0, 0)
        canvas.alpha_composite(layer, ((w - layer.width) // 2 + ox,
                                       (h - layer.height) // 2 + oy))
        drew = True
    return canvas if drew else None


def pack(tiles, max_width=2048, pad=4):
    """把 {名字: Image} 按行摆进一张拼合图。"""
    x = y = rowh = height = 0
    placed = {}
    for name, im in tiles.items():
        if x + im.width > max_width and x:
            x, y, rowh = 0, y + rowh + pad, 0
        placed[name] = (x, y, im.width, im.height)
        x += im.width + pad
        rowh = max(rowh, im.height)
        height = max(height, y + im.height)
    sheet = Image.new("RGBA", (max_width, max(height, 1)), (0, 0, 0, 0))
    for name, im in tiles.items():
        sheet.paste(im, placed[name][:2])
    return sheet, placed


def rect_yaml(rects, insets=None):
    """rects: {名字: (x, y, w, h)}；insets: {名字: (左, 上, 右, 下)}，可选。"""
    insets = insets or {}
    out = []
    for n, r in rects.items():
        out.append("%s:\n  rect:   { x: %d, y: %d, width: %d, height: %d }\n" % (n, *r))
        ins = insets.get(n)
        if ins:
            out.append("  insets: { left: %d, top: %d, right: %d, bottom: %d }\n" % tuple(ins))
    return "".join(out) or "{}\n"


# --------------------------------------------------------------------------- 主流程

def opaque_height(skin, name, rect):
    """背景切片底部常有淡出到全透明的渐变，裁掉它，否则元书里会透出系统底色。"""
    x, y, w, h = rect
    try:
        alpha = skin.img(name).split()[3]
    except Exception:
        return h
    while h > 1 and alpha.getpixel((x + w // 2, y + h - 1)) < 250:
        h -= 1
    return h


def run(src, dest, layouts):
    skin = Skin(src)
    resdir = os.path.join(dest, "resources")
    os.makedirs(resdir, exist_ok=True)

    used_sheets = set()
    summary = {}

    for lname in layouts:
        path = os.path.join(skin.port, lname + ".ini")
        if not os.path.exists(path):
            print("  跳过（不存在）:", path)
            continue
        layout = parse_ini(path)
        pw, ph = skin.panel_size(layout)

        # [TIP*] 自己没有 VIEW_RECT，画布尺寸取引用它的那颗键（STAT_STYLE=S1_3|S2_4 …）
        tip_owner = {}
        for sec_name, sec in layout.items():
            if not re.match(r"^KEY\d+$", sec_name):
                continue
            for pair in (sec.get("STAT_STYLE") or "").split("|"):
                m = re.match(r"^(S\d+)_(\d+)$", pair.strip())
                if m:
                    tip_owner.setdefault("TIP" + m.group(2), (sec_name, m.group(1)))
        for tip, (owner, _state) in tip_owner.items():
            if tip in layout and not layout[tip].get("VIEW_RECT"):
                layout[tip]["VIEW_RECT"] = layout[owner].get("VIEW_RECT", "")

        keys = {}
        for sec_name, sec in layout.items():
            if not re.match(r"^(KEY|TIP)\d+$", sec_name):
                continue
            rect = ints(sec.get("VIEW_RECT", ""))
            back = skin.style_img(sec.get("BACK_STYLE")) if sec.get("BACK_STYLE") else None
            back_hl = skin.style_img(sec.get("BACK_STYLE"), True) if sec.get("BACK_STYLE") else None
            if back:
                used_sheets.add(back[0])
            if back_hl:
                used_sheets.add(back_hl[0])
            keys[sec_name] = {
                "viewRect": rect,
                "touchRect": ints(sec.get("TOUCH_RECT", "")) or rect,
                "background": {"file": back[0], "image": "k%d" % back[1]} if back else None,
                "backgroundPressed": ({"file": back_hl[0], "image": "k%d" % back_hl[1]}
                                      if back_hl else None),
                "center": sec.get("CENTER"), "show": sec.get("SHOW"),
                "up": sec.get("UP"), "down": sec.get("DOWN"),
                "left": sec.get("LEFT"), "right": sec.get("RIGHT"),
                "hold": sec.get("HOLD"), "holdSymbols": sec.get("HOLDSYM"),
                "statStyle": sec.get("STAT_STYLE"),
            }
            if sec_name in tip_owner:
                owner, state = tip_owner[sec_name]
                keys[sec_name]["tipOf"] = {"key": owner, "state": state}
        summary[lname] = {"panelSize": [pw, ph], "keys": keys,
                          "list": layout.get("LIST"), "hint": layout.get("HINT")}

        if Image is None:
            continue
        for pressed, suffix in ((False, ""), (True, "ax")):
            tiles = {}
            for sec_name, sec in layout.items():
                if re.match(r"^(KEY|TIP)\d+$", sec_name):
                    im = compose(skin, sec, pressed)
                    if im is not None:
                        tiles[sec_name] = im
            if not tiles:
                continue
            sheet, rects = pack(tiles)
            sheet.crop((0, 0, sheet.width, sheet.height)).save(
                os.path.join(resdir, "fg_%s%s.png" % (lname, suffix)))
            open(os.path.join(resdir, "fg_%s%s.yaml" % (lname, suffix)),
                 "w", encoding="utf-8").write(rect_yaml(rects))
            print("  写出 fg_%s%s（%d 块）" % (lname, suffix, len(tiles)))

    # 背景拼合图：原样复制 + 翻译 .til
    # bj = 面板背景，hint = 长按/短按气泡（由 .pop 引用，不出现在 BACK_STYLE 里）
    used_sheets.update(("bj", "hint"))
    for name in sorted(used_sheets):
        png = os.path.join(skin.res, name + ".png")
        if not os.path.exists(png):
            continue
        shutil.copy(png, os.path.join(resdir, name + ".png"))
        rects, insets = {}, {}
        for i, r in sorted(skin.til(name).items()):
            if name == "bj" and Image is not None:
                r = [r[0], r[1], r[2], opaque_height(skin, name, r)]
            rects["k%d" % i] = r
            ins = skin.til_insets(name, i)
            if ins:
                insets["k%d" % i] = ins
        open(os.path.join(resdir, name + ".yaml"), "w", encoding="utf-8").write(
            rect_yaml(rects, insets))
        print("  背景 %s（%d 块，%d 块带九宫格保护区）" % (name, len(rects), len(insets)))

    out_json = os.path.join(dest, "baidu_layout.json")
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print("  布局摘要 ->", out_json)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, dest = sys.argv[1], sys.argv[2]
    layouts = sys.argv[3:] or ["py_26", "py_9"]
    if not os.path.isdir(os.path.join(src, "res")):
        print("错误：%s 下没有 res/ 目录，请指向百度皮肤的 skin 目录" % src)
        return 2
    if Image is None:
        print("警告：未安装 Pillow，跳过图片合成，只输出 json 与背景描述文件")
    os.makedirs(dest, exist_ok=True)
    print("从 %s 提取 -> %s" % (src, dest))
    run(src, dest, layouts)
    print("完成。注意：baidu_layout.json 里的 background 是「普通态/按下态」两张图，"
          "写 yaml 时分别填进 normalImage / highlightImage。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
