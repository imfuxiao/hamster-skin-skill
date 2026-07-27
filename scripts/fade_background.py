#!/usr/bin/env python3
"""把背景拼合图的指定小图在顶边 / 底边做 alpha 渐变，直到完全透明。

用于皮肤的「过渡背景」：整片背景图保留原样，但上下两端渐隐到透明，
于是它与 iOS 26 自带的圆角键盘背景之间不再有一条硬边。

用法：

    fade_background.py <resources目录> <图片名> [--top 小图名:像素]... [--bottom 小图名:像素]...

例（青颜：预编辑区顶边渐隐 40px，按键区底边渐隐 32px）：

    fade_background.py skin/light/resources bj --top k1:40 --bottom k3:32

小图名与像素高度都对应 <图片名>.yaml 里的 rect（图片像素，不是点）。
渐变用 smoothstep（3t²-2t³）而不是线性，避免在渐变起点看到一条淡淡的界线。
原图会先备份成 <图片名>.png.orig（已存在则不覆盖，便于反复调参数）。
"""
import os
import shutil
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：python3 -m venv venv && ./venv/bin/pip install Pillow pyyaml")
try:
    import yaml
except ImportError:
    sys.exit("需要 PyYAML：python3 -m venv venv && ./venv/bin/pip install Pillow pyyaml")


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def fade_slice(img, rect, edge, length):
    """在 rect 指定的小图内，从 edge 边起 length 像素做 alpha 渐变到 0。"""
    x, y, w, h = rect
    length = min(int(length), h)
    if length <= 0:
        return 0
    px = img.load()
    for i in range(length):
        # i=0 是最外一行（全透明），i=length-1 最靠内（几乎不变）
        factor = smoothstep((i + 0.5) / length)
        row = y + i if edge == "top" else y + h - 1 - i
        for cx in range(x, x + w):
            r, g, b, a = px[cx, row]
            px[cx, row] = (r, g, b, int(round(a * factor)))
    return length


def parse_specs(args, flag):
    out = []
    i = 0
    while i < len(args):
        if args[i] == flag:
            if i + 1 >= len(args):
                sys.exit(f"{flag} 后面缺少 小图名:像素")
            spec = args[i + 1]
            if ":" not in spec:
                sys.exit(f"{flag} 的参数应写成 小图名:像素，收到 {spec!r}")
            name, _, n = spec.partition(":")
            try:
                out.append((name, int(n)))
            except ValueError:
                sys.exit(f"{flag} 的像素值不是整数：{n!r}")
            i += 2
        else:
            i += 1
    return out


def main(argv):
    positional = [a for a in argv if not a.startswith("--")]
    # 去掉 --top/--bottom 的值
    consumed = set()
    for flag in ("--top", "--bottom"):
        for i, a in enumerate(argv):
            if a == flag and i + 1 < len(argv):
                consumed.add(argv[i + 1])
    positional = [a for a in positional if a not in consumed]
    if len(positional) != 2:
        sys.exit(__doc__)
    res_dir, name = positional

    png = os.path.join(res_dir, name + ".png")
    desc = os.path.join(res_dir, name + ".yaml")
    for f in (png, desc):
        if not os.path.exists(f):
            sys.exit("找不到 " + f)

    slices = yaml.safe_load(open(desc, encoding="utf-8")) or {}

    tops = parse_specs(argv, "--top")
    bottoms = parse_specs(argv, "--bottom")
    if not tops and not bottoms:
        sys.exit("至少要给一个 --top 或 --bottom")

    backup = png + ".orig"
    if not os.path.exists(backup):
        shutil.copy(png, backup)
    img = Image.open(backup).convert("RGBA")

    for edge, specs in (("top", tops), ("bottom", bottoms)):
        for sname, length in specs:
            if sname not in slices:
                sys.exit(f"{name}.yaml 里没有小图 {sname}")
            r = slices[sname].get("rect") or {}
            rect = (int(r.get("x", 0)), int(r.get("y", 0)),
                    int(r.get("width", 0)), int(r.get("height", 0)))
            if rect[2] <= 0 or rect[3] <= 0:
                sys.exit(f"小图 {sname} 的 rect 面积为 0")
            done = fade_slice(img, rect, edge, length)
            pct = 100.0 * done / rect[3]
            print(f"  {name}.{sname} {edge} 渐隐 {done}px（占该小图高度 {pct:.0f}%）")

    img.save(png)
    print(f"已写回 {png}（原图备份在 {os.path.basename(backup)}）")


if __name__ == "__main__":
    main(sys.argv[1:])
