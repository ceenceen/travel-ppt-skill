# -*- coding: utf-8 -*-
"""gen_assets.py —— 离线生成深色渐变背景与当日景点卡片（Pexels 被墙时的替代方案）。
生成:
  images/landscape-01..12.jpg   16:9 深色渐变背景（带极淡等高线肌理）
  spot_photos/spot_01..29.png   1180x400 当日景点卡片（深色 + 主景点名）
依赖: Pillow, numpy（numpy 仅用于背景噪声，缺失则用纯 PIL）
"""
import os, math, sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFont

try:
    import numpy as np
    HAVE_NP = True
except Exception:
    HAVE_NP = False

FONT = r'C:/Windows/Fonts/msyh.ttc'
try:
    F = ImageFont.truetype(FONT, 46)
    F_SM = ImageFont.truetype(FONT, 26)
    F_TINY = ImageFont.truetype(FONT, 20)
except Exception:
    F = ImageFont.load_default()
    F_SM = F
    F_TINY = F

# 12 套深色配色（深蓝→墨绿→暗紫，保持高级冷调）
PALETTES = [
    ((11,18,30),(22,38,58)), ((14,22,34),(26,42,60)),
    ((12,20,28),(20,34,46)), ((16,20,32),(30,38,56)),
    ((10,20,26),(18,40,52)), ((18,16,30),(34,30,54)),
    ((12,18,26),(24,36,50)), ((14,24,30),(28,46,58)),
    ((16,18,28),(32,40,56)), ((10,22,24),(16,40,46)),
    ((18,18,28),(36,34,52)), ((12,16,24),(22,32,48)),
]

def gradient(w, h, c1, c2, angle=35):
    img = Image.new('RGB', (w, h))
    px = img.load()
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    for y in range(h):
        for x in range(w):
            t = (x*dx + y*dy) / (w*dx + h*dy)
            t = max(0.0, min(1.0, t))
            r = int(c1[0] + (c2[0]-c1[0])*t)
            g = int(c1[1] + (c2[1]-c1[1])*t)
            b = int(c1[2] + (c2[2]-c1[2])*t)
            px[x, y] = (r, g, b)
    return img

def add_contour(img, c1, c2, n=5):
    """叠加极淡的等高线肌理，增加地图/地形气质。"""
    w, h = img.size
    d = ImageDraw.Draw(img, 'RGBA')
    for k in range(1, n+1):
        base = 30 + k*36
        amp = 10 + k*4
        col = (c2[0], c2[1], c2[2], 26)
        for yy in range(0, h, 2):
            pts = []
            for xx in range(0, w+4, 4):
                off = int(math.sin((xx/120.0) + k*0.7) * amp + math.cos((yy/90.0)+k)*amp*0.5)
                pts.append((xx, base + off))
            if len(pts) > 1:
                d.line(pts, fill=col, width=1)
    return img

def gen_backgrounds():
    os.makedirs(os.path.join(HERE, 'images'), exist_ok=True)
    W, H = 1920, 1080
    for i, (c1, c2) in enumerate(PALETTES, 1):
        img = gradient(W, H, c1, c2, angle=30 + i*4)
        if HAVE_NP:
            arr = np.array(img).astype(float)
            noise = (np.random.rand(H, W, 1) - 0.5) * 10
            arr = np.clip(arr + noise, 0, 255).astype('uint8')
            img = Image.fromarray(arr)
        img = add_contour(img, c1, c2)
        out = os.path.join(HERE, 'images', f'landscape-{i:02d}.jpg')
        img.save(out, quality=88)
        print('bg', out)

def gen_spot_cards():
    import trip_data as td
    os.makedirs(os.path.join(HERE, 'spot_photos'), exist_ok=True)
    W, H = 1180, 400
    for day in range(1, 30):
        name = td.DAY_SPOT.get(day, f'DAY {day}')
        pal = PALETTES[(day-1) % len(PALETTES)]
        img = gradient(W, H, pal[0], pal[1], angle=20)
        img = add_contour(img, pal[0], pal[1], n=4)
        d = ImageDraw.Draw(img, 'RGBA')
        # 底部暗条
        d.rectangle([0, H-150, W, H], fill=(0, 0, 0, 120))
        # 顶部小标签
        d.text((40, 28), f'DAY {day}', font=F_TINY, fill=(200, 210, 222, 230))
        # 主景点名（居中偏左）
        d.text((40, 70), name, font=F, fill=(255, 255, 255, 255))
        # 细线
        d.line([(40, 150), (W-40, 150)], fill=(255, 255, 255, 70), width=2)
        # 下方小字说明
        sub = '当日核心看点'
        d.text((40, H-120), sub, font=F_SM, fill=(180, 192, 204, 220))
        out = os.path.join(HERE, 'spot_photos', f'spot_{day}.png')
        img.save(out)
        print('card', out)

if __name__ == '__main__':
    gen_backgrounds()
    gen_spot_cards()
    print('ALL ASSETS DONE')
