import os, base64, io
from PIL import Image

base = r'E:\03_Projects\bear\visual-demo'
html_path = os.path.join(base, 'index.html')
with open(html_path, encoding='utf-8') as f:
    html = f.read()

def embed_png(name, max_size):
    p = os.path.join(base, 'assets', name)
    img = Image.open(p).convert('RGBA')
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    print(name, '->', len(data), 'chars')
    return 'data:image/png;base64,' + data

def embed_jpg(name, max_size):
    p = os.path.join(base, 'assets', name)
    img = Image.open(p).convert('RGB')
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=82, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode()
    print(name, '->', len(data), 'chars')
    return 'data:image/jpeg;base64,' + data

emos = ['natural', 'serious', 'happy', 'helpless', 'confused']
img_data = {}
for e in emos:
    img_data[e] = embed_png('chenggong-' + e + '.png', 520)
bg_data = embed_jpg('library.png', 1280)

# 1) 背景图
html = html.replace("url('assets/library.png')", "url('" + bg_data + "')")

# 2) 初始熊图
html = html.replace('<img src="assets/chenggong-serious.png"', '<img src="' + img_data['serious'] + '"')

# 3) 注入图片映射 + 替换两处动态路径
mapping = '  var bearImages = {\n'
for e in emos:
    mapping += "    '" + e + "': '" + img_data[e] + "',\n"
mapping = mapping.rstrip(',\n') + '\n  };\n'

anchor = "  var scene = document.getElementById('scene');"
html = html.replace(anchor, mapping + anchor, 1)
html = html.replace("bear.src = 'assets/chenggong-' + v + '.png';", "bear.src = bearImages[v];")
html = html.replace("bear.src = 'assets/chenggong-' + (v === 'focus' ? 'serious' : 'helpless') + '.png';",
                    "bear.src = v === 'focus' ? bearImages.serious : bearImages.helpless;")

out = os.path.join(base, '小熊镇自习室-动画版-单文件.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('WROTE', out, os.path.getsize(out), 'bytes')
print('remaining asset refs:', html.count('assets/'))
