# -*- coding: utf-8 -*-
"""景点图鉴：从 Pexels 抓取每个景点的精准实拍，全局去重 + 感知距离二次核查。

用法 / Usage:
  python fetch_spot_photos.py --data spot_gallery_data.py [--out spot_gallery]

数据模块需定义 / The data module must define:
  GROUPS       : [(cn_theme, en_sub, [spot_cn, ...]), ...]
  SPOT_QUERIES : {spot_cn: (query_en, [expected_keywords])}   # 可选，缺省按景点名兜底
  DAYS         : {spot_cn: int}                                # 可选（仅用于日志/校验）

行为 / Behavior:
  1. 收集 GROUPS 里全部景点（去重展开）。
  2. 第一轮：多页搜索 + alt 相关性打分，挑「全局唯一」(photo id + md5 未占用) 的最佳图。
  3. 第二轮（感知哈希二次核查）：任意两图距离 ≤ THRESH 视为近似重复，对后者重抓并
     强制其与全场其他图感知距离 ≥ MIN_DIST；仍不行则写入 _fallback.txt（由 agent 用 ImageGen 兜底）。
  4. 写出 spot_gallery/{spot_cn}.jpg 与 CREDITS.txt（Pexels 署名，需随 deck 保留）。

图片策略 / Image strategy: 优先 Pexels 真实摄影；仅当 Pexels 搜不到贴合图时才回退 ImageGen（写 _fallback.txt）。
"""
import os
import sys
import io
import time
import importlib.util
import hashlib

import requests
from PIL import Image

API = 'https://api.pexels.com/v1/search'
THRESH = 6      # 8x8 平均哈希(64bit) 视为「近似重复」的距离阈值
MIN_DIST = 10   # 二次重抓时，强制新图与全场其他图的最小感知距离


# ---------- key ----------
def load_key():
    k = os.environ.get('PEXELS_API_KEY')
    if k:
        return k
    for p in ('scripts/pexels_key.txt', 'pexels_key.txt'):
        if os.path.exists(p):
            return open(p, encoding='utf-8').read().strip()
    return None


# ---------- hashing ----------
def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def ahash_bytes(data, size=8):
    im = Image.open(io.BytesIO(data)).convert('L').resize((size, size), Image.LANCZOS)
    px = list(im.get_flattened_data())
    mean = sum(px) / len(px)
    v = 0
    for b in px:
        v = (v << 1) | (1 if b > mean else 0)
    return v


def ahash_file(path, size=8):
    im = Image.open(path).convert('L').resize((size, size), Image.LANCZOS)
    px = list(im.get_flattened_data())
    mean = sum(px) / len(px)
    v = 0
    for b in px:
        v = (v << 1) | (1 if b > mean else 0)
    return v


def ham(a, b):
    x = a ^ b
    c = 0
    while x:
        c += x & 1
        x >>= 1
    return c


# ---------- pexels ----------
def search(sess, key, q, page, retries=3):
    h = {'Authorization': key}
    for attempt in range(retries):
        try:
            time.sleep(0.5)
            r = sess.get(API, params={'query': q, 'per_page': 30, 'page': page,
                                      'orientation': 'landscape'}, headers=h, timeout=30)
            if r.status_code == 200:
                return r.json().get('photos', [])
        except Exception as e:
            print(f'  NETERR {q} p{page} a{attempt+1} {e}', flush=True)
            time.sleep(1.5 * (attempt + 1))
    return []


def score(ph, expected):
    return sum(1 for w in expected if w in (ph.get('alt') or '').lower())


def best_url(ph):
    src = ph.get('src', {})
    return (src.get('large2x') or src.get('large') or src.get('medium')
            or src.get('original'))


def download(sess, url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(0.3)
            r = sess.get(url, timeout=40)
            r.raise_for_status()
            return r.content
        except Exception as e:
            print(f'  DLERR a{attempt+1} {e}', flush=True)
            time.sleep(1.5 * (attempt + 1))
    return None


def load_data(path):
    spec = importlib.util.spec_from_file_location('spot_data', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def spots_from_groups(mod):
    seen = []
    for _, _, spots in getattr(mod, 'GROUPS', []):
        for s in spots:
            if s not in seen:
                seen.append(s)
    return seen


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True, help='spot gallery data module (.py)')
    ap.add_argument('--out', default='spot_gallery')
    a = ap.parse_args()

    mod = load_data(a.data)
    key = load_key()
    if not key:
        print('NO_PEXELS_KEY — 设置 PEXELS_API_KEY 或 scripts/pexels_key.txt', flush=True)
        sys.exit(2)

    spots = spots_from_groups(mod)
    queries = getattr(mod, 'SPOT_QUERIES', {})
    os.makedirs(a.out, exist_ok=True)

    sess = requests.Session()
    used_ids = set()
    used_md5 = set()
    store = {}        # cn -> {'data':bytes, 'pid':int, 'meta':dict}
    fallback = []

    # ---------- 第一轮：全局去重抓取 ----------
    for cn in spots:
        q, expected = queries.get(cn, (cn + ' travel photography', [w for w in cn if ord(w) < 128]))
        cands = []
        for page in range(1, 4):
            for ph in search(sess, key, q, page):
                cands.append((score(ph, expected), ph))
        cands.sort(key=lambda x: x[0], reverse=True)

        chosen = None
        for sc, ph in cands:
            pid = ph.get('id')
            if pid in used_ids:
                continue
            url = best_url(ph)
            if not url:
                continue
            data = download(sess, url)
            if not data:
                continue
            m = md5_bytes(data)
            if m in used_md5:
                continue
            chosen = (pid, m, data, ph)
            break

        if chosen is None:
            print(f'FALLBACK_AI {cn}', flush=True)
            fallback.append(cn)
            continue
        pid, m, data, ph = chosen
        used_ids.add(pid)
        used_md5.add(m)
        store[cn] = {'data': data, 'pid': pid, 'meta': ph}
        print(f'OK {cn} score=top', flush=True)

    # ---------- 第二轮：感知哈希二次核查 ----------
    hashes = {cn: ahash_bytes(store[cn]['data']) for cn in store}
    # 找近似重复对（距离小者重抓）
    pairs = [(cn, on, ham(hashes[cn], hashes[on]))
             for i, cn in enumerate(hashes) for on in list(hashes)[i+1:]
             if ham(hashes[cn], hashes[on]) <= THRESH]
    for cn, on, d in pairs:
        # 重抓 cn：强制与全场其他图距离 ≥ MIN_DIST
        q, expected = queries.get(cn, (cn + ' travel photography', []))
        better = None
        best_key = (-1, -1)
        for page in range(1, 4):
            for ph in search(sess, key, q, page):
                pid = ph.get('id')
                if pid in used_ids:
                    continue
                url = best_url(ph)
                if not url:
                    continue
                data = download(sess, url)
                if not data:
                    continue
                m = md5_bytes(data)
                if m in used_md5:
                    continue
                h = ahash_bytes(data)
                others = [hashes[o] for o in hashes if o != cn]
                mind = min((ham(h, o) for o in others), default=64)
                ok = 1 if mind >= MIN_DIST else 0
                if (ok, mind) > best_key:
                    best_key = (ok, mind)
                    better = (pid, m, data, ph)
                if ok:
                    break
            if better and best_key[0]:
                break
        if better:
            pid, m, data, ph = better
            used_ids.discard(store[cn]['pid'])
            used_md5.discard(md5_bytes(store[cn]['data']))
            store[cn] = {'data': data, 'pid': pid, 'meta': ph}
            hashes[cn] = ahash_bytes(data)
            used_ids.add(pid)
            used_md5.add(m)
            print(f'REDUP {cn} (was~{on} d={d}) -> min_dist={best_key[1]}', flush=True)
        else:
            print(f'REDUP_FAIL {cn} (still~{on}); 建议 ImageGen 兜底', flush=True)

    # ---------- 写出 ----------
    credits = []
    for cn, info in store.items():
        path = os.path.join(a.out, cn + '.jpg')
        with open(path, 'wb') as f:
            f.write(info['data'])
        ph = info['meta']
        credits.append(f"{cn}\t{ph.get('photographer','?')}\t{ph.get('url','')}")
    with open(os.path.join(a.out, 'CREDITS.txt'), 'w', encoding='utf-8') as f:
        f.write('Pexels 署名 / Pexels attribution\n')
        f.write('=' * 40 + '\n')
        f.write('\n'.join(credits) + '\n')
    with open(os.path.join(a.out, '_fallback.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(fallback))

    print(f'--- done: {len(store)} ok, {len(fallback)} fallback -> {a.out}/', flush=True)
    if fallback:
        print('需 ImageGen 兜底:', fallback, flush=True)


if __name__ == '__main__':
    main()
