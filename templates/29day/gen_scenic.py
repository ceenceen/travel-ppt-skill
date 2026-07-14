# -*- coding: utf-8 -*-
"""gen_scenic.py —— 生成写实风雪山/高原剪影背景（离线，Pexels 被墙时的替代）。
输出 images/landscape-sil-01..06.jpg，供川藏段(无实拍)每日背景使用。
"""
import os, math, random
from PIL import Image, ImageDraw

IMG_DIR = os.path.join(os.getcwd(), 'images')
random.seed(7)

W, H = 1600, 900

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def sky(draw, top, bot):
    for y in range(H):
        t = y / H
        c = lerp(top, bot, t)
        draw.line([(0, y), (W, y)], fill=c)

def mountain_range(draw, base_y, amp, color, snow=0.18, jag=0.5):
    """画一层山脊剪影；snow>0 时顶部加白雪。"""
    pts = [(0, H)]
    x = 0
    phase = random.uniform(0, 6.28)
    while x <= W:
        n = math.sin(x / 220 + phase) * 0.5 + math.sin(x / 90 + phase * 2) * 0.3
        n += random.uniform(-jag, jag) * 0.15
        y = base_y - amp * (0.5 + 0.5 * n)
        # 尖峰
        if random.random() < 0.04:
            y -= random.uniform(0.2, 0.5) * amp
        pts.append((x, int(y)))
        x += random.randint(40, 90)
    pts.append((W, H))
    draw.polygon(pts, fill=color)
    # 雪线
    if snow > 0:
        snow_pts = []
        for (px, py) in pts:
            if py < base_y - amp * (1 - snow):
                snow_pts.append((px, py))
        # 简化：在脊线以上画浅色描边
        draw.line(pts, fill=lerp(color, (235, 240, 248), 0.55), width=3)

def make(idx, palette):
    top, bot, m1, m2, m3 = palette
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    sky(d, top, bot)
    # 远山
    mountain_range(d, H * 0.62, 120, m1, snow=0.0, jag=0.4)
    # 中景山
    mountain_range(d, H * 0.74, 180, m2, snow=0.22, jag=0.6)
    # 近景山（最深）
    mountain_range(d, H * 0.9, 150, m3, snow=0.12, jag=0.8)
    # 暗角
    vig = Image.new('L', (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, W, H], fill=0)
    vd.ellipse([-W * 0.3, -H * 0.3, W * 1.3, H * 1.3], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new('RGB', (W, H), (0, 0, 0))
    im = Image.composite(im, dark, vig)
    out = os.path.join(IMG_DIR, f'landscape-sil-{idx:02d}.jpg')
    im.save(out, 'JPEG', quality=86)
    print('saved', out)

from PIL import ImageFilter

PALETTES = [
    ((28, 38, 58), (12, 18, 30), (40, 52, 74), (24, 34, 52), (12, 18, 30)),   # 夜蓝
    ((46, 60, 82), (22, 30, 46), (54, 70, 96), (32, 44, 66), (16, 24, 38)),   # 晨青
    ((60, 70, 84), (30, 38, 50), (70, 82, 98), (44, 54, 70), (22, 30, 42)),   # 雾灰
    ((38, 52, 70), (16, 24, 38), (48, 64, 88), (28, 40, 60), (14, 22, 34)),   # 湖蓝
    ((58, 50, 64), (26, 22, 34), (68, 58, 78), (40, 34, 50), (20, 16, 28)),   # 暮紫
    ((52, 64, 76), (24, 32, 42), (62, 76, 92), (36, 48, 64), (18, 26, 38)),   # 高原青
]

for i, pal in enumerate(PALETTES, 1):
    make(i, pal)
print('done', len(PALETTES), 'scenic backgrounds')
