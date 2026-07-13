# 景点图鉴 · 网格排版规范（Spot Gallery Layout）
# Spot Gallery — Grid Layout Spec

> 本文件是 `scripts/gen_spot_gallery.py` 的版式权威说明，供复用 skill 时参考。
> Authoritative layout reference for `scripts/gen_spot_gallery.py`.

---

## 0. 适用场景 / When to use
把一趟行程里**所有景点**单独列成一页页「图鉴」：按主题分组（神山 / 圣湖 / 寺庙 / 遗址…），每组一页紧凑网格，每格一张景点实拍 + 景点名 + 到达日标签。适合做「行程看点清单 / 景点手册」附册。

List **all spots** of a trip as a compact gallery: grouped by theme, one slide per group, each cell = one spot photo + name + arrival-day tag. Good as a "trip highlights / spot catalogue" add-on.

---

## 1. 画布 Canvas
- 尺寸：16:9，13.33 in × 7.5 in。
- 深色背景 `BK=(11,14,20)`（接近纯黑，比行程册黑底 (0,0,0) 稍暖，更显高级）。
- 强调色用**白色**（用户要求去掉橘色）：标题下划线、右上「N 处」计数、每格小方块均为白 `(255,255,255)`。可改回橘 `(232,109,78)` 只需改 `ACCENT`。
- 字体：微软雅黑 `Microsoft YaHei`。

---

## 2. 单页网格 Grid per slide
顶部主题标题区 + 下方网格。

### 2.1 顶部标题 Title block
| 元素 | 位置 (in) | 样式 |
|------|-----------|------|
| 中文主题名 | (0.55, 0.30) 宽 9.5 | 26pt 白 粗 |
| 英文副标 | (0.58, 0.86) 宽 9.5 | 11pt 灰 `SUB=(184,192,204)` |
| 白色下划线 | (0.58, 0.80) 0.9×0.045 | 白实 fill |
| 右上计数「N 处」 | (11.3, 0.38) 宽 1.7 右对齐 | 13pt 白 粗 |

### 2.2 网格参数 Grid metrics
- 左边距 `L=0.55`、右边距 `Rm=0.55`、网格顶 `T=1.30`、网格底 `B=0.30`。
- 列数 `cols`：景点数 ≥ 8 → 4 列；否则 3 列。
- 行数 `rows = ceil(n/cols)`。
- **单元间距 gutter = 0.12 in（极小，杂志式紧凑）**。
- 单元宽 `cell_w = (grid_w - gut*(cols-1))/cols`；单元高 `cell_h = (grid_h - gut*(rows-1))/rows`；`grid_w = 13.333 - L - Rm`，`grid_h = 7.5 - T - B`。
- 目标裁切比例 `target_ratio = cell_w / cell_h`。

### 2.3 单元内容 Cell content
每格依次叠加（z 顺序从下到上）：
1. **景点图**：用 PIL 按 `target_ratio` 做 **cover 裁切**（按原比例缩放、溢出居中裁切，绝不拉伸），填满整格。
2. **细边框**：0.75pt 灰线 `LINE=(42,49,62)`，无填充。
3. **底部半透明黑条**：高 0.34 in，置于单元底部，`a:alpha` 不透明度约 58%。
4. **白色小方块图标**：(cx+0.10, sy+strip_h/2-0.055, 0.06×0.11)，白 fill —— 即「橘色图标改白」后的标记。
5. **文字（可编辑）**：在黑条上，`(cx+0.22, sy, cell_w-0.28, 0.34)`，垂直居中：
   - 先一个浅灰小 run：`Day N  `（9pt，`SUB` 色，非粗）——到达日标签；
   - 再一个白粗 run：景点中文名（≤6 字 12pt，否则 10.5pt，白 粗）。

> 到达日 `N` 来自数据模块的 `DAYS = {景点名: int}`；某景点未提供 `DAYS` 则不显示日期标签。

---

## 3. 配色与字体 Palette & Fonts
- 背景 `BK=(11,14,20)`；占位面板 `PANEL=(21,26,34)`（图缺失时显示，避免崩）。
- 白 `W=(255,255,255)`；次要灰 `SUB=(184,192,204)`；细线 `LINE=(42,49,62)`；强调（白）。
- 字体：微软雅黑。标题 26pt，计数 13pt，景点名 10.5–12pt，日期标签 9pt。

---

## 4. 图片管线 Image pipeline（见 `scripts/fetch_spot_photos.py`）
1. 每个景点按 `SPOT_QUERIES` 的精准英文词从 **Pexels** 搜索（landscape，多页）。
2. 按 Pexels `alt` 描述做关键词相关性打分，挑最佳；同时做**全局去重**：photo id 与 md5 一旦被占用就顺延下一张，保证整套图鉴无重复图。
3. **二次核查（感知哈希）**：算每图 8×8 平均哈希，任意两图距离 ≤ 6 视为近似重复，对后者重抓并强制其与全场其他图距离 ≥ 10；仍不行则写入 `spot_gallery/_fallback.txt`，由 agent 用 ImageGen 兜底。
4. 写出 `spot_gallery/{景点名}.jpg` 与 `CREDITS.txt`（Pexels 署名，需随 deck 保留）。
5. 缺图兜底：Pexels 搜不到的小众地标（如古格遗址、札达土林），写 `_fallback.txt`，agent 用 ImageGen 按地标提示词生成写实图后放入同名 jpg。

---

## 5. 校验 Checklist（生成后必做）
- 越界：遍历所有 shape，`left+width ≤ slide_w + 0.05in` 且 `top+height ≤ slide_h + 0.05in`。
- 无重复图：对 `spot_gallery/*.jpg` 算 md5 + 平均哈希，应「0 完全相同、0 感知相近(diff≤6)」——本 skill 抓取阶段已强制去重，此处复核即可。
- 每个景点都有对应图（无占位黑框）或已在 `_fallback.txt` 登记。

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
