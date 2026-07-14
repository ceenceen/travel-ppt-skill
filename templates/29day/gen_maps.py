"""gen_maps.py —— 真实路线地图生成器（自驾 / 户外环线场景）

把一份逐日路线渲染成「真实卫星底图 + 中文注记 + 轨迹标绘」的小尺寸 PNG，
用于每日行程页右上角小框（1180x400，比例 2.95）。

依赖: Pillow, numpy, matplotlib，以及联网（高德瓦片，国内直连、免 API key）。
数据来源: 与本 skill 的 gen_pptx_roadtrip.py 共用同一个 trip_data.py：
    NODE = {'地点名': (lon_WGS84, lat_WGS84), ...}   # 所有途经点经纬度（WGS-84）
    DAYS = [(day, start, [ways...], end, km), ...]    # 逐日路线；km 仅用于图例
输出: <DECK_DIR>/maps/day_map_{day}.png

用法: 在含 trip_data.py 的旅行目录下执行
    python gen_maps.py
"""
import os, sys, io, math, time, concurrent.futures, ssl
import urllib.request
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as pe

# 把工作目录优先加入 path，使 `import trip_data` 成功（trip_data.py 放在旅行目录）
sys.path.insert(0, os.getcwd())
try:
    from trip_data import NODE, DAYS
except Exception:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from trip_data import NODE, DAYS

try:
    FONT = FontProperties(fname=r'C:/Windows/Fonts/msyh.ttc')
except Exception:
    FONT = FontProperties()

ACCENT = '#ff8c2e'
ORANGE = '#ffc078'
CYAN   = '#39d6ff'
GREY   = '#e8eef6'
FRAME  = '#4a7fb5'

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# ---------- WGS-84 -> GCJ-02（高德瓦片使用火星坐标系）----------
A = 6378245.0
EE = 0.00669342162296594323
def _tlat(x, y):
    r = (-100 + 2*x + 3*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
         + (20*math.sin(6*x*math.pi) + 20*math.sin(2*x*math.pi))*2/3
         + (20*math.sin(y*math.pi) + 40*math.sin(y/3*math.pi))*2/3
         + (160*math.sin(y/12*math.pi) + 320*math.sin(y*math.pi/30))*2/3)
    return r
def _tlon(x, y):
    r = (300 + x + 2*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
         + (20*math.sin(6*x*math.pi) + 20*math.sin(x/3*math.pi))*2/3
         + (20*math.sin(x*math.pi) + 40*math.sin(x/30*math.pi))*2/3)
    return r
def wgs_gcj(lon, lat):
    """把 WGS-84 经纬度转换成高德/国测局 GCJ-02 坐标。"""
    if lon < 72.004 or lon > 137.834 or lat < 0.829 or lat > 55.827:
        return lon, lat
    dlat = _tlat(lon - 105, lat - 35)
    dlon = _tlon(lon - 105, lat - 35)
    rl = lat/180*math.pi
    magic = math.sin(rl); magic = 1 - EE*magic*magic
    sm = math.sqrt(magic)
    dlat = (dlat*180)/((A*(1-EE))/(magic*sm)*math.pi)
    dlon = (dlon*180)/(A/sm*math.cos(rl)*math.pi)
    return lon + dlon, lat + dlat

def fetch_tile(x, y, z, style):
    """下载高德瓦片：style=6 卫星影像，style=8 中文注记层。带重试与长超时（代理抖动）。"""
    host = f'wprd0{1 + (x*3 + y) % 4}'
    url = (f'https://{host}.is.autonavi.com/appmaptile?style={style}'
           f'&x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1')
    last = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=60, context=CTX).read()
        except Exception as e:
            last = e
            time.sleep(1.5 + attempt)
    raise last

def lat2y(lat, z):
    n = 2**z; lr = math.radians(lat)
    return (1 - math.log(math.tan(lr) + 1/math.cos(lr))/math.pi)/2*n

def pick_z(dl):
    z = round(math.log2(1800/max(dl, 0.02)))
    return max(6, min(14, z))

def build_base(bbox, z):
    """下载高德卫星影像(style=6)+中文注记(style=8)，拼接为真实底图；bbox=(ml,ML,ma,MA)"""
    ml, ML, ma, MA = bbox
    n = 2**z
    x0 = max(0, int((ml+180)/360*n)); x1 = min(n-1, int((ML+180)/360*n))
    y0 = max(0, int(lat2y(MA, z))); y1 = min(n-1, int(lat2y(ma, z)))
    W = (x1-x0+1)*256; H = (y1-y0+1)*256
    base = Image.new('RGB', (W, H))
    note = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    jobs = [(x, y) for x in range(x0, x1+1) for y in range(y0, y1+1)]

    def get(job):
        x, y = job
        try:
            img = Image.open(io.BytesIO(fetch_tile(x, y, z, 6))).convert('RGB')
        except Exception:
            img = Image.open(io.BytesIO(fetch_tile(x, y, z, 7))).convert('RGB')
        nt = None
        try:
            nt = Image.open(io.BytesIO(fetch_tile(x, y, z, 8))).convert('RGBA')
            # 把注记瓦片的背景色设为透明（高德部分瓦片背景不透明）
            arr = np.array(nt)
            corners = np.array([arr[0, 0, :3], arr[0, -1, :3],
                                arr[-1, 0, :3], arr[-1, -1, :3]])
            bg = np.median(corners, axis=0)
            diff = np.abs(arr[..., :3].astype(float) - bg).sum(axis=2)
            mask = diff <= 28
            arr[..., 3] = np.where(mask, 0, arr[..., 3])
            nt = Image.fromarray(arr)
        except Exception:
            nt = None
        return job, img, nt

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for job, img, nt in ex.map(get, jobs):
            x, y = job
            base.paste(img, ((x-x0)*256, (y-y0)*256))
            if nt is not None:
                note.paste(nt, ((x-x0)*256, (y-y0)*256), nt)

    # 清理缺失/灰色瓦片：用有效瓦片均值暗化后填充（避免边境/低覆盖区出现大块灰斑）
    valid_means = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            tile = base.crop(((x - x0) * 256, (y - y0) * 256,
                              (x - x0 + 1) * 256, (y - y0 + 1) * 256))
            arr = np.array(tile)
            mean_ch = arr.mean(axis=(0, 1))
            if arr.std() > 18 or np.ptp(mean_ch) > 30:
                valid_means.append(mean_ch)
    if valid_means:
        fill = tuple((np.median(valid_means, axis=0) * 0.6).astype(np.uint8))
    else:
        fill = (6, 18, 31)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            tile = base.crop(((x - x0) * 256, (y - y0) * 256,
                              (x - x0 + 1) * 256, (y - y0 + 1) * 256))
            arr = np.array(tile)
            mean_ch = arr.mean(axis=(0, 1))
            if arr.std() <= 18 and np.ptp(mean_ch) <= 30:
                base.paste(Image.new('RGB', (256, 256), fill),
                         ((x - x0) * 256, (y - y0) * 256))

    arr = np.array(base)
    print(f'  base {W}x{H} z{z} mean={arr.mean():.0f} std={arr.std():.0f}')
    return base, note, W, H, x0, y0, z

def halo():
    return [pe.withStroke(linewidth=3.0, foreground='#06121f')]

def draw(day, start, ways, end, km):
    """绘制某一天的真实路线地图，保存到 <DECK_DIR>/maps/day_map_{day}.png。"""
    raw = [start] + ways + [end]
    seen = []
    for p in raw:
        if p not in seen:
            seen.append(p)
    coords = [wgs_gcj(*NODE[p]) for p in seen]
    lons = [c[0] for c in coords]; lats = [c[1] for c in coords]
    ml, ML = min(lons), max(lons)
    ma, MA = min(lats), max(lats)
    dl = ML - ml; dla = MA - ma

    OUT_W, OUT_H = 1180, 400   # 右上角小框比例（2.95）
    BOX_ASPECT = OUT_W / OUT_H

    eps = 0.02
    if dl < eps and dla < eps:
        # 单点（同城环线）：城市级视野
        z = 14
        span = 360 / (2**z) * 4
        cx, cy = (ml+ML)/2, (ma+MA)/2
        ml, ML = cx-span/2, cx+span/2
        ma, MA = cy-span/2, cy+span/2
    else:
        # 紧贴路线缩放：只按路线本身加 5% 边距，不再硬扩比例
        cx, cy = (ml+ML)/2, (ma+MA)/2
        hw, hh = dl/2 * 1.05, dla/2 * 1.05
        ml, ML = cx-hw, cx+hw
        ma, MA = cy-hh, cy+hh
    bbox_w = ML - ml
    bbox_h = MA - ma
    route_aspect = bbox_w / bbox_h

    z = pick_z(max(bbox_w, bbox_h))
    base, note, W, H, x0, y0, z = build_base((ml, ML, ma, MA), z)

    # 把真实地图按原比例嵌入 1180×400 输出，剩余区域用深色填充
    if route_aspect > BOX_ASPECT:
        inner_w = OUT_W
        inner_h = max(1, int(OUT_W / route_aspect))
    else:
        inner_h = OUT_H
        inner_w = max(1, int(OUT_H * route_aspect))
    pad_x = (OUT_W - inner_w) / 2
    pad_y = (OUT_H - inner_h) / 2

    base = base.resize((inner_w, inner_h), Image.LANCZOS)
    if note is not None:
        note = note.resize((inner_w, inner_h), Image.LANCZOS)

    def to_fig(lon, lat):
        n = 2**z
        px = ((lon + 180) / 360 * n - x0) * 256
        py = (lat2y(lat, z) - y0) * 256
        fx = pad_x + px * inner_w / W
        fy = pad_y + py * inner_h / H
        return fx, fy
    pxs = [to_fig(lon, lat) for lon, lat in coords]
    lx = [p[0] for p in pxs]; ly = [p[1] for p in pxs]

    fig, ax = plt.subplots(figsize=(5.9, 2.0), dpi=200, facecolor='#06121f')
    ax.imshow(base, extent=(pad_x, pad_x+inner_w, pad_y+inner_h, pad_y))
    if note is not None:
        ax.imshow(note, extent=(pad_x, pad_x+inner_w, pad_y+inner_h, pad_y))
    ax.set_xlim(0, OUT_W); ax.set_ylim(OUT_H, 0)
    ax.set_axis_off()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # 轨迹
    ax.plot(lx, ly, color=ACCENT, lw=9, alpha=0.16, zorder=5)
    ax.plot(lx, ly, color=ACCENT, lw=3.2, zorder=6)

    n_way = len(coords) - 2
    way_lons = lons[1:-1]
    way_lats = lats[1:-1]
    wlon = max(way_lons) - min(way_lons) if n_way > 1 else 0
    wlat = (max(way_lats) - min(way_lats)) if n_way > 1 else 0
    dense = (n_way >= 3 and wlon < 1.2 and wlat < 1.5)
    loop = (start == end)

    # 起点
    if not loop:
        ax.scatter([lx[0]], [ly[0]], s=240, color=CYAN, edgecolor='white',
                   lw=1.6, zorder=8, clip_on=False)
        ax.annotate('起 ' + seen[0], (lx[0], ly[0]), textcoords='offset points',
                    xytext=(9, 9), color=CYAN, fontsize=12, fontweight='bold',
                    fontproperties=FONT, zorder=10, path_effects=halo(), clip_on=False)
    # 住宿点
    ax.scatter([lx[-1]], [ly[-1]], marker='*', s=600, color=ACCENT,
               edgecolor='white', lw=1.6, zorder=9, clip_on=False)
    ax.annotate('宿 ' + seen[-1], (lx[-1], ly[-1]), textcoords='offset points',
                xytext=(9, -17), color=ACCENT, fontsize=13, fontweight='bold',
                fontproperties=FONT, zorder=10, path_effects=halo(), clip_on=False)

    # 途经点
    if dense:
        names = '  '.join(seen[1:-1])
        ax.text(OUT_W/2, pad_y + inner_h - 14, names, color=ORANGE,
                fontsize=12, ha='center', va='top', fontproperties=FONT,
                zorder=10, path_effects=halo(), clip_on=False,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a1622cc',
                          edgecolor=FRAME, linewidth=1.0))
    else:
        last = None
        for i in range(1, len(coords) - 1):
            ax.scatter([lx[i]], [ly[i]], marker='D', s=140, color=ORANGE,
                       edgecolor='white', lw=1.2, zorder=8, clip_on=False)
            if last and abs(lx[i]-last[0]) < 45 and abs(ly[i]-last[1]) < 45:
                last = (lx[i], ly[i]); continue
            dy = 14 if i % 2 == 1 else -20
            ax.annotate(seen[i], (lx[i], ly[i]), textcoords='offset points',
                        xytext=(9, dy), color=ORANGE, fontsize=11,
                        fontproperties=FONT, zorder=10, path_effects=halo(), clip_on=False)
            last = (lx[i], ly[i])

    # 指北针（右上角）
    ax.annotate('N', xy=(0.96, 0.92), xytext=(0.96, 0.84), transform=ax.transAxes,
                color=CYAN, fontsize=13, fontweight='bold', fontproperties=FONT,
                ha='center', zorder=11, path_effects=halo(), clip_on=False,
                arrowprops=dict(arrowstyle='->', color=CYAN, lw=1.8))

    buf = io.BytesIO()
    plt.savefig(buf, dpi=200)
    plt.close()
    im = Image.open(buf).convert('RGB').resize((OUT_W, OUT_H))
    out_dir = os.path.join(os.getcwd(), 'maps')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'day_map_{day}.png')
    im.save(out)
    print('saved', out, im.size)

if __name__ == '__main__':
    for d in DAYS:
        draw(*d)
    print('ALL MAPS DONE')
