# 自驾 / 户外环线 · 每日行程排版规范（Roadtrip Layout）
# Roadtrip / Outdoor Loop — Daily Itinerary Layout Spec

> 本文件是 `gen_pptx_roadtrip.py` 的版式权威说明，供复用 skill 时参考。
> This file is the authoritative layout reference for `gen_pptx_roadtrip.py`.

---

## 0. 画布 Canvas
- 尺寸 / Size：16:9，宽 13.33 in × 高 7.5 in（标准宽屏）。
- 单位 / Units：下文坐标均为英寸 (in)；代码用 `Inches()`。
- 安全边距 / Safe margin：文字左列从 x=0.8 in 起，避免贴边。

---

## 1. 每日行程页 Daily Page（核心）
Each day = one slide，版式四区 / four zones：

```
┌───────────────────────────────────────────────────────────┐
│ DAY 1 · 8.10          (0.8,0.45) 14pt 灰                  │
│ 拉萨 → 日喀则          (0.8,0.82) 38pt 白 标题            │
│ 里程 360km  时长 6h  最高海拔 3836m   (0.8,1.95) 数据条   │
│                                                           │
│ ▸行程说明                 ┌────────────────────────────┐   │
│  ...三条...               │  上框：真实路线地图         │   │
│ ▸经典介绍                 │  (6.9,3.05) 5.9×2.0        │   │
│  ...三条...               ├────────────────────────────┤   │
│ ▸注意事项                 │  下框：今日景点图(原比例)   │   │
│  ...                      │  (6.9,5.15) 5.9×2.0        │   │
│ ▸住宿点                   │  [景点名标注 右上角]        │   │
│  ...                      └────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
   左列 x=0.8, 宽 5.8          右列 x=6.9, 宽 5.9
```

### 1.1 全幅背景 Background（cover）
- 用通用风光照铺满整页，再叠半透明黑层（intensity=0.62，越不透明越暗）。
- **cover 逻辑**：按图片原始比例缩放，使短边铺满画布，长边居中裁切（横图裁左右、竖图裁上下）。**绝不拉伸变形**。
- 公式：若 iw/ih ≥ 13.33/7.5 → 高铺满、宽溢出裁切；否则宽铺满、高溢出裁切。

### 1.2 顶部标题区 Title block
| 元素 | 位置 (in) | 尺寸 | 颜色 |
|------|-----------|------|------|
| 日期标签 day_label | (0.8, 0.45) | 14pt 灰 | DG |
| 路线 route | (0.8, 0.82) | 38pt 白 粗 | W |
| 数据条标签 | (0.8, 1.95) / +2.2 步进 | 11pt 灰 | DG |
| 数据条数值 | (0.8, 2.28) | 24pt 白 粗 | W |

数据条三项：里程 DISTANCE / 时长 TIME / 最高海拔 ALT，x 步进 2.2 in。

### 1.3 左列四块 Left column（4 blocks）
- 列 x=0.8，宽 lw=5.8 in。
- 每块：标题（16pt 强调色 ACCENT）+ 多行正文（12.5pt 浅色 VL）。
- 四块 Y 坐标与行高：
  - 行程说明 (0.8, 3.05)，行高 step=0.21
  - 经典介绍 (0.8, 4.30)
  - 注意事项 (0.8, 5.50)
  - 住宿点 (0.8, 6.55)
- 每块标题用 `▸` 前缀，正文过密时下调 fs 到 12。

### 1.4 右上双框 Right-top two frames
- **上框 = 真实路线地图**：(x=6.9, y=3.05, w=5.9, h=2.0)。
- **下框 = 今日景点图**：(x=6.9, y=5.15, w=5.9, h=2.0)。
- 两框等宽等高，竖向堆叠，间距 0.1 in。

### 1.5 景点图原比例（关键，避免压扁）
- 框比例 5.9:2.0 ≈ 2.95:1；多数实拍图比例不同。
- **contain 逻辑**：`scale = min(box_w/iw, box_h/ih)`，按原比例完整显示，居中于框内。
- 留白区域先铺半透明深底（_set_alpha 0.55），再放图片，避免露出背景照。
- 图片外描边 0.75pt 灰线。

### 1.6 景点名标注 Spot label
- 取当天 `intro[0]` 第一个景点名（去冒号/括号），置于**景点图右上角**。
- 标签框 (dx+dw-2.7, dy+0.10, 2.7×0.42)，半透明黑底、白字右对齐 12pt。

---

## 2. 其他页型 Other slide types
| 类型 | 内容 | 关键坐标 |
|------|------|----------|
| cover | 大标题 84pt 居中 + 副标 28pt + 元信息 18pt | 标题 (1,2.8)，meta (1,5.0) |
| section | 大区分隔：标签 + 64pt 标题 + 22pt 描述 | 标题 (0.8,2.5)，body (0.8,4.2) |
| stats | 3 个大数字 72pt + 标签 18pt | y 从 1.6 步进 1.7 |
| tips | 列表项 20pt，最多约 8 条 | y 从 1.8 步进 0.55 |
| closing | 72pt 居中标题 + 24pt 副标 | 标题 (2,3.0)，sub (2,4.5) |

所有非每日页同样用 `add_bg` 铺满背景 + 暗化层（intensity 0.45–0.7）。

---

## 3. 配色与字体 Palette & Fonts
- 背景黑 BK=(0,0,0)；正文白 W=(255,255,255)；次要灰 G=(167,167,167)；深灰 DG=(111,111,111)；浅色正文 VL=(242,242,242)。
- 强调色 ACCENT=(232,109,78) 橘（用于块标题、轨迹线、住宿星标）。
- 字体：微软雅黑 `Microsoft YaHei`（地图中文注记用 `C:/Windows/Fonts/msyh.ttc`；非 Windows 回退默认字体）。
- 标题 34–84pt，正文 12–24pt。

---

## 4. 图片管线 Image pipeline
1. **背景/通用风光照**：用户自备横版图（建议 ≥1920×1080），放 `images/`；cover 铺满。
2. **真实路线地图**：`gen_maps.py` 用高德卫星瓦片（GCJ-02，脚本内部 WGS84→GCJ02 转换）+ 中文注记，紧贴当天路线缩放，输出 `maps/day_map_{day}.png`（1180×400）。
3. **今日景点图**：优先精准实拍（Pexels/自备）；对中国小众地标用 ImageGen 按精准地标提示词生成写实图（1536×1024），放 `spot_photos/spot_{day}.png`，contain 原比例嵌入下框。

---

## 5. 校验 Checklist（生成后必做）
- 越界：遍历所有 shape，`left+width ≤ slide_w + 0.05in` 且 `top+height ≤ slide_h + 0.05in`。
- 景点图比例：`width/height ≈ 原图比例`，确认未被拉伸（contain）。
- 地图/景点图存在：`os.path.exists` 为真，否则为黑框（容错不崩）。
- 每日页数 = DAYS 天数；总页数 = len(S)。

```python
from pptx import Presentation
from pptx.util import Emu
p = Presentation(out); SW, SH = p.slide_width, p.slide_height
bad = 0
for s in p.slides:
    for sh in s.shapes:
        if None not in (sh.left, sh.top, sh.width, sh.height):
            if sh.left+sh.width > SW+45720 or sh.top+sh.height > SH+45720:
                bad += 1
print("越界 shape 数:", bad)
```
