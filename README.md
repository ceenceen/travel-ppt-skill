# travel-ppt

> 把结构化行程数据渲染成 **16:9 可编辑 PPTX** 的 WorkBuddy skill。
> Render a **structured itinerary** into an editable 16:9 PPTX — a WorkBuddy skill.

支持两种模式 / Two modes included:

- **模式 A · 城市多日游 (City Multi-day Tour)**：Pexels 精准实拍作背景，单栏排版。
- **模式 B · 自驾 / 户外环线 (Roadtrip / Outdoor Loop)**：全幅背景 + 右上**真实路线地图**（高德卫星瓦片）+ 右下**当天景点图（原比例）** + 左列四块文字。

---

## 目录 / Table of Contents

- [中文说明](#中文说明)
  - [功能特性](#功能特性)
  - [仓库结构](#仓库结构)
  - [快速开始 · 模式 B（自驾环线）](#快速开始--模式-b自驾环线)
  - [快速开始 · 模式 A（城市游）](#快速开始--模式-a城市游)
  - [排版规范](#排版规范)
  - [依赖](#依赖)
- [English](#english)
  - [Features](#features)
  - [Repository structure](#repository-structure)
  - [Quick start · Mode B (Roadtrip)](#quick-start--mode-b-roadtrip)
  - [Quick start · Mode A (City tour)](#quick-start--mode-a-city-tour)
  - [Layout spec](#layout-spec)
  - [Dependencies](#dependencies)
- [许可证 / License](#许可证--license)

---

## 中文说明

### 功能特性

- **双模式**：城市游（无 GPS 路线）与自驾/环线（有逐日 GPS 路线）各一套生成管线。
- **真实地图**：模式 B 用高德卫星瓦片（国内直连、免 API key）生成真实路线地图，自动做 WGS-84 → GCJ-02 坐标转换，紧贴当天路线缩放并标绘轨迹。
- **原比例景点图**：景点图以 `contain` 原比例居中嵌入，**绝不拉伸压扁**。
- **可编辑输出**：python-pptx 生成，所有文字/图片后续可在 PowerPoint 直接改。
- **自动防锁**：PPTX 被打开导致写入失败时，脚本自动换名输出，不阻塞流程。

### 仓库结构

```
travel-ppt-skill/
├── SKILL.md                       # 中英双语 skill 说明（含触发词、数据 schema、排版规范）
├── README.md                      # 本文档
├── scripts/
│   ├── gen_pptx.py                # 模式 A：城市多日游 PPTX 生成器
│   ├── fetch_trip.py              # 模式 A：按关键词从 Pexels 拉取精准实拍
│   ├── make_routes.py             # 模式 A：路线辅助
│   ├── gen_maps.py                # 模式 B：真实路线地图生成器（高德瓦片）
│   └── gen_pptx_roadtrip.py       # 模式 B：每日双框排版 PPTX 生成器
├── templates/
│   ├── trip_data_template.py      # 模式 A 数据模板
│   └── roadtrip_data_template.py  # 模式 B 数据模板（含阿里南线 14 天全量示例）
└── references/
    └── roadtrip_layout.md         # 模式 B 权威排版规格（坐标 / 配色 / 字体）
```

### 快速开始 · 模式 B（自驾环线）

1. **准备数据**：在你的旅行目录（如 `alida-deck/`）放一份 `trip_data.py`，定义 `NODE`（地点经纬度，WGS-84）、`DAYS`（逐日路线）、`get_img / get_spot / get_map`（图片路径函数）与页面序列 `S`。可直接复制 `templates/roadtrip_data_template.py` 改。
2. **生成地图**：
   ```bash
   cd /path/to/your/trip
   python <skill>/scripts/gen_maps.py        # 输出 maps/day_map_{day}.png（需联网）
   ```
3. **生成 PPTX**：
   ```bash
   python <skill>/scripts/gen_pptx_roadtrip.py  # 输出 <TRIP_TITLE>-roadtrip.pptx
   ```
4. **改行程**：只改 `trip_data.py` 对应 day dict，重跑即可，无需动布局代码。

> 景点图：优先精准实拍（Pexels / 自备）；小众地标可用 ImageGen 工具按地标提示词生成写实图（1536×1024），放入 `spot_photos/spot_{day}.png`。

### 快速开始 · 模式 A（城市游）

```bash
python <skill>/scripts/gen_pptx.py <数据模块.py> <输出.pptx> \
    [--photos ppt_assets/photos] [--budget 预算.xlsx] [--cover-slug cover]
```

背景图由 `fetch_trip.py` 按精准英文关键词从 Pexels 拉取，Pexels 无图时回退 ImageGen 生成；统一裁到 1920×1080 并轻度压暗/提饱和，**保持非黑白**。

### 排版规范

权威坐标见 `references/roadtrip_layout.md`（模式 B）。要点：

- 画布 13.33 × 7.5 in；左列 x=0.8 宽 5.8；右列 x=6.9 宽 5.9。
- 右上双框：上框地图 `(6.9, 3.05, 5.9, 2.0)`；下框景点图 `(6.9, 5.15, 5.9, 2.0)` **contain 原比例**。
- 背景用 **cover 铺满**（按原比例缩放 + 居中裁切），绝不固定尺寸拉伸。
- 配色：黑底、白字、橘色强调 `(232,109,78)`；字体微软雅黑。

生成后建议用 `SKILL.md` 末尾的校验脚本扫描越界 shape，并确认景点图比例未被拉伸。

### 依赖

- 模式 B：`python-pptx`、`Pillow`、`numpy`、`matplotlib`（生成地图需联网）。
- 模式 A：`python-pptx`、`Pillow`、`openpyxl`、`requests`（Pexels）。
- 安装：`python -m pip install python-pptx Pillow numpy matplotlib openpyxl requests`

---

## English

### Features

- **Two modes**: City tour (no GPS route) and Roadtrip / outdoor loop (day-by-day GPS route), each with its own pipeline.
- **Real maps**: Mode B renders real route maps from AMap satellite tiles (direct in CN, no API key), auto-converts WGS-84 → GCJ-02, zooms tightly to the day's route and overlays the trajectory.
- **Native-ratio spot photos**: Spot images are embedded with `contain` at native aspect ratio — **never stretched**.
- **Editable output**: Built with python-pptx; all text/images remain editable in PowerPoint.
- **Lock-safe**: If the PPTX is open (write lock), the script auto-renames the output instead of blocking.

### Repository structure

```
travel-ppt-skill/
├── SKILL.md                       # Bilingual skill doc (triggers, data schema, layout spec)
├── README.md                      # This document
├── scripts/
│   ├── gen_pptx.py                # Mode A: city tour PPTX generator
│   ├── fetch_trip.py              # Mode A: pull precise photos from Pexels by keyword
│   ├── make_routes.py             # Mode A: route helper
│   ├── gen_maps.py                # Mode B: real route map generator (AMap tiles)
│   └── gen_pptx_roadtrip.py       # Mode B: daily dual-frame PPTX generator
├── templates/
│   ├── trip_data_template.py      # Mode A data template
│   └── roadtrip_data_template.py  # Mode B data template (full Ali-Nan 14-day sample)
└── references/
    └── roadtrip_layout.md         # Mode B authoritative layout spec (coords / palette / fonts)
```

### Quick start · Mode B (Roadtrip)

1. **Prepare data**: In your trip folder (e.g. `alida-deck/`), add a `trip_data.py` defining `NODE` (place lon/lat, WGS-84), `DAYS` (per-day route), `get_img / get_spot / get_map` (image path helpers) and the slide sequence `S`. Copy `templates/roadtrip_data_template.py` as a starting point.
2. **Generate maps**:
   ```bash
   cd /path/to/your/trip
   python <skill>/scripts/gen_maps.py        # writes maps/day_map_{day}.png (needs network)
   ```
3. **Generate PPTX**:
   ```bash
   python <skill>/scripts/gen_pptx_roadtrip.py  # writes <TRIP_TITLE>-roadtrip.pptx
   ```
4. **Edit itinerary**: Change only the relevant day dict in `trip_data.py` and re-run — no layout code changes needed.

> Spot photos: prefer precise shots (Pexels / your own); for obscure landmarks use the ImageGen tool with a landmark-specific prompt (1536×1024) into `spot_photos/spot_{day}.png`.

### Quick start · Mode A (City tour)

```bash
python <skill>/scripts/gen_pptx.py <data_module.py> <output.pptx> \
    [--photos ppt_assets/photos] [--budget budget.xlsx] [--cover-slug cover]
```

Background photos are fetched from Pexels by precise English keywords via `fetch_trip.py`; falls back to ImageGen when Pexels has none. All images are cropped to 1920×1080 with light dimming/saturation — **kept in color, not B/W**.

### Layout spec

Authoritative coordinates are in `references/roadtrip_layout.md` (Mode B). Key points:

- Canvas 13.33 × 7.5 in; left column x=0.8 width 5.8; right column x=6.9 width 5.9.
- Right-top two frames: top = map `(6.9, 3.05, 5.9, 2.0)`; bottom = spot photo `(6.9, 5.15, 5.9, 2.0)` **contain at native ratio**.
- Background uses **cover** (scale + center crop), never fixed-size stretch.
- Palette: black background, white text, orange accent `(232,109,78)`; font Microsoft YaHei.

After building, scan for overflowing shapes with the validation snippet at the end of `SKILL.md`, and confirm spot images keep their aspect ratio.

### Dependencies

- Mode B: `python-pptx`, `Pillow`, `numpy`, `matplotlib` (map gen needs network).
- Mode A: `python-pptx`, `Pillow`, `openpyxl`, `requests` (Pexels).
- Install: `python -m pip install python-pptx Pillow numpy matplotlib openpyxl requests`

---

## 许可证 / License

MIT — 可自由用于个人与商业行程册制作。
MIT — free for personal and commercial itinerary decks.
