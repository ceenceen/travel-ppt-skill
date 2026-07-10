# -*- coding: utf-8 -*-
"""travel-ppt 图片抓取：为每个目的地抓精准实拍图（Pexels + alt 相关性打分），统一彩色后处理。

用法:
  python fetch_trip.py --map '{"beijing":["Forbidden City Beijing palace","Beijing Tiananmen"], ...}' \
      [--out ppt_assets/photos] [--fetch-images "C:/.../spacex-ppt-skill/scripts/fetch_images.py"]

说明:
- Pexels key 默认从 spacex-ppt-skill/scripts/pexels_key.txt 读取（无环境变量时）。
- 对每个 slug 搜索多个候选，按 Pexels 返回的 alt 描述做关键词相关性打分，自动挑最贴合的图。
- 后处理：裁到 1920x1080，压暗 0.82 + 提饱和 1.05 + 提对比 1.06（保留彩色，不用 duotone）。
- 已存在的 {slug}.jpg 会跳过（可删后重抓）。
- Pexels 对某城/小众地标无精准图时（alt 全是别的城市），脚本会告警，此时改用 ImageGen 工具按地标提示词生成，
  再单独运行 postprocess.py 统一风格（见 references/workflow.md）。
"""
import os, sys, io, re, json, argparse, importlib.util
from PIL import Image, ImageEnhance

DEFAULT_FETCH = r"C:\Users\Administrator\.workbuddy\skills\spacex-ppt-skill\scripts\fetch_images.py"

def load_fetch(path):
    spec = importlib.util.spec_from_file_location("fetch_images", path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def score(alt, must, avoid):
    a = (alt or "").lower()
    s = 0
    for w in must:
        if w.lower() in a: s += 2
    for w in avoid:
        if w.lower() in a: s -= 5
    return s

def best_photo(F, key, queries, avoid):
    best = None; best_s = -999
    for q in queries:
        try:
            ph = F.search(key, q, "landscape", 12)
        except Exception as e:
            print("  搜索失败 %s: %s" % (q, e)); continue
        for p in ph:
            must = re.findall(r"[A-Za-z]+", q)
            s = score(p.get("alt"), must, avoid)
            if s > best_s:
                best_s = s; best = p
    return best, best_s

def postprocess(src_path, dst_path, darken=0.82, sat=1.05, con=1.06):
    img = Image.open(src_path).convert("RGB")
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Contrast(img).enhance(con)
    img = ImageEnhance.Brightness(img).enhance(darken)
    w,h = img.size; tw,th = 1920,1080
    scale = max(tw/w, th/h); nw,nh = int(w*scale), int(h*scale)
    img = img.resize((nw,nh), Image.LANCZOS)
    img = img.crop(((nw-tw)//2,(nh-th)//2,(nw-tw)//2+tw,(nh-th)//2+th))
    img.save(dst_path, "JPEG", quality=88)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True, help='JSON: {"slug":["query1","query2"]}')
    ap.add_argument("--out", default="ppt_assets/photos")
    ap.add_argument("--fetch-images", default=DEFAULT_FETCH)
    ap.add_argument("--avoid", default="vietnam,jiujiang,chongqing,tianjin,huangshan,huashan",
                    help="逗号分隔的排除词（出现在 alt 里则扣分）")
    a = ap.parse_args()

    F = load_fetch(a.fetch_images)
    key = F.load_key()
    mp = json.loads(a.map)
    avoid = [x.strip() for x in a.avoid.split(",") if x.strip()]
    os.makedirs(a.out, exist_ok=True)

    for slug, queries in mp.items():
        dst = os.path.join(a.out, slug + ".jpg")
        if os.path.exists(dst):
            print("[skip] %s 已存在" % slug); continue
        print("抓取 %s ..." % slug)
        best, sc = best_photo(F, key, queries, avoid)
        if not best:
            print("  [WARN] %s 未找到候选，请用 ImageGen 生成" % slug); continue
        print("  选中 id=%s score=%d alt=%s" % (best.get("id"), sc, best.get("alt")))
        url = best.get("src", {}).get("large2x") or best.get("src", {}).get("large") or best.get("src", {}).get("original")
        try:
            ir = F.requests.get(url, timeout=90)
            raw = os.path.join(a.out, slug + "_raw.jpg")
            open(raw, "wb").write(ir.content)
            postprocess(raw, dst)
            os.remove(raw)
            print("  已存 %s (%dKB)" % (dst, os.path.getsize(dst)//1024))
        except Exception as e:
            print("  下载/处理失败: %s" % e)

if __name__ == "__main__":
    main()
