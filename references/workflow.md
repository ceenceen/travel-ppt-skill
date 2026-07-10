# travel-ppt 工作流参考

## 端到端步骤
1. **准备数据模块**：复制 `templates/trip_data_template.py`，按真实行程填写 `days`（每天一页）、`hotels`、`timeline`、`budget`。
2. **准备图片**：在 `ppt_assets/photos/` 放每个城市的 `slug.jpg`（1920×1080，彩色）。
   - 有精准实拍 → `python scripts/fetch_trip.py --map '{"beijing":["Forbidden City Beijing palace"]}' --out ppt_assets/photos`
   - 无精准实拍（Pexels 搜出来是别的城市）→ 用 **ImageGen 工具**按地标提示词生成，再 `python scripts/postprocess.py`（或直接用 fetch_trip 的 postprocess 逻辑）统一压暗+裁切。
3. **生成 PPTX**：`python scripts/gen_pptx.py 数据.py 输出.pptx --photos ppt_assets/photos [--budget 预算.xlsx]`
4. **校验**：越界检查 + 无橘色（见 SKILL.md 校验段）。

## ImageGen 地标提示词要点（Pexels 缺图时）
- 哈尔滨圣索菲亚大教堂：`Saint Sophia Cathedral in Harbin China, Russian Byzantine Orthodox church, green onion domes, overcast cinematic`
- 沈阳故宫：`Shenyang Imperial Palace Mukden Palace, red walls golden glazed roofs, courtyard`
- 丹东鸭绿江断桥：`Yalu River Broken Bridge Dandong China, rusty steel railway bridge, China-North Korea border`
- 泰山：`Mount Tai Shandong China, stone stairways, sea of clouds at sunrise, ancient temple`
- 趵突泉：`Baotu Spring Jinan China, clear bubbling spring, traditional pavilions, willow trees`
- 风格统一：都加 `overcast moody cinematic sky, photorealistic, slightly desaturated, dramatic soft light`，生成后过压暗+裁切即可融入整本。

## 常见坑
- **预算页溢出**：读 xlsx 只收「带 % 占比」的明细行，过滤"人均/建议区间/单人估算"等汇总行（会混入脏数据导致整页向下溢出）。
- **文件被占用**：输出 PPTX 被用户打开时写不进，换文件名输出即可。
- **城市→图映射**：`day_photo` 取 `city_html` 首 chip；含"长城"关键词当天用 `cover`（长城图）。若某城图不对，在数据模块 `photo_map` 覆盖。
- **当前模型不支持读图**：用 Pexels `alt` 字段程序化核对 + 精准 photo-ID/提示词定点抓取；交付时附 AI 图缩略图供用户肉眼确认。
