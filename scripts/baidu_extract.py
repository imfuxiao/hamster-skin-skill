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
    * anim_<拼合图>_<序号>.png —— 「按下才冒出来、而且会位移」的那些前景层，
      它们不能烘进静态贴图，要交给元书的 physics 动画

产出（写进 <元书皮肤目录>/）:
    * baidu_layout.json —— 每个键的结构化信息（矩形、背景图、动作、长按符号、动画…）
      以及 metrics（换算好的行高 / keyboardHeight），写键盘 yaml 时照着它填即可

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

# iPhone 竖屏逻辑宽度，用于把设计稿单位换算成点
SCREEN_W = 390.0


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


def csv(s):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


class Skin:
    def __init__(self, root):
        self.root = root
        self.res = os.path.join(root, "res")
        self.port = os.path.join(root, "port")
        if not os.path.isdir(self.port):          # 有些皮肤布局文件直接放在 skin/ 下
            self.port = root
        self.css = parse_ini(os.path.join(self.res, "default.css"))
        self.gen = parse_ini(os.path.join(self.port, "gen.ini"))
        anim_path = os.path.join(self.res, "anim.ini")
        self.anim = parse_ini(anim_path) if os.path.exists(anim_path) else {}
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

    def press_only(self, sid):
        """只有 HL_IMG 的样式 = 按下才出现的图层。"""
        s = self.css.get("STYLE%s" % sid, {})
        return bool(s.get("HL_IMG")) and not s.get("NM_IMG")

    def sound(self, sid):
        return (self.css.get("STYLE%s" % sid, {}) or {}).get("PRESS_SOUND_PATH")

    # -- 动画 ------------------------------------------------------------
    def style_anim(self, sid):
        """STYLE 号 -> 归一化后的动画描述，没有则 None。

        [STYLE*] PRESS_ANIM=<n> -> [ANIM<n>]；[ANIM*] 可能是 BUILD 组合。
        归一化结果:
            { duration, scale: <TO/100 或 None>, translate: [dx, dy] 或 None, remove }
        """
        n = (self.css.get("STYLE%s" % sid, {}) or {}).get("PRESS_ANIM")
        return self.resolve_anim(n) if n else None

    def resolve_anim(self, n, _depth=0):
        sec = self.anim.get("ANIM%s" % n)
        if not sec or _depth > 3:
            return None
        if sec.get("BUILD_LIST"):                 # 组合动画：合并各分量
            out = {"duration": 0, "scale": None, "translate": None, "remove": False}
            for sub in csv(sec["BUILD_LIST"]):
                part = self.resolve_anim(sub, _depth + 1)
                if not part:
                    continue
                out["duration"] = max(out["duration"], part["duration"])
                out["scale"] = part["scale"] if part["scale"] is not None else out["scale"]
                out["translate"] = part["translate"] or out["translate"]
                out["remove"] = out["remove"] or part["remove"]
            return out if (out["scale"] or out["translate"]) else None
        typ = sec.get("TYPE")
        to = ints(sec.get("TO", ""))
        if len(to) < 2:
            return None
        out = {"duration": int(float(sec.get("DURATION", 0) or 0)),
               "scale": None, "translate": None,
               "remove": sec.get("REMOVE") == "1"}
        if typ == "4":                            # 缩放，FROM/TO 是百分比
            out["scale"] = round(to[0] / 100.0, 3)
        elif typ == "2":                          # 位移，FROM/TO 是设计单位
            frm = ints(sec.get("FROM", "")) or [0, 0]
            out["translate"] = [to[0] - frm[0], to[1] - frm[1]]
        else:
            return None
        return out

    def offset(self, n):
        pos = self.gen.get("OFFSET%s" % n, {}).get("POS")
        return tuple(ints(pos)) if pos else (0, 0)

    def panel_size(self, layout):
        for src in (layout, self.gen):
            v = (src.get("PANEL") or {}).get("SIZE")
            if v:
                return ints(v)
        return [1125, 595]


def splash_layers(skin, sec):
    """挑出「按下才出现、而且带位移动画」的前景层——交给 physics，不要烘进静态贴图。

    返回 {前景层下标: {styleId, image:(拼合图,序号), offset:(dx,dy), anim:{...}}}。
    只有 HL_IMG 但没有位移动画的层（纯角标 / 水印）不算，照旧烘进 fg_*ax。
    """
    fore = csv(sec.get("FORE_STYLE", ""))
    pos = csv(sec.get("POS_TYPE", ""))
    anim = csv(sec.get("FORE_ANIM_STYLE", ""))
    out = {}
    for i, sid in enumerate(fore):
        if not skin.press_only(sid):
            continue
        a = skin.style_anim(anim[i]) if i < len(anim) else None
        if not a or not a.get("translate"):
            continue
        ref = skin.style_img(sid, True)
        if not ref or ref[1] not in skin.til(ref[0]):
            continue
        out[i] = {"styleId": sid, "image": ref,
                  "offset": skin.offset(pos[i]) if i < len(pos) else (0, 0),
                  "anim": a}
    return out


def splash_layer(skin, fname, idx, rect, offset, out):
    """把「按下才冒出来」的那一层单独画到与按键等大的画布上。

    元书的 transform 动画只能作用于按键**已有的图层**，而 fileImage 图层总是铺满
    可视区——所以要给这一层单独出一张与按键等大的贴图，元素按 [OFFSET*] 摆在里面。
    这样就能用 `transform` 同时做位移和缩放（physics 没有缩放曲线）。

    返回补进 json 的字段：
        layerImage  贴图文件名，作为该层的 highlightImage（没有 normalImage，常态不显示）
        anchorPoint 元素中心在画布中的单位坐标，对应百度缩放动画的锚点
        layerShift  为了不裁掉元素而整体下移的量（设计单位），动画起点要减掉它
    """
    if Image is None or len(rect) != 4:
        return {}
    tile = skin.til(fname).get(idx)
    if not tile:
        return {}
    kw, kh = rect[2], rect[3]
    tw, th = tile[2], tile[3]
    px = (kw - tw) // 2 + offset[0]
    py = (kh - th) // 2 + offset[1]

    # 画布只有按键那么大，元素超出上下边会被裁掉。整体挪一挪补回来，
    # 动画起点再把这段位移减掉，视觉位置与原皮肤一致。
    bbox = skin.tile(fname, idx).split()[3].getbbox() or (0, 0, tw, th)
    shift = max(0, -(py + bbox[1])) - max(0, (py + bbox[3]) - kh)
    py += shift

    key = (fname, idx, kw, kh, px, py)
    if key not in out:
        src = skin.tile(fname, idx)
        # alpha_composite 不接受负坐标，越界的部分先从源图裁掉
        src = src.crop((max(0, -px), max(0, -py), src.width, src.height))
        canvas = Image.new("RGBA", (kw, kh), (0, 0, 0, 0))
        canvas.alpha_composite(src, (max(px, 0), max(py, 0)))
        out[key] = ("splash_%s_%d_%dx%d.png" % (fname, idx, kw, kh), canvas)
    return {
        "layerImage": out[key][0],
        "anchorPoint": [round((px + tw / 2.0) / kw, 4), round((py + th / 2.0) / kh, 4)],
        "layerShift": shift,
    }


# --------------------------------------------------------------------------- 前景合成

def compose(skin, sec, pressed, skip=()):
    """把一个 [KEY*]/[TIP*] 的全部 FORE_STYLE 层合成到与 VIEW_RECT 等大的透明画布上。

    skip: 要跳过的前景层下标集合（交给 physics 动画的那些）。
    """
    rect = ints(sec.get("VIEW_RECT", ""))
    if len(rect) != 4:
        return None
    w, h = rect[2], rect[3]
    canvas = Image.new("RGBA", (max(w, 1), max(h, 1)), (0, 0, 0, 0))
    fore = csv(sec.get("FORE_STYLE", ""))
    pos = csv(sec.get("POS_TYPE", ""))
    drew = False
    for i, sid in enumerate(fore):
        if i in skip:
            continue
        ref = skin.style_img(sid, pressed)
        if not ref:
            continue                              # 空样式 / 该状态不画
        fname, idx = ref
        if idx not in skin.til(fname):
            continue
        layer = skin.tile(fname, idx)
        ox, oy = skin.offset(pos[i]) if i < len(pos) else (0, 0)
        # [实测] POS 是「小图中心对准按键中心后再平移」，不是文档写的左上角对齐
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


# --------------------------------------------------------------------------- 尺寸换算

def metrics(skin, keys, panel):
    """反推元书的行高与 keyboardHeight。

    [PANEL] SIZE 只是设计稿坐标系，**不是宽高比**，照它算键盘会明显偏矮。
    正确做法是拿「键帽切片的原始宽高比」反推行高：切片通常比 VIEW_RECT 更高瘦，
    说明百度渲染时把面板拉得比设计稿高。详见 references/baidu-skin.md 第 8 节。
    """
    pw, ph = panel
    unit_x = SCREEN_W / pw

    # 取占比最多的那种 VIEW_RECT 尺寸当「普通字母键」，排除铺满面板的背景键
    sizes = {}
    rows = set()
    for k in keys.values():
        r = k.get("viewRect") or []
        if len(r) != 4 or (r[2] >= pw * 0.9 and r[3] >= ph * 0.9):
            continue
        rows.add(r[1])
        sizes.setdefault((r[2], r[3]), []).append(k)
    if not sizes:
        return None
    (kw, kh), sample = max(sizes.items(), key=lambda kv: len(kv[1]))

    tile = None
    for k in sample:
        bgref = k.get("_backRef")
        if bgref and bgref[1] in skin.til(bgref[0]):
            tile = skin.til(bgref[0])[bgref[1]]
            break

    key_w_pt = kw * unit_x
    if tile and tile[2] > 0:
        row_h = key_w_pt * tile[3] / float(tile[2])   # 按切片比例反推
        basis = "键帽切片 %dx%d / VIEW_RECT %dx%d" % (tile[2], tile[3], kw, kh)
    else:                                             # 找不到切片时退回设计稿比例
        row_h = kh * unit_x
        basis = "找不到键帽切片，退回设计稿等比（可能偏矮，务必用 preview_skin.py 核对）"
    unit_y = row_h / float(kh)

    top = min(rows) if rows else 0
    bottom = ph - max(r[1] + r[3] for r in
                      (k["viewRect"] for k in keys.values()
                       if len(k.get("viewRect") or []) == 4
                       and not (k["viewRect"][2] >= pw * 0.9 and k["viewRect"][3] >= ph * 0.9)))
    return {
        "screenWidth": SCREEN_W,
        "unitX": round(unit_x, 5),
        "unitY": round(unit_y, 5),
        "rowCount": len(rows),
        "rowHeight": round(row_h, 2),
        "keyWidth": round(key_w_pt, 2),
        "insetTop": round(top * unit_y, 1),
        "insetBottom": round(bottom * unit_y, 1),
        "keyboardHeight": round(len(rows) * row_h + (top + bottom) * unit_y),
        "basis": basis,
    }


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
    splash_out = {}          # (拼合图, 序号) -> physics 用的原始切片文件名
    layer_out = {}           # (切片, 按键尺寸, 位置) -> (文件名, 与按键等大的整层贴图)
    sounds = set()
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

        keys, skips = {}, {}
        for sec_name, sec in layout.items():
            if not re.match(r"^(KEY|TIP)\d+$", sec_name):
                continue
            rect = ints(sec.get("VIEW_RECT", ""))
            bid = sec.get("BACK_STYLE")
            back = skin.style_img(bid) if bid else None
            back_hl = skin.style_img(bid, True) if bid else None
            if back:
                used_sheets.add(back[0])
            if back_hl:
                used_sheets.add(back_hl[0])

            # 按下时的缩放动画（背景层）
            press = skin.style_anim(sec.get("BACK_ANIM_STYLE")) if sec.get("BACK_ANIM_STYLE") else None
            # 按下时冒出来并位移的图层
            sp = splash_layers(skin, sec) if skin.anim else {}
            skips[sec_name] = set(sp)
            splash = []
            for info in sp.values():
                fname, idx = info["image"]
                fn = "anim_%s_%d.png" % (fname, idx)
                splash_out[(fname, idx)] = fn
                entry = {
                    "image": fn,
                    "tileSize": skin.til(fname).get(idx, [0, 0, 0, 0])[2:],
                    # 贴图中心相对按键中心的偏移（设计单位，负 = 上）
                    "centerOffset": list(info["offset"]),
                    "translate": info["anim"]["translate"],
                    "duration": info["anim"]["duration"],
                    "scaleTo": info["anim"]["scale"],
                }
                entry.update(splash_layer(skin, fname, idx, rect, info["offset"], layer_out))
                splash.append(entry)

            snd = skin.sound(sec.get("SOUND_STYLE")) if sec.get("SOUND_STYLE") else None
            if snd:
                sounds.add(snd)

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
                "pressAnimation": press,
                "splashAnimations": splash or None,
                "sound": snd,
                "_backRef": list(back) if back else None,
            }
            if sec_name in tip_owner:
                owner, state = tip_owner[sec_name]
                keys[sec_name]["tipOf"] = {"key": owner, "state": state}

        summary[lname] = {
            "panelSize": [pw, ph],
            "metrics": metrics(skin, keys, [pw, ph]),
            "keys": keys,
            "list": layout.get("LIST"),
            "hint": layout.get("HINT"),
        }
        for k in keys.values():
            k.pop("_backRef", None)

        if Image is None:
            continue
        for pressed, suffix in ((False, ""), (True, "ax")):
            tiles = {}
            for sec_name, sec in layout.items():
                if re.match(r"^(KEY|TIP)\d+$", sec_name):
                    im = compose(skin, sec, pressed, skips.get(sec_name, ()))
                    if im is not None:
                        tiles[sec_name] = im
            if not tiles:
                continue
            sheet, rects = pack(tiles)
            sheet.save(os.path.join(resdir, "fg_%s%s.png" % (lname, suffix)))
            open(os.path.join(resdir, "fg_%s%s.yaml" % (lname, suffix)),
                 "w", encoding="utf-8").write(rect_yaml(rects))
            print("  写出 fg_%s%s（%d 块）" % (lname, suffix, len(tiles)))

        m = summary[lname]["metrics"]
        if m:
            print("  %s 尺寸：行高 %.1fpt x %d 行 -> keyboardHeight %d（%s）"
                  % (lname, m["rowHeight"], m["rowCount"], m["keyboardHeight"], m["basis"]))

    # 「按下才冒出来」那一层的两种用法：physics 用原始切片，transform 用整层贴图
    if Image is not None:
        for (fname, idx), out in sorted(splash_out.items()):
            skin.tile(fname, idx).save(os.path.join(resdir, out))
            print("  physics 用图 %s（来自 %s 第 %d 张）" % (out, fname, idx))
        for name, canvas in sorted(layer_out.values()):
            canvas.save(os.path.join(resdir, name))
            # fileImage 要配一个图片描述文件才能引用；整张图就是一块，固定叫 k1
            stem = os.path.splitext(name)[0]
            open(os.path.join(resdir, stem + ".yaml"), "w", encoding="utf-8").write(
                rect_yaml({"k1": (0, 0, canvas.width, canvas.height)}))
            print("  transform 用整层贴图 %s（引用为 { file: %s, image: k1 }）" % (name, stem))

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

    if sounds:
        print("  按键音（自行从 res/ 复制到皮肤的 sound/）:", " ".join(sorted(sounds)))

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
    print("完成。要点：")
    print("  * background / backgroundPressed 分别填进 normalImage / highlightImage")
    print("  * keyboardHeight 用 metrics 里的值，别拿 panelSize 的高宽比去算")
    print("  * splashAnimations 要写成 physics 动画，它已经从 fg_*ax 里剔除了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
