import os, base64, io
from PIL import Image

base = r'E:\03_Projects\bear\study-room\sketch'
bears = r'E:\03_Projects\bear\study-room\public\bears'

with open(os.path.join(base, '同桌版.html'), encoding='utf-8') as f:
    html = f.read()

def data_url(path, size):
    img = Image.open(path).convert('RGBA')
    img.thumbnail((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

emos = ['natural', 'serious', 'happy', 'helpless', 'confused']
for who in ['xiaolin', 'xiaozhao']:
    for e in emos:
        name = who + '-' + e + '.png'
        data = data_url(os.path.join(bears, name), 520)
        html = html.replace(name, data)
        print(name, '->', len(data))

out = os.path.join(base, '小熊镇自习室-同桌版-单文件.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('WROTE', out, os.path.getsize(out), 'bytes')
print('remaining refs:', html.count('.png'))
