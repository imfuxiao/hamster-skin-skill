#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按元书的布局算法把皮肤画成一张 png，用来在装机之前肉眼检查。

用法:
    python3 preview_skin.py <皮肤目录> [输出目录] [--width 390] [--scale 3]

    对 config.yaml 里声明的每个「键盘类型 x light/dark」各渲三张：
        preview_<light|dark>_<名称>.png            常态
        preview_<light|dark>_<名称>_hint.png       长按符号面板（红框标出格子边界）
        preview_<light|dark>_<名称>_vertical.png   纵向候选栏展开态

校验器只能查出「引用了不存在的样式」这类结构问题，查不出
「键太矮」「某一行没铺满」「跨行键错位」这类几何问题——那些必须看图。
**尤其是转换百度皮肤时，把这张图和原皮肤的 demo.png 并排比一眼。**

能画的：fileImage（拼合图切片）、geometry（圆角、填充、描边、下边缘）、text。
不能画的：systemImage（SF Symbols 不在这里，画成虚线占位框）、
集合视图的实际内容（候选字 / 符号列表只画背景与边框）、动画。

依赖 Pillow 与 PyYAML。
"""
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("需要 PyYAML：pip install pyyaml（或在 venv 里装）")
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("需要 Pillow：pip install Pillow（或在 venv 里装）")

# 按优先级找一个带中日韩字形的字体，否则「空格」「换行」会画成方框
FONTS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
_font_cache = {}
_font_path = None


def _pick_font():
    global _font_path
    if _font_path is not None:
        return _font_path
    for p in FONTS:
        if not os.path.exists(p):
            continue
        try:
            f = ImageFont.truetype(p, 24)
        except OSError:
            continue
        if f.getmask("空").getbbox():      # 真的有中文字形才用
            _font_path = p
            return p
    _font_path = ""
    return ""


def font(size):
    size = max(6, int(round(size)))
    if size not in _font_cache:
        p = _pick_font()
        try:
            _font_cache[size] = ImageFont.truetype(p, size) if p else ImageFont.load_default()
        except OSError:
            _font_cache[size] = ImageFont.load_default()
    return _font_cache[size]


def color(v, default=None):
    """'#RRGGBB' / '#RRGGBBAA'（# 可省）-> (r, g, b, a)。数组取第一个（渐变起点）。"""
    if isinstance(v, list):
        v = v[0] if v else None
    if not isinstance(v, str):
        return default
    s = v.lstrip("#")
    if len(s) not in (6, 8):
        return default
    try:
        c = [int(s[i:i + 2], 16) for i in range(0, len(s), 2)]
    except ValueError:
        return default
    return tuple(c) if len(c) == 4 else tuple(c) + (255,)


def size_of(v, parent):
    """Size -> point。'a/b' 为父容器比例，数值为绝对 point，None = 均分。"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict):
        return size_of(v.get("percentage"), parent)
    s = str(v)
    if "/" in s:
        a, b = s.split("/", 1)
        try:
            return float(a) / float(b) * parent
        except (ValueError, ZeroDivisionError):
            return None
    try:
        return float(s)
    except ValueError:
        return None


def insets_of(d):
    d = d or {}
    return tuple(float(d.get(k, 0) or 0) for k in ("left", "top", "right", "bottom"))


class Renderer:
    def __init__(self, root, resdir, scale):
        self.root = root
        self.resdir = resdir
        self.scale = scale
        self.missing = []
        self.cell_rects = {}
        self.force_pressed = False
        self._sheets, self._descs = {}, {}

    # -- 资源 ------------------------------------------------------------
    def sheet(self, name):
        if name not in self._sheets:
            p = os.path.join(self.resdir, name + ".png")
            self._sheets[name] = Image.open(p).convert("RGBA") if os.path.exists(p) else None
        return self._sheets[name]

    def desc(self, name):
        if name not in self._descs:
            p = os.path.join(self.resdir, name + ".yaml")
            self._descs[name] = (yaml.safe_load(open(p, encoding="utf-8")) or {}) \
                if os.path.exists(p) else {}
        return self._descs[name]

    # -- 绘制 ------------------------------------------------------------
    def px(self, v):
        return int(round(v * self.scale))

    def style(self, canvas, name, rect, pressed=False):
        st = self.root.get(name)
        if not isinstance(st, dict):
            self.missing.append(name)
            return
        vx, vy, vw, vh = rect                       # 可视区域，center 以它为基准
        l, t, r, b = insets_of(st.get("insets"))
        x, y, w, h = vx + l, vy + t, vw - l - r, vh - t - b
        if w <= 0 or h <= 0:
            return
        # center：把图层中心挪到「可视区域宽 x center.x + 可视区域 minX」
        ctr = st.get("center")
        if isinstance(ctr, dict):
            if ctr.get("x") is not None:
                x = vx + vw * float(ctr["x"]) - w / 2.0
            if ctr.get("y") is not None:
                y = vy + vh * float(ctr["y"]) - h / 2.0
        # offset：在此基础上再平移（点）
        off = st.get("offset")
        if isinstance(off, dict):
            x += float(off.get("x") or 0)
            y += float(off.get("y") or 0)
        typ = st.get("buttonStyleType")
        if typ == "fileImage":
            self._file_image(canvas, st, (x, y, w, h), pressed)
        elif typ == "geometry":
            self._geometry(canvas, st, (x, y, w, h), pressed)
        elif typ == "text":
            self._text(canvas, st, (x, y, w, h), pressed)
        elif typ in ("systemImage", "assetImage"):
            self._placeholder(canvas, st, (x, y, w, h))

    def _file_image(self, canvas, st, rect, pressed=False):
        # 元书是 styleNode[isActive ? "highlightImage" : "normalImage"]，
        # 按下态**不会**回退到 normalImage——只写 normalImage 的图层按下时是空的
        ni = (st.get("highlightImage") if pressed else st.get("normalImage")) or {}
        f, i = ni.get("file"), ni.get("image")
        if not f or not i:
            return
        sheet = self.sheet(f)
        d = (self.desc(f) or {}).get(i)
        if sheet is None or not d or not d.get("rect"):
            self.missing.append("图片 %s/%s" % (f, i))
            return
        rc = d["rect"]
        if not rc.get("width") or not rc.get("height"):
            return
        im = sheet.crop((rc["x"], rc["y"], rc["x"] + rc["width"], rc["y"] + rc["height"]))
        x, y, w, h = rect
        tw, th = max(1, self.px(w)), max(1, self.px(h))
        mode = st.get("contentMode") or "scaleToFill"     # fileImage 的默认值
        ins = d.get("insets")
        ox = oy = 0
        if ins and mode == "scaleToFill":
            im = self._nine_patch(im, tw, th, ins)
        elif mode == "scaleAspectFit":
            s = min(tw / float(im.width), th / float(im.height))
            nw, nh = max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))
            im = im.resize((nw, nh), Image.LANCZOS)
            ox, oy = (tw - nw) // 2, (th - nh) // 2
        elif mode == "scaleAspectFill":
            s = max(tw / float(im.width), th / float(im.height))
            nw, nh = max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))
            im = im.resize((nw, nh), Image.LANCZOS)
            cx, cy = (nw - tw) // 2, (nh - th) // 2
            im = im.crop((cx, cy, cx + tw, cy + th))
        elif mode == "center":
            # 原始像素尺寸居中；超出可视区就裁掉（真机按点算，这里按像素近似）
            cx, cy = max(0, (im.width - tw) // 2), max(0, (im.height - th) // 2)
            im = im.crop((cx, cy, cx + min(tw, im.width), cy + min(th, im.height)))
            ox, oy = (tw - im.width) // 2, (th - im.height) // 2
        else:
            im = im.resize((tw, th), Image.LANCZOS)
        canvas.alpha_composite(im, (self.px(x) + ox, self.px(y) + oy))

    def _nine_patch(self, im, tw, th, ins):
        """按 insets 做九宫格拉伸：四角不缩放，四边单向拉伸，中间双向拉伸。

        insets 是**图片像素**，目标尺寸是**渲染像素**（= 点 x scale），
        所以角要先乘 scale 再用；角之和超过目标尺寸时按比例缩小——
        这也是真机上「保护区比按键还大」时会糊掉的原因，这里如实反映出来。
        """
        s = self.scale
        l = int(float(ins.get("left", 0) or 0) * s)
        t = int(float(ins.get("top", 0) or 0) * s)
        r = int(float(ins.get("right", 0) or 0) * s)
        b = int(float(ins.get("bottom", 0) or 0) * s)
        if l + r >= tw:                            # 角太大，按比例压缩
            k = (tw - 1) / float(l + r)
            l, r = int(l * k), int(r * k)
        if t + b >= th:
            k = (th - 1) / float(t + b)
            t, b = int(t * k), int(b * k)
        sl = int(float(ins.get("left", 0) or 0))
        st_ = int(float(ins.get("top", 0) or 0))
        sr = int(float(ins.get("right", 0) or 0))
        sb = int(float(ins.get("bottom", 0) or 0))
        iw, ih = im.size
        if sl + sr >= iw or st_ + sb >= ih:
            return im.resize((tw, th), Image.LANCZOS)
        xs = [(0, sl, 0, l), (sl, iw - sr, l, tw - r), (iw - sr, iw, tw - r, tw)]
        ys = [(0, st_, 0, t), (st_, ih - sb, t, th - b), (ih - sb, ih, th - b, th)]
        out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        for x0, x1, dx0, dx1 in xs:
            for y0, y1, dy0, dy1 in ys:
                if x1 <= x0 or y1 <= y0 or dx1 <= dx0 or dy1 <= dy0:
                    continue
                part = im.crop((x0, y0, x1, y1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
                out.paste(part, (dx0, dy0))
        return out

    def _geometry(self, canvas, st, rect, pressed=False):
        k = (lambda a, b: st.get(a) if pressed and st.get(a) else st.get(b))
        x, y, w, h = rect
        box = [self.px(x), self.px(y), self.px(x + w) - 1, self.px(y + h) - 1]
        if box[2] <= box[0] or box[3] <= box[1]:
            return
        radius = self.px(float(st.get("cornerRadius") or 0))
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(layer)
        edge = color(k("highlightLowerEdgeColor", "normalLowerEdgeColor"))
        if edge:                                   # 键帽底部的立体边缘
            dr.rounded_rectangle([box[0], box[1] + self.px(1), box[2], box[3] + self.px(1)],
                                 radius=radius, fill=edge)
        fill = color(k("highlightColor", "normalColor"))
        border = color(k("highlightBorderColor", "normalBorderColor"))
        bw = self.px(float(st.get("borderSize") or 0)) if border else 0
        if fill or border:
            dr.rounded_rectangle(box, radius=radius, fill=fill,
                                 outline=border, width=max(bw, 1) if border else 0)
        canvas.alpha_composite(layer)

    def _text(self, canvas, st, rect, pressed=False):
        txt = st.get("text")
        if txt is None:
            txt = "◻"                              # 集合视图的单元格文字来自数据源
        txt = str(txt)
        if txt.startswith("$"):
            txt = {"$rimeSchemaName": "拼音", "$returnKeyType": "换行"}.get(txt, txt)
        fs = st.get("fontSize", 16)
        if isinstance(fs, str) and fs.endswith("em"):
            fs = float(fs[:-2]) * 16
        x, y, w, h = rect
        dr = ImageDraw.Draw(canvas)
        f = font(float(fs) * self.scale)
        bb = dr.textbbox((0, 0), txt, font=f)
        dr.text((self.px(x + w / 2) - (bb[2] - bb[0]) / 2 - bb[0],
                 self.px(y + h / 2) - (bb[3] - bb[1]) / 2 - bb[1]),
                txt, font=f,
                fill=color((st.get("highlightColor") if pressed else None)
                           or st.get("normalColor"), (0, 0, 0, 255)))

    def _placeholder(self, canvas, st, rect):
        """SF Symbols / App 内置图片渲不出来，画个虚线框标出位置。"""
        x, y, w, h = rect
        name = str(st.get("systemImageName") or st.get("assetImageName") or "?")
        c = color(st.get("normalColor"), (128, 128, 128, 255))
        dr = ImageDraw.Draw(canvas)
        s = min(w, h) * 0.6
        box = [self.px(x + (w - s) / 2), self.px(y + (h - s) / 2),
               self.px(x + (w + s) / 2), self.px(y + (h + s) / 2)]
        step = max(self.px(2), 2)
        for i in range(box[0], box[2], step):
            end = min(i + step // 2, box[2])
            dr.line([i, box[1], end, box[1]], fill=c)
            dr.line([i, box[3], end, box[3]], fill=c)
        dr.text((box[0], box[1]), name[:10], font=font(6 * self.scale), fill=c)

    # -- 布局 ------------------------------------------------------------
    def cell(self, canvas, name, rect, pressed=False):
        st = self.root.get(name)
        if not isinstance(st, dict):
            self.missing.append(name)
            return
        self.cell_rects.setdefault(name, rect)
        pressed = pressed or self.force_pressed
        x, y, w, h = rect
        bd = st.get("bounds")
        if bd:
            bw = size_of(bd.get("width"), w) or w
            bh = size_of(bd.get("height"), h) or h
            al = str(bd.get("alignment", "center")).lower()
            bx = x if "left" in al else (x + w - bw if "right" in al else x + (w - bw) / 2)
            by = y if "top" in al else (y + h - bh if "bottom" in al else y + (h - bh) / 2)
            x, y, w, h = bx, by, bw, bh
        bg = st.get("backgroundStyle")
        if isinstance(bg, list) and bg:           # 条件样式：预览取第一条
            bg = (bg[0] or {}).get("styleName")
            bg = bg[0] if isinstance(bg, list) else bg
        if isinstance(bg, str):
            self.style(canvas, bg, (x, y, w, h), pressed)
        fg = st.get("foregroundStyle")
        if isinstance(fg, list) and fg and isinstance(fg[0], dict):
            fg = (fg[0] or {}).get("styleName")
        if isinstance(fg, str):
            fg = [fg]
        for n in fg or []:
            if isinstance(n, str):
                self.style(canvas, n, (x, y, w, h), pressed)
        # 集合视图：把 cellStyle 画一格出来，提示这里是个列表
        if st.get("type") in ("symbols", "t9Symbols", "numericSymbols",
                              "categorySymbols", "horizontalSymbols") and st.get("cellStyle"):
            rows = int(st.get("maximumRow") or 4)
            l, t, r, b = insets_of(st.get("insets"))
            ch = (h - t - b) / max(rows, 1)
            for i in range(rows):
                self.cell(canvas, st["cellStyle"], (x + l, y + t + i * ch, w - l - r, ch))

    def layout(self, canvas, nodes, rect, vertical):
        """vertical=True: 子节点自上而下分高度（同级 HStack，或 VStack 里的 Cell）。"""
        if not isinstance(nodes, list) or not nodes:
            return
        x, y, w, h = rect
        total = h if vertical else w
        sizes = []
        for n in nodes:
            if not isinstance(n, dict):
                sizes.append(None)
                continue
            if "Cell" in n:
                st = self.root.get(n["Cell"]) or {}
            else:
                key = "HStack" if "HStack" in n else "VStack"
                sty = (n.get(key) or {}).get("style")
                st = (self.root.get(sty) or {}) if sty else {}
            sz = st.get("size") or {}
            sizes.append(size_of(sz.get("height") if vertical else sz.get("width"), total))
        fixed = sum(s for s in sizes if s is not None)
        auto_n = sum(1 for s in sizes if s is None)
        auto = (total - fixed) / auto_n if auto_n else 0
        sizes = [auto if s is None else s for s in sizes]

        pos = y if vertical else x
        for n, s in zip(nodes, sizes):
            r = (x, pos, w, s) if vertical else (pos, y, s, h)
            if "Cell" in n:
                self.cell(canvas, n["Cell"], r)
            elif "HStack" in n:
                self.layout(canvas, (n["HStack"] or {}).get("subviews"), r, False)
            elif "VStack" in n:
                self.layout(canvas, (n["VStack"] or {}).get("subviews"), r, True)
            pos += s

    def hint_grid(self, canvas, grid_name, key_rect):
        """长按符号网格：面板 + 每格的背景 / 高亮 / 文字。

        主要用来检查「高亮块是不是比格子小一圈」——顶满格子就看不出选中哪个了。
        """
        gs = self.root.get(grid_name)
        if not isinstance(gs, dict):
            self.missing.append(grid_name)
            return
        rows = [r for r in (gs.get("symbolRows") or []) if r]
        if not rows:
            return
        kx, ky, kw, kh = key_rect
        sz = gs.get("size") or {}
        cw = size_of(sz.get("width"), kw) or kw
        ch = size_of(sz.get("height"), kh) or kh
        sp = gs.get("spacing") or {}
        hs, vs = float(sp.get("horizontal", 0) or 0), float(sp.get("vertical", 0) or 0)
        l, t, r, b = insets_of(gs.get("insets"))
        cols = max(len(x) for x in rows)
        pw = cols * cw + (cols - 1) * hs + l + r
        ph = len(rows) * ch + (len(rows) - 1) * vs + t + b
        off = gs.get("offset") or {}
        px = kx + (kw - pw) / 2 + float(off.get("x", 0) or 0)
        py = ky - ph + float(off.get("y", 0) or 0)
        anchor = gs.get("anchor") or {}
        if "row" in anchor and "col" in anchor:      # 锚点格中心对准按键中心
            ax = l + anchor["col"] * (cw + hs) + cw / 2
            ay = t + anchor["row"] * (ch + vs) + ch / 2
            px = kx + kw / 2 - ax + float(off.get("x", 0) or 0)
            py = ky + kh / 2 - ay + float(off.get("y", 0) or 0)

        if gs.get("backgroundStyle"):
            self.style(canvas, gs["backgroundStyle"], (px, py, pw, ph))
        sel = gs.get("selected") or {"row": 0, "col": 0}   # 预览里默认高亮第一格
        for ri, row in enumerate(rows):
            for ci, cn in enumerate(row):
                if not cn:
                    continue
                cr = (px + l + ci * (cw + hs), py + t + ri * (ch + vs), cw, ch)
                on = ri == sel.get("row") and ci == sel.get("col")
                if on and gs.get("selectedBackgroundStyle"):
                    self.style(canvas, gs["selectedBackgroundStyle"], cr)
                self.cell(canvas, cn, cr, pressed=on)
        # 用细框标出格子边界，方便对比高亮块有没有小一圈
        dr = ImageDraw.Draw(canvas)
        for ri in range(len(rows)):
            for ci in range(cols):
                cr = (px + l + ci * (cw + hs), py + t + ri * (ch + vs), cw, ch)
                dr.rectangle([self.px(cr[0]), self.px(cr[1]),
                              self.px(cr[0] + cr[2]) - 1, self.px(cr[1] + cr[3]) - 1],
                             outline=(255, 0, 0, 90))

    def region(self, canvas, node, rect):
        if not isinstance(node, dict):
            return rect
        bg = node.get("backgroundStyle")
        if isinstance(bg, str):
            self.style(canvas, bg, rect)
        l, t, r, b = insets_of(node.get("insets"))
        return (rect[0] + l, rect[1] + t, rect[2] - l - r, rect[3] - t - b)


def render(path, out_prefix, width, scale):
    """渲三张：常态、长按符号面板、纵向候选栏展开态。"""
    root = yaml.safe_load(open(path, encoding="utf-8"))
    if not isinstance(root, dict):
        print("  跳过（不是映射）:", path)
        return
    resdir = os.path.join(os.path.dirname(path), "resources")
    ph = float(root.get("preeditHeight") or 0)
    th = float(root.get("toolbarHeight") or 0)
    kh = float(root.get("keyboardHeight") or 0)
    total = ph + th + kh

    def new_canvas():
        return Image.new("RGBA", (int(width * scale), int(total * scale)), (255, 255, 255, 255))

    def base(r, canvas):
        inner = r.region(canvas, root.get("preeditStyle"), (0, 0, width, ph))
        if root.get("preeditStyle"):
            ImageDraw.Draw(canvas).text(
                (r.px(inner[0]), r.px(inner[1])), "pi'yin",
                font=font(14 * scale), fill=(120, 120, 120, 255))
        inner = r.region(canvas, root.get("toolbarStyle"), (0, ph, width, th))
        r.layout(canvas, root.get("toolbarLayout"), inner, True)
        inner = r.region(canvas, root.get("keyboardStyle"), (0, ph + th, width, kh))
        nodes = root.get("keyboardLayout") or []
        r.layout(canvas, nodes, inner,
                 bool(nodes) and isinstance(nodes[0], dict) and "HStack" in nodes[0])

    def save(r, canvas, suffix):
        out = "%s%s.png" % (out_prefix, suffix)
        canvas.convert("RGB").save(out)
        note = ""
        if r.missing:
            uniq = sorted(set(r.missing))
            note = "  ！缺 %d 项: %s" % (len(uniq), ", ".join(uniq[:5]))
        print("  %s  (%.0f x %.0f pt)%s" % (out, width, total, note))

    # 1) 常态
    r = Renderer(root, resdir, scale)
    canvas = new_canvas()
    base(r, canvas)
    save(r, canvas, "")

    # 2) 长按符号面板（取第一个带 hintSymbolsGridStyle 的键）
    target = next(((n, st["hintSymbolsGridStyle"]) for n, st in root.items()
                   if isinstance(st, dict) and st.get("hintSymbolsGridStyle")
                   and n in r.cell_rects), None)
    if target:
        r2 = Renderer(root, resdir, scale)
        canvas = new_canvas()
        base(r2, canvas)
        r2.hint_grid(canvas, target[1], r2.cell_rects[target[0]])
        save(r2, canvas, "_hint")

    # 3) 全部按键的按下态：检查 highlightImage / 按下才出现的图层对不对
    rp = Renderer(root, resdir, scale)
    rp.force_pressed = True
    canvas = new_canvas()
    base(rp, canvas)
    save(rp, canvas, "_pressed")

    # 4) 纵向候选栏展开态：盖住预编辑区以下的全部区域
    if root.get("verticalCandidatesLayout"):
        r3 = Renderer(root, resdir, scale)
        canvas = new_canvas()
        base(r3, canvas)
        inner = r3.region(canvas, root.get("verticalCandidatesStyle"),
                          (0, ph, width, th + kh))
        nodes = root["verticalCandidatesLayout"]
        r3.layout(canvas, nodes, inner,
                  bool(nodes) and isinstance(nodes[0], dict) and "HStack" in nodes[0])
        save(r3, canvas, "_vertical")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(zip([a.lstrip("-") for a in sys.argv[1:] if a.startswith("--")],
                    [sys.argv[i + 1] for i, a in enumerate(sys.argv[1:], 1)
                     if a.startswith("--")]))
    if not args:
        print(__doc__)
        return 2
    skin = os.path.abspath(args[0])
    out = os.path.abspath(args[1]) if len(args) > 1 else skin
    width = float(opts.get("width", 390))
    scale = int(opts.get("scale", 3))

    cfg_path = os.path.join(skin, "config.yaml")
    if not os.path.exists(cfg_path):
        print("错误：%s 下没有 config.yaml" % skin)
        return 2
    cfg = yaml.safe_load(open(cfg_path, encoding="utf-8")) or {}
    names = []
    for kb, v in cfg.items():
        if not isinstance(v, dict):
            continue
        for dev in ("iPhone", "iPad"):
            for orient, f in (v.get(dev) or {}).items():
                if isinstance(f, str) and f not in names:
                    names.append(f)
    if not names:
        print("错误：config.yaml 里没有找到任何键盘配置文件名")
        return 2

    os.makedirs(out, exist_ok=True)
    print("预览 %s（宽 %gpt，%dx）" % (skin, width, scale))
    for side in ("light", "dark"):
        for n in names:
            p = os.path.join(skin, side, n + ".yaml")
            if os.path.exists(p):
                render(p, os.path.join(out, "preview_%s_%s" % (side, n)), width, scale)
    print("把图和原皮肤的 demo.png 并排看一眼：行高、留白、跨行键的位置对不对。")
    print("_hint 是长按面板（红框标出格子边界，高亮块应当比红框小一圈），"
          "_vertical 是候选栏展开态。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
