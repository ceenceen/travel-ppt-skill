import os
from PIL import Image

# 去掉 AI 生成图右下角的“图片由AI生成”水印：批量裁掉底部 70px。
# 用法：把 AI 生成的路线/景点图放到 <deck>/images/route/ 后，python crop_watermark.py
route_dir = os.path.join(os.getcwd(), 'images', 'route')

for fn in sorted(os.listdir(route_dir)):
    if not fn.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue
    path = os.path.join(route_dir, fn)
    with Image.open(path) as im:
        w, h = im.size
        # crop bottom 70px to remove AI watermark
        crop_h = min(70, h // 10)
        cropped = im.crop((0, 0, w, h - crop_h))
        cropped.save(path, quality=95 if im.mode == 'RGB' else None)
        print(f'{fn}: {w}x{h} -> {w}x{h - crop_h}')

print('done')
