# 29 天川藏大环线自驾 PPT 模板

本模板是一套**完整可复用的 29 天长途环线行程 PPT 生成器**示例，基于本 skill 的「自驾/户外环线（双框排版）」版式，已沉淀成都 → G318 川藏南线（含稻城亚丁支线）→ 拉萨 → 西藏南线 14 天环线 → G317 川藏北线 → 成都 的真实数据。

> 它展示的是「整体工作流」：数据建模 → 离线/真实背景 → 真实路线地图 → 每日双框页 → 景点图鉴，29 天 / 约 6200 km 一站式产出。

## 文件角色

| 文件 | 作用 |
| --- | --- |
| `trip_data.py` | 全部行程数据：NODE 坐标(WGS-84)、DAYS 逐日路线、DAY_SPOT 主景点、S 页面序列、GALLERY 景点图鉴（43 处，Day 1–22）。`DATE_BASE` 控制出发日，自动推算每日日期。 |
| `gen_29day.py` | 主生成器：全幅背景 + 右上地图/景点图双框 + 左列四块文字；内建 `build_gallery`（4×3 网格、43 处、含名称+Day 标签）。ACCENT 强调色为纯白。 |
| `gen_maps.py` | 真实路线地图：高德瓦片联网生成 `maps/day_map_1..29.png`（带重试/超时/降并发以应对代理抖动）。 |
| `gen_assets.py` | 离线生成 12 张深色渐变背景 + 当日景点卡片（Pexels 不可用时兜底）。 |
| `gen_scenic.py` | 生成川藏段雪山剪影背景（无实拍时的兜底底图）。 |
| `crop_watermark.py` | 批量裁掉 AI 生成图底部水印（右侧「图片由AI生成」）。 |

## 运行

```bash
pip install pillow python-pptx
python gen_maps.py        # 生成真实路线地图（需联网取高德瓦片）
python gen_assets.py      # 生成离线渐变背景/景点卡片（可选）
python gen_29day.py       # 生成最终 deck：<DECK_DIR>/成都—拉萨—川藏大环线-vN.pptx
```

## 图片资源（不随仓库提交，需自行准备）

仓库只含代码与数据，**不含大体积图片**。运行前请准备：

1. **川藏段背景 / Day1–8、Day23–29 图鉴**：用 ImageGen（或 Pexels）生成写实风光照，放入 `images/route/`，命名 `scenic_cover.png`、`scenic_d1.png` … `scenic_d29.png`（Day4 复用 Day3）。生成后跑 `python crop_watermark.py` 去水印。
2. **西藏段真实照（Day9–22 背景 + 图鉴）**：设置环境变量 `TIBET_PHOTO_DIR` 指向含 35 张真景照（`<景点名>.jpg`）的目录，脚本会自动按 `GALLERY` 名称匹配；缺图时回退到通用渐变底图。也可用 skill 的 `scripts/fetch_spot_photos.py` 从 Pexels 抓取。

## 关键点

- 日期默认 `DATE_BASE = 2026-08-10`，Day 1 = 8.10 … Day 29 = 9.07，改 `trip_data.py` 顶部即可。
- 景点图鉴 `GALLERY` 为 `(名称, 绝对Day, 图片路径)` 三元组：Day1–8 用 `ROUTE_BG` 的 AI 图，Day9–22 用真实照。
- 强调色统一为纯白 `(255,255,255)`，契合全黑/深底视觉。
