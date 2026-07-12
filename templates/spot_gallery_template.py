# -*- coding: utf-8 -*-
# 景点图鉴数据模板 / Spot Gallery data template (模式 C)
#
# 复制本文件到你的旅行目录，按真实行程修改后：
#   python <skill>/scripts/fetch_spot_photos.py --data spot_gallery_data.py   # 抓图(全局去重+二次核查)
#   python <skill>/scripts/gen_spot_gallery.py  --data spot_gallery_data.py --out 景点图鉴.pptx
#
# 字段 / Fields:
#   GROUPS       : [(中文主题名, 英文副标, [景点中文名...]), ...]  分组与每页景点
#   SPOT_QUERIES : {景点中文名: (Pexels英文搜索词, [期望关键词...])}  精准搜图 + alt 打分
#   DAYS         : {景点中文名: 到达日(int)}                         可选，景点名旁的「Day N」标签
#
# 下方为「西藏南线 14 天自驾环线」示例数据（与 examples/ 图鉴一致）。

TRIP_TITLE = '西藏南线 · 景点图鉴'

GROUPS = [
    ('神山 · 雪山', 'SACRED MOUNTAINS', [
        '冈仁波齐', '珠穆朗玛峰', '希夏邦马峰', '念青唐古拉山主峰',
        '琼姆岗嘎雪山', '加乌拉山口', '岗巴拉山口', '雪格拉山口', '卡若拉冰川']),
    ('圣湖 · 湖泊', 'HOLY LAKES', [
        '羊卓雍错', '玛旁雍错', '拉昂错', '佩枯措',
        '公珠措', '纳木错', '圣象天门', '月亮湾']),
    ('寺庙 · 人文', 'TEMPLES & CULTURE', [
        '扎什伦布寺', '科迦寺', '托林寺', '绒布寺', '扎西寺', '布达拉宫',
        '大昭寺', '色拉寺', '江孜宗山古堡', '西藏博物馆', '八廓街', '药王山观景台']),
    ('遗址 · 风貌', 'RUINS & LANDSCAPES', [
        '古格王朝遗址', '札达土林', '霞义沟', '羊八井温泉', '仲巴草原沙丘', '雅江上游湿地']),
]

# 各景点到达日（依据行程 D1-D14 映射，取首次到达/重点游览日）
DAYS = {
    '冈仁波齐': 4, '珠穆朗玛峰': 2, '希夏邦马峰': 3, '念青唐古拉山主峰': 12,
    '琼姆岗嘎雪山': 10, '加乌拉山口': 2, '岗巴拉山口': 1, '雪格拉山口': 10, '卡若拉冰川': 1,
    '羊卓雍错': 1, '玛旁雍错': 4, '拉昂错': 4, '佩枯措': 3,
    '公珠措': 4, '纳木错': 10, '圣象天门': 11, '月亮湾': 11,
    '扎什伦布寺': 2, '科迦寺': 5, '托林寺': 7, '绒布寺': 2, '扎西寺': 10, '布达拉宫': 13,
    '大昭寺': 13, '色拉寺': 14, '江孜宗山古堡': 1, '西藏博物馆': 14, '八廓街': 13, '药王山观景台': 13,
    '古格王朝遗址': 6, '札达土林': 6, '霞义沟': 7, '羊八井温泉': 12, '仲巴草原沙丘': 8, '雅江上游湿地': 8,
}

# Pexels 精准搜索词 + 期望关键词（用于 alt 相关性打分挑最贴合图）
SPOT_QUERIES = {
    '冈仁波齐': ('Mount Kailash sacred mountain Tibet', ['kailash', 'mountain', 'tibet']),
    '珠穆朗玛峰': ('Mount Everest snow peak summit', ['everest', 'peak', 'summit', 'snow', 'mountain']),
    '希夏邦马峰': ('Shishapangma peak Himalaya snow Tibet', ['shishapangma', 'peak', 'himalaya', 'snow']),
    '念青唐古拉山主峰': ('Nyenchen Tanglha snow mountain range Tibet', ['nyenchen', 'tanglha', 'mountain', 'snow']),
    '琼姆岗嘎雪山': ('Chomolhari snow mountain border Tibet Bhutan', ['chomolhari', 'snow', 'mountain']),
    '加乌拉山口': ('Gambo Utse mountain pass viewpoint five 8000m peaks Tibet', ['pass', 'viewpoint', 'mountain']),
    '岗巴拉山口': ('Gambala mountain pass road viewpoint Yamdrok Tibet', ['gambala', 'pass', 'road', 'viewpoint']),
    '雪格拉山口': ('Snow Gra mountain pass S304 Tibet', ['pass', 'snow', 'mountain']),
    '卡若拉冰川': ('Karola Glacier Tibet roadside ice', ['karola', 'glacier', 'ice', 'tibet']),
    '羊卓雍错': ('Yamdrok Lake turquoise blue Tibet', ['yamdrok', 'lake', 'tibet', 'turquoise']),
    '玛旁雍错': ('Manasarovar Lake Tibet sacred', ['manasarovar', 'lake', 'tibet', 'sacred']),
    '拉昂错': ('Lhanag Tso Rakshas Tal lake Tibet', ['lhanag', 'lake', 'tibet', 'rakshas']),
    '佩枯措': ('Peiku Tso lake Himalaya Tibet', ['peiku', 'lake', 'tibet', 'himalaya']),
    '公珠措': ('Gongzhu Tso lake Tibet plateau', ['gongzhu', 'lake', 'tibet', 'plateau']),
    '纳木错': ('Namtso Lake Tibet blue plateau', ['namtso', 'lake', 'tibet', 'plateau']),
    '圣象天门': ('Namtso Heavenly Gate natural stone arch Tibet', ['namtso', 'stone', 'arch', 'gate', 'tibet']),
    '月亮湾': ('Namtso Moon Bay lake bend Tibet', ['moon', 'bay', 'lake', 'bend', 'tibet']),
    '扎什伦布寺': ('Tashilhunpo Monastery Shigatse Tibet', ['tashilhunpo', 'monastery', 'shigatse', 'tibet']),
    '科迦寺': ('Kojar Monastery Purang Tibet temple', ['kojar', 'monastery', 'purang', 'temple']),
    '托林寺': ('Tholing Monastery Zanda Tibet', ['tholing', 'monastery', 'zanda', 'tibet']),
    '绒布寺': ('Rongbuk Monastery Everest base camp Tibet', ['rongbuk', 'monastery', 'everest', 'tibet']),
    '扎西寺': ('Tashi Gompa monastery prayer flags Tibet', ['tashi', 'monastery', 'prayer', 'flags', 'tibet']),
    '布达拉宫': ('Potala Palace Lhasa Tibet', ['potala', 'palace', 'lhasa', 'tibet']),
    '大昭寺': ('Jokhang Temple Lhasa Tibet', ['jokhang', 'temple', 'lhasa', 'tibet']),
    '色拉寺': ('Sera Monastery monks debate Lhasa Tibet', ['sera', 'monastery', 'monks', 'lhasa', 'tibet']),
    '江孜宗山古堡': ('Gyantse Dzong fortress Tibet', ['gyantse', 'dzong', 'fortress', 'tibet']),
    '西藏博物馆': ('Tibet Museum Lhasa building', ['tibet', 'museum', 'lhasa', 'building']),
    '八廓街': ('Barkhor Street Lhasa Tibet', ['barkhor', 'street', 'lhasa', 'tibet']),
    '药王山观景台': ('Chakpori viewpoint Potala Palace Lhasa', ['chakpori', 'potala', 'lhasa', 'viewpoint']),
    '古格王朝遗址': ('Guge Kingdom ruins cliff palace Zanda Tibet', ['guge', 'ruins', 'cliff', 'zanda', 'tibet']),
    '札达土林': ('Zanda earth forest clay canyon Tibet', ['zanda', 'earth', 'forest', 'clay', 'canyon', 'tibet']),
    '霞义沟': ('Xiagou Zanda Earth Forest canyon Tibet', ['xiagou', 'canyon', 'earth', 'tibet']),
    '羊八井温泉': ('Yangbajing hot spring geothermal Tibet', ['yangbajing', 'hot', 'spring', 'geothermal', 'tibet']),
    '仲巴草原沙丘': ('Zhongba sand dunes grassland Tibet plateau', ['zhongba', 'sand', 'dunes', 'grassland', 'tibet']),
    '雅江上游湿地': ('Yarlung Tsangpo river wetland Tibet', ['yarlung', 'river', 'wetland', 'tibet']),
}
