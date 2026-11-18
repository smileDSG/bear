import os, base64, io
from PIL import Image

base = r'E:\03_Projects\bear\study-room\sketch'
bears = r'E:\03_Projects\bear\study-room\public\bears'

with open(os.path.join(base, '草图.html'), encoding='utf-8') as f:
    html = f.read()

emos = ['natural', 'serious', 'happy', 'helpless', 'confused']
img_map = {}
for e in emos:
    p = os.path.join(bears, 'xiaolin-' + e + '.png')
    img = Image.open(p).convert('RGBA')
    img.thumbnail((640, 640), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    data = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    img_map[e] = data
    html = html.replace('src="xiaolin-' + e + '.png"', 'src="' + data + '"')
    print(e, '->', len(data), 'chars')

# 把动态换表情改成映射查表
mapping_js = '  var BEAR = {\n' + ''.join("    '%s': '%s',\n" % (e, img_map[e]) for e in emos).rstrip(',\n') + '\n  };\n'
html = html.replace('  var bearImg = document.getElementById',
                    mapping_js + '  var bearImg = document.getElementById', 1)
html = html.replace("bearImg.src = 'xiaolin-' + e + '.png';", 'bearImg.src = BEAR[e];')

out = os.path.join(base, '小熊镇自习室-草图-单文件.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('WROTE', out, os.path.getsize(out), 'bytes')
print('remaining refs:', html.count('xiaolin-'), html.count('.png'))
