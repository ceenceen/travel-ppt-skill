# -*- coding: utf-8 -*-
"""为每天的行程页生成'地图路线'配图（写入 <datadir>/ppt_assets/routes/dayNN.png）。
- 普通日：用数据模块里该天的 intro 景点名，生成深色电影风'当日路线'示意图（编号圆点+地名）。
- 真实地图日：用 --real-day N --real-map <图片路径> 指定某天用真实地图（如用户提供的手绘/截图路线）。

用法：
  python make_routes.py <数据模块.py> [--out DIR] [--real-day 12 --real-map tianjin.png] [--font C:/Windows/Fonts/msyh.ttc]
"""
import os, sys, math, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw, ImageFont

W, H = 980, 500
NAVY1 = (13, 24, 40)
GRID  = (28, 46, 70)
LINE  = (110, 180, 214)
PIN   = (226, 150, 92)
PINR  = (245, 238, 225)
TXT   = (233, 240, 248)
SUB   = (150, 170, 190)
DEFAULT_FONT = r"C:\Windows\Fonts\msyh.ttc"

def font(sz, path):
    return ImageFont.truetype(path, sz)

def num_label(i):
    if 1 <= i <= 20:
        return chr(0x2460 + i - 1)
    return str(i)

def gen_schematic(day_no, names, fpath):
    names = [n.strip() for n in names if n.strip() and n != "—"]
    if not names:
        names = ["出发", "抵达"]
    names = (names + ["", ""])[:8]
    n = max(2, len(names))
    names = (names + ["", ""])[:n]
    img = Image.new("RGB", (W, H), NAVY1)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 49):
        d.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, 50):
        d.line([(0, y), (W, y)], fill=GRID, width=1)
    d.text((30, 22), "当日路线 · Day %s" % day_no, font=font(27, fpath), fill=TXT)
    d.text((30, 60), "ROUTE OF THE DAY", font=font(13, fpath), fill=SUB)
    margin_l, margin_r = 78, 78
    y0 = int(H * 0.56)
    span = W - margin_l - margin_r
    pts = [(margin_l + (span * i / (n - 1)), y0) for i in range(n)]
    d.line(pts, fill=(LINE[0]//2, LINE[1]//2, LINE[2]//2), width=14, joint="curve")
    d.line(pts, fill=LINE, width=5, joint="curve")
    for i, (x, y) in enumerate(pts):
        r = 19
        d.ellipse([x-r, y-r, x+r, y+r], fill=PIN, outline=(255,255,255), width=2)
        d.text((x, y), num_label(i+1), font=font(20, fpath), fill=PINR, anchor="mm")
        label = names[i]
        if len(label) > 7:
            label = label[:6] + "…"
        if i % 2 == 0:
            d.text((x, y + 30), label, font=font(16, fpath), fill=TXT, anchor="mm")
        else:
            d.text((x, y - 46), label, font=font(16, fpath), fill=TXT, anchor="mm")
    return img

def place_real(day_no, src_path, fpath):
    img = Image.new("RGB", (W, H), NAVY1)
    d = ImageDraw.Draw(img)
    d.text((30, 22), "当日路线 · Day %s" % day_no, font=font(27, fpath), fill=TXT)
    d.text((30, 60), "实际地图 · REAL MAP", font=font(14, fpath), fill=SUB)
    src = Image.open(src_path).convert("RGB")
    sw, sh = src.size
    scale = min((W - 60) / sw, (H - 90) / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    src = src.resize((nw, nh), Image.LANCZOS)
    x = (W - nw) // 2
    y = (H - nh) // 2 + 25
    img.paste(src, (x, y))
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--out", default=None)
    ap.add_argument("--real-day", type=int, default=None)
    ap.add_argument("--real-map", default=None)
    ap.add_argument("--font", default=DEFAULT_FONT)
    a = ap.parse_args()

    import importlib.util
    spec = importlib.util.spec_from_file_location("td", os.path.abspath(a.data))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    datadir = os.path.dirname(os.path.abspath(a.data))
    out = a.out or os.path.join(datadir, "ppt_assets", "routes")
    os.makedirs(out, exist_ok=True)

    real = {}
    if a.real_day and a.real_map and os.path.exists(a.real_map):
        real[a.real_day] = a.real_map

    for d in getattr(mod, "days", []):
        no = int(d["day"].replace("Day ", ""))
        out_p = os.path.join(out, "day%02d.png" % no)
        if no in real:
            Image.new("RGB", (W, H), NAVY1).save(out_p)  # placeholder to avoid race
            img = place_real(no, real[no], a.font)
            print("real map -> day%02d.png" % no)
        else:
            names = [n for n, _ in d.get("intro", [])]
            img = gen_schematic(no, names, a.font)
            print("schematic -> day%02d.png (%d 点)" % (no, len(names)))
        img.save(out_p, "PNG")

if __name__ == "__main__":
    main()
