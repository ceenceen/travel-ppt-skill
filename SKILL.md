---
name: travel-ppt
description: 把结构化行程数据渲染成 16:9 可编辑旅行 PPTX。内置三类行程场景：① 城市多日游（Pexels 实拍 + 单栏背景）；② 自驾 / 户外环线（真实路线地图 + 每日双框排版：全幅背景 + 右上真实地图 + 右下景点图原比例 + 左列四块文字）；③ 景点图鉴（按主题分组的紧凑网格陈列，每格景点实拍 + 到达日标签，深色高级风、白强调）。触发词：行程PPT / 旅行PPT / 旅游攻略PPT / 自驾PPT / 环线PPT / 景点图鉴 / 景点清单 / 看点手册 / itinerary slideshow / travel deck / roadtrip PPT / self-drive itinerary / spot gallery / highlights catalogue。
version: 3.1.0
disable: false
---

# Travel PPT — 行程幻灯片生成器（双语 / Bilingual）
# Travel PPT — Itinerary Slides Generator (Bilingual)

把一份**结构化行程数据**渲染成 16:9 可编辑 PPTX：封面 → 路线总览 → 关键数据 → **每天单独一页** → 预算 → 住宿 → 收尾。
Render a **structured itinerary** into an editable 16:9 PPTX: cover → route overview → key stats → **one slide per day** → budget → stay → closing.

本 skill 是一个统一工具，内置三类行程场景 / This is one unified skill with three built-in trip scenarios:

- **城市多日游 City Multi-day Tour**：Pexels 精准实拍作背景（非黑白），单栏排版。见 `scripts/gen_pptx.py` + `templates/trip_data_template.py`。
- **自驾 / 户外环线 Roadtrip / Outdoor Loop**：全幅背景 + 右上**真实路线地图**（高德卫星瓦片）+ 右下**当天景点图（原比例）** + 左列四块文字。见 `scripts/gen_maps.py` + `scripts/gen_pptx_roadtrip.py` + `templates/roadtrip_data_template.py` + `references/roadtrip_layout.md`。
- **景点图鉴 Spot Gallery**：把一趟行程的所有景点按主题分组，做**紧凑网格陈列**（深色高级风、白强调、极小间距），每格一张景点实拍 + 景点名 + **到达日标签**。见 `scripts/fetch_spot_photos.py`（抓图 + 全局去重 + 感知哈希二次核查）+ `scripts/gen_spot_gallery.py`（排版）+ `templates/spot_gallery_template.py`（数据模板）+ `references/spot_gallery_layout.md`。适合做「行程看点清单 / 景点手册」附册。

三类场景共用同一套 Pexels 图片管线和同一套 python-pptx 排版内核，按行程类型自动选用，无需在多个子工具间切换。
All three scenarios share one Pexels image pipeline and one python-pptx layout core; the skill picks the right one by trip type — there is no separate "mode" to switch.

---

## 前置配置：Pexels API Key / Prerequisite: Pexels API Key

城市游与景点图鉴默认用 **Pexels 高清实拍**；自驾环线的当天景点图也优先用 Pexels。首次使用前需配置一个免费的 Pexels API Key（约 1 分钟）。
City tour and spot gallery use **Pexels high-res photos** by default; roadtrip spot photos also prefer Pexels. Configure a free Pexels API Key before first use (~1 min).

获取与配置 / Get & configure:
1. 打开 https://www.pexels.com/api/ ，注册/登录后点「Get Started」免费申请一个 API Key。
   Go to https://www.pexels.com/api/ , sign in and click "Get Started" to get a free API key.
2. 配置方式二选一 / Either way works:
   - **环境变量（推荐）**：设置 `PEXELS_API_KEY=你的key`，脚本自动读取。
     **Env var (recommended)**: set `PEXELS_API_KEY=your_key`; the script reads it automatically.
   - **密钥文件**：把 key 写进 `scripts/pexels_key.txt`（一行，纯 key，可加 `#` 注释）。
     **Key file**: put the key in `scripts/pexels_key.txt` (one line, the key only; `#` for comments).
3. 验证 / Verify: `python scripts/fetch_trip.py --map '{"beijing":["Forbidden City Beijing"]}'` 能抓到图即配置成功。
   `python scripts/fetch_trip.py --map '{"beijing":["Forbidden City Beijing"]}'` fetches an image → config OK.

图片策略（重要）/ Image strategy (important):
- **优先 Pexels 真实摄影**：有对应高清实拍就直接用，画面真实、版权可溯源（脚本会生成 `CREDITS.txt` 署名）。
  **Prefer Pexels real photography**: use it whenever a matching high-res shot exists — authentic and attributable (script writes `CREDITS.txt`).
- **Pexels 无合适图 → 再用 AI 生成**：仅当某目的地/小众地标在 Pexels 上搜不到贴合图（如 alt 全是别的城市）时，才回退 ImageGen 按地标提示词生成写实图。
  **Fall back to AI only when Pexels has no match**: only when a destination/obscure landmark has no fitting Pexels shot (e.g. alt text is all wrong cities), use ImageGen with a landmark-specific prompt.

> 注意：Pexels 要求署名，生成的 `CREDITS.txt` 请随 deck 保留。Key 属私密，不要把它提交进公开的 skill 仓库。
> Note: Pexels requires attribution — keep the generated `CREDITS.txt` with the deck. Keep the key private; never commit it into a public skill repo.

---

## 何时使用 / When to use
- 用户有多日行程（天数 ≥ 3），想要可放映/打印的行程册。
  User has a multi-day trip (≥3 days) and wants a presentable/printable deck.
- 提到「每天一页」「行程PPT」「旅行PPT」「自驾PPT」「旅游攻略PPT」「itinerary / travel deck / roadtrip PPT」。
  Mentions "one slide per day", "itinerary PPT", "travel deck", "roadtrip PPT", etc.
- 自驾/环线类行程 → 用**自驾 / 户外环线**场景（带真实地图）；城市观光类 → 用**城市多日游**场景。
  Self-drive / loop trips → use the **Roadtrip / Outdoor Loop** scenario (with real map); city tours → use the **City Multi-day Tour** scenario.
- 想单独做「景点图鉴 / 景点清单 / 看点手册」——把所有景点按主题网格陈列、每格带到达日 → 用**景点图鉴**场景。
  Want a standalone "spot gallery / highlights list" — all spots in a themed grid, each cell with arrival day → use the **Spot Gallery** scenario.

---

## 信息不足时主动询问 / Ask proactively when info is missing

本 skill 强依赖结构化数据。用户只说「做个旅行PPT / travel deck」而没给足材料时，**不要凭空捏造**（尤其 GPS 坐标、真实地名、里程、住宿点、文案），应先用 `AskUserQuestion` 澄清，再动手。
This skill depends heavily on structured data. If the user only says "make a travel PPT / travel deck" without enough material, **do not fabricate** (especially GPS coords, real place names, distances, stays, copy) — clarify with `AskUserQuestion` first, then build.

出发前必问（按需裁剪，不必一次全问）/ Ask up front (trim as needed, not all at once):
- **行程类型 Trip type**: 自驾/环线（有逐日 GPS 路线）→ 自驾/户外环线场景；城市观光（无路线）→ 城市多日游场景；只要景点清单 → 景点图鉴场景。
- **自驾 / 户外环线缺什么 What the Roadtrip scenario needs**:
  - 逐日路线 day-by-day route（每天 起点→途经→终点）。坐标(WGS-84)最好给；不给则问能否按地名推断或请用户补，绝不编造。
  - 每日文案 per-day copy：行程说明 / 经典介绍 / 注意事项 / 住宿点。缺失则请用户直接给，或由 agent 据路线先起草、再让用户改。
  - 图片策略 image strategy：背景风光照 + 当天景点图。**默认优先 Pexels 实拍**；仅当 Pexels 搜不到对应合适图时再用 AI 生成 / 用户自备。先定策略再生成。
- **城市多日游缺什么 What the City tour scenario needs**: 行程标题、城市/天数、酒店、预算；背景图关键词或自备图。Pexels 需要关键词，缺失则问。
- **景点图鉴缺什么 What the Spot Gallery scenario needs**: 景点清单（按主题分组）+ 每个景点的 Pexels 英文搜索词；到达日（可选，用于 Day N 标签）。
- **输出偏好 output prefs**: 文件名、是否要预算页/住宿页、语言（中文 / 中英双语）。

原则 / Rule of thumb: **缺数据先问、缺图先定策略、绝不编造坐标与事实**。问清后再跑生成器，避免返工。
Ask before building when data is missing, decide image strategy before generating, never invent coordinates or facts. Clarify first, then run the generator to avoid rework.

---

# 自驾 / 户外环线（真实地图）Roadtrip / Outdoor Loop (real map)

适用：自驾、摩旅、骑行、徒步等有明确逐日路线与 GPS 坐标的行程。
For: self-drive, motorcycle, cycling, trekking — any trip with a day-by-day route and GPS coordinates.

## 每日页版式 / Daily page layout
每页四区（详见 `references/roadtrip_layout.md`）：
Four zones per slide (see `references/roadtrip_layout.md`):

1. **全幅背景 Full-bleed background**：通用风光照 cover 铺满 + 暗化层（保证文字可读）。
2. **顶部标题 Top title**：日期标签 + 路线名 + 数据条（里程 / 时长 / 最高海拔）。
3. **左列四块 Left column (4 blocks)**：▸ 行程说明 / ▸ 经典介绍 / ▸ 注意事项 / ▸ 住宿点。
4. **右上双框 Right-top two frames**：
   - 上框 = **真实路线地图**（gen_maps.py 产出，高德卫星底图 + 轨迹标绘）。
   - 下框 = **当天景点图**（保持原比例 contain 居中，不拉伸；右上角带景点名标注）。

## 数据约定 / Data schema
数据放在旅行目录下的 `trip_data.py`，同时被 `gen_maps.py` 与 `gen_pptx_roadtrip.py` 共用。
Put data in `trip_data.py` inside your trip folder; shared by both scripts.

```python
import os
DECK_DIR = os.getcwd()
TRIP_TITLE = '阿里南线自驾环线'

# 地点经纬度 (WGS-84)。国内地图需 GCJ-02，gen_maps.py 内部自动转换。
NODE = {'拉萨': (91.13, 29.65), '羊湖(岗巴拉)': (90.70, 28.95), ...}
# 逐日路线：(day, 起点, [途经点...], 终点, 里程km)
DAYS = [(1, '拉萨', ['羊湖(岗巴拉)','卡若拉冰川','江孜'], '日喀则', '360'), ...]
# 图片路径函数（按你的素材命名调整）
def get_img(idx): return os.path.join(DECK_DIR,'images',f'landscape-{idx:02d}.jpg')
def get_spot(day): return os.path.join(DECK_DIR,'spot_photos',f'spot_{day}.png')
def get_map(day): return os.path.join(DECK_DIR,'maps',f'day_map_{day}.png')

# 页面序列 S：元素 (类型, 数据dict)。类型: cover/section/stats/day/tips/closing
S = [
  ('cover', {'img': get_img(1), 'word':'阿里南线', 'sub':'14天自驾环线', 'meta':'8.10–8.23'}),
  ('day', {'img': get_spot(1), 'bg': get_img(6), 'map': get_map(1),
           'day_label':'DAY 1 · 8.10', 'route':'拉萨 → 日喀则', 'km':'360', 'time':'6h',
           'highest_alt':'3836m',
           'trip':[...], 'intro':[...], 'caution':[...], 'stay':[...]}),
  ...
]
```
完整可运行模板见 `templates/roadtrip_data_template.py`（含阿里南线 14 天全量数据）。
Full runnable template: `templates/roadtrip_data_template.py` (Ali-Nan line 14-day sample).

## 图片管线 / Image pipeline
1. **背景 / 通用风光照 Background**：用户自备横版图（≥1920×1080），放 `images/`，cover 铺满。
2. **真实路线地图 Real route map**：`gen_maps.py` 下载高德卫星瓦片（style=6）+ 中文注记（style=8），
   按 WGS-84→GCJ-02 转换坐标，紧贴当天路线缩放（5% 边距），标绘起点/住宿点/途经点/指北针，输出 `maps/day_map_{day}.png`（1180×400）。
3. **当天景点图 Spot photo**：**优先 Pexels 精准实拍**（真实、可溯源）；仅当 Pexels 搜不到该景点对应图（尤其中国小众地标）时，才用 **ImageGen 工具**按精准地标提示词生成写实图（1536×1024），
   放 `spot_photos/spot_{day}.png`，**contain 原比例**嵌入下框（绝不拉伸压扁）。

## 生成命令 / Build
```bash
cd /path/to/your/trip        # 旅行目录（含 trip_data.py、images/、spot_photos/）
python <skill>/scripts/gen_maps.py            # 先：生成 maps/day_map_*.png（需联网）
python <skill>/scripts/gen_pptx_roadtrip.py   # 后：生成 <TRIP_TITLE>-roadtrip.pptx
```
- 若输出 PPTX 被用户打开导致 `PermissionError`，脚本自动换名输出（不阻塞）。
- 改行程只需改 `trip_data.py` 的对应 day dict，重新运行即可，无需改布局代码。

---

# 景点图鉴（主题网格）Spot Gallery (themed grid)

适用：在行程册之外，单独做一本「**所有景点图鉴**」——按主题分组（神山/圣湖/寺庙/遗址…），每组一页紧凑网格，每格一张景点实拍 + 景点名 + 到达日标签。常用作行程册的「看点清单 / 景点手册」附册。
For: a standalone "spot catalogue" of the whole trip — grouped by theme, one compact grid slide per group, each cell = one spot photo + name + arrival-day tag. Great as a "highlights / spot list" add-on to the itinerary deck.

## 数据约定 / Data schema
复制 `templates/spot_gallery_template.py` 到旅行目录，按真实景点填三个字段：
Copy `templates/spot_gallery_template.py` into your trip folder and fill three fields:

- `GROUPS`：`[(中文主题名, 英文副标, [景点中文名...]), ...]` —— 分组与每页景点。
- `SPOT_QUERIES`：`{景点中文名: (Pexels英文搜索词, [期望关键词...])}` —— 精准搜图 + alt 相关性打分；务必给小众地标精准英文（地名 + landmark 类型）。
- `DAYS`：`{景点中文名: 到达日(int)}` —— **可选**；提供后每个景点名旁显示「Day N」标签。

## 图片管线 / Image pipeline
1. **抓图（去重 + 二次核查）**：`scripts/fetch_spot_photos.py` 从 **Pexels** 按 `SPOT_QUERIES` 搜 landscape 图，alt 相关性打分挑最佳；
   - **全局去重**：photo id 与 md5 一旦被占用就顺延下一张，保证整套图鉴**无重复图**；
   - **感知哈希二次核查**：算每图 8×8 平均哈希，任意两图距离 ≤ 6 视为近似重复，对后者重抓并强制其与全场其他图距离 ≥ 10；
   - 写出 `spot_gallery/{景点名}.jpg` 与 `CREDITS.txt`（Pexels 署名，需随 deck 保留）；Pexels 搜不到的写 `spot_gallery/_fallback.txt`。
2. **缺图兜底**：`_fallback.txt` 里的小众地标（如古格遗址、札达土林）由 agent 用 **ImageGen 工具**按地标提示词生成写实图，放入同名 `spot_gallery/{景点名}.jpg`。
3. **排版**：深色背景 `BK=(11,14,20)` + **白强调**（橘色图标已改白）+ 微软雅黑；杂志式紧凑网格（gutter 0.12in），图片按单元格比例 **cover 裁切填满**（无白边），底部半透明黑条 + 白色小方块 + 白字可编辑名称 + `Day N` 标签。详见 `references/spot_gallery_layout.md`。

## 生成命令 / Build
```bash
cd /path/to/your/trip        # 旅行目录（含 spot_gallery_data.py）
python <skill>/scripts/fetch_spot_photos.py --data spot_gallery_data.py   # 先：抓图(去重+二次核查)
python <skill>/scripts/gen_spot_gallery.py  --data spot_gallery_data.py --out 景点图鉴.pptx  # 后：生成
```
- 若输出 PPTX 被用户打开导致 `PermissionError`，脚本自动换名输出（不阻塞）。
- 改景点只改数据模块，重新运行即可，无需动布局代码。

---

# 城市多日游（单栏）City Multi-day Tour (single column)

适用：城市游、多城串联，无逐日 GPS 路线。背景用 Pexels 精准实拍（非黑白）。
For city tours without per-day GPS routes. Background uses Pexels precise photos (not B/W).

## 数据约定 / Data schema
`templates/trip_data_template.py` 定义 `days` / `hotels` / `timeline` / `budget` / `photo_map` / `TRIP_TITLE` 等。

## 图片管线 / Image pipeline
1. **优先 Pexels 实拍**（需先配置 Pexels API Key，见上文「前置配置」）：`scripts/fetch_trip.py` 按精准英文关键词搜索，按 `alt` 相关性打分 + 排除错城词，自动挑最贴合图。
2. **Pexels 无精准图 → ImageGen 生成**：对中国小众地标用 ImageGen 定点生成（100% 贴合），再后处理统一风格。
3. **后处理**：所有图裁到 1920×1080，压暗 0.82 + 提饱和 1.05 + 提对比 1.06，**不要 duotone/灰度**（用户要求背景非黑白）。

## 生成命令 / Build
```bash
python scripts/gen_pptx.py <数据模块.py> <输出.pptx> [--photos ppt_assets/photos] [--budget 预算.xlsx] [--cover-slug cover]
```

---

## 排版规范 / Layout spec
权威坐标见 `references/roadtrip_layout.md`（自驾/户外环线）与 `references/spot_gallery_layout.md`（景点图鉴）。要点 / Key points:
- 画布 13.33×7.5 in；左列 x=0.8 宽 5.8；右列 x=6.9 宽 5.9。
- 右上双框（自驾/户外环线）：上框地图 (6.9,3.05,5.9,2.0)；下框景点图 (6.9,5.15,5.9,2.0) **contain 原比例**。
- 背景用 cover 铺满（按原比例缩放、溢出裁切），**绝不拉伸**。
- 景点图鉴：深色背景 `(11,14,20)` + 白强调 + 微软雅黑；紧凑网格（gutter 0.12in），图片 cover 裁切填满，每格底部半透明黑条 + 白字名称 + `Day N` 标签。

## 配色与字体 / Palette & fonts
- 自驾/户外环线：黑底 BK=(0,0,0)；白 W=(255,255,255)；次要灰 G=(167,167,167)；深灰 DG=(111,111,111)；浅正文 VL=(242,242,242)。强调色 ACCENT=(232,109,78) 橘（块标题、轨迹线、住宿星标）。地图轨迹橙 `#ff8c2e`、起点青 `#39d6ff`、途经橙 `#ffc078`。
- 景点图鉴：深色背景 BK=(11,14,20)；白 W=(255,255,255)；次要灰 SUB=(184,192,204)；白强调 ACCENT=(255,255,255)；细线 LINE=(42,49,62)。
- 字体：微软雅黑（地图中文 `C:/Windows/Fonts/msyh.ttc`，非 Windows 回退默认）。标题 34–84pt，正文 12–24pt。

## 校验（必做）/ Validate (required)
生成后遍历所有 shape，检查 `left+width ≤ slide_w+0.05in` 且 `top+height ≤ slide_h+0.05in`（越界即错位）；
并确认每日页景点图 `width/height ≈ 原图比例`（未被拉伸）。
After build, scan all shapes for overflow; confirm each daily spot image keeps its original aspect ratio (no stretch).

```python
from pptx import Presentation
p = Presentation(out); SW, SH = p.slide_width, p.slide_height
bad = 0
for s in p.slides:
    for sh in s.shapes:
        if None not in (sh.left, sh.top, sh.width, sh.height):
            if sh.left+sh.width > SW+45720 or sh.top+sh.height > SH+45720:
                bad += 1
print("越界 shape 数:", bad)
```

## 依赖 / Dependencies
- 自驾 / 户外环线：`python-pptx`、`Pillow`、`numpy`、`matplotlib`（生成地图需联网下载高德瓦片）。
- 城市多日游：`python-pptx`、`Pillow`、`openpyxl`（读预算表）、`requests`（Pexels）。
- 景点图鉴：`python-pptx`、`Pillow`、`requests`（Pexels 抓图 + 感知哈希去重）；`ImageGen` 工具用于小众地标兜底。
- managed python 缺包：`python -m pip install python-pptx Pillow numpy matplotlib openpyxl requests`。

## 经验沉淀 / Lessons learned
- 自驾/环线行程，**真实地图比手绘色块强得多**；高德瓦片国内直连免 key，但坐标是 GCJ-02，需把 GPS(WGS-84) 先转换。
  Real maps beat hand-drawn blocks; AMap tiles are key-free in CN but use GCJ-02 — convert WGS-84 first.
- 景点图务必 **contain 原比例**，否则横框会把竖图/方图压扁变形（常见返工点）。
  Always contain spot images at native ratio; stretching into a wide frame is a common rework cause.
- 背景图用 **cover 铺满**（按原比例缩放+裁切），比固定尺寸拉伸更专业。
  Use cover (scale+crop) for full-bleed backgrounds, never fixed-size stretch.
- 改行程只改数据模块（`trip_data.py` / `spot_gallery_data.py`），生成器自动重建，无需动布局代码。
  Edit only the data module to change itinerary; the generator rebuilds automatically.
- PPTX 被用户打开会锁文件导致 `PermissionError`，脚本自动换名即可，不要阻塞。
  An open PPTX locks the file; the script auto-renames output — never block on it.
