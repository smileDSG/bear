# -*- coding: utf-8 -*-
"""画 A 图书馆的 2.5D 主视角：斜侧俯视、分层视差、统一光影，疏朗不拥挤。"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
S = 2
W, H = 1120, 660


def f(size):
    return ImageFont.truetype(FONT_PATH, size)


def txt(d, x, y, s, size=14, fill=(60, 60, 60), center=False):
    fo = f(size)
    if center:
        bbox = d.textbbox((0, 0), s, font=fo)
        x = x - (bbox[2] - bbox[0]) // 2
    d.text((x, y), s, font=fo, fill=fill)


def glow(img, cx, cy, rx, ry, color=(255, 208, 120), steps=14, max_alpha=52):
    """台灯光池：多层椭圆从中心到边缘渐隐。"""
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(steps, 0, -1):
        t = i / steps
        a = int(max_alpha * (1 - t) ** 1.4)
        d.ellipse([cx - rx * t, cy - ry * t, cx + rx * t, cy + ry * t],
                  fill=(color[0], color[1], color[2], a))


def person(d, x, y_back, scale, body, head, detail=False):
    """坐在桌后的人（桌沿会盖住下半身）。y_back = 桌后缘 y。"""
    hw = int(15 * scale)
    hh = int(13 * scale)
    # 影子投在身后的桌面上（光从左上）
    d.ellipse([x - hw + 4, y_back - 2, x + hw + 8, y_back + 5],
              fill=(60, 55, 45, 40))
    # 肩膀（梯形），桌面会盖住下半
    d.polygon([(x - hw, y_back + 6), (x + hw, y_back + 6),
               (x + hw - 3, y_back - int(16 * scale)), (x - hw + 3, y_back - int(16 * scale))],
              fill=(body[0], body[1], body[2], body[3] if len(body) > 3 else 255))
    # 头（略低）
    hy = y_back - int(22 * scale)
    d.ellipse([x - hh, hy - hh, x + hh, hy + hh], fill=head)
    if detail:
        # 熊耳
        d.ellipse([x - hh - 2, hy - hh - 5, x - hh + 6, hy - hh + 3], fill=head)
        d.ellipse([x + hh - 6, hy - hh - 5, x + hh + 2, hy - hh + 3], fill=head)
        # 低头：脸上半阴影
        d.pieslice([x - hh, hy - hh, x + hh, hy + hh], 180, 360,
                   fill=(0, 0, 0, 28))


def desk(img, d, cx, y_back, w_back, w_front, depth, scale, people,
         tone=(234, 222, 203), alpha=255, detail=False, lamp=True, plant=False, label=None):
    """一张斜侧俯视的长桌：梯形桌面 + 厚度 + 人 + 道具 + 光池 + 影子。"""
    xb0, xb1 = cx - w_back / 2, cx + w_back / 2
    xf0, xf1 = cx - w_front / 2, cx + w_front / 2
    y_front = y_back + depth
    # 桌面在地面的投影（统一右下）
    d.polygon([(xb0 + 6, y_back + 6), (xb1 + 6, y_back + 6),
               (xf1 + 10, y_front + 8), (xf0 + 10, y_front + 8)], fill=(60, 55, 45, 30))
    # 桌面（梯形，近边宽）
    d.polygon([(xb0, y_back), (xb1, y_back), (xf1, y_front), (xf0, y_front)],
              fill=(tone[0], tone[1], tone[2], alpha))
    # 桌沿厚度
    d.polygon([(xf0, y_front), (xf1, y_front), (xf1, y_front + 8), (xf0, y_front + 8)],
              fill=(196, 178, 152, alpha))
    # 人坐在桌后（先画人，桌面已画，人会露在桌后缘之上）
    n = len(people)
    for k, (body, head) in enumerate(people):
        px = xb0 + (xb1 - xb0) * (k + 0.5) / n
        person(d, px, y_back, scale, body, head, detail=detail)
    # 台灯光池（叠在桌面上）
    if lamp:
        glow(img, xb0 + w_back * 0.16, y_back + depth * 0.45,
             int(w_back * 0.18), int(depth * 0.5))
        glow(img, xb1 - w_back * 0.16, y_back + depth * 0.45,
             int(w_back * 0.18), int(depth * 0.5), color=(255, 200, 110), max_alpha=46)
        # 两盏台灯
        for lx in (xb0 + w_back * 0.16, xb1 - w_back * 0.16):
            d.polygon([(lx - 9, y_back + depth * 0.2), (lx + 9, y_back + depth * 0.2),
                       (lx + 5, y_back + depth * 0.05), (lx - 5, y_back + depth * 0.05)],
                      fill=(246, 206, 122, min(255, alpha + 40)))
    # 桌面道具：摊开的书、杯子、笔
    for k in range(max(1, n - 1)):
        bx = xb0 + w_back * (0.28 + k * 0.22)
        by = y_back + depth * 0.55
        d.polygon([(bx, by), (bx + int(30 * scale), by - 2),
                   (bx + int(30 * scale), by + int(13 * scale)), (bx, by + int(15 * scale))],
                  fill=(252, 251, 247, min(255, alpha + 30)))
        d.line([(bx + int(15 * scale), by), (bx + int(15 * scale), by + int(14 * scale))],
               fill=(205, 200, 190, alpha), width=1)
    # 绿萝边界（玩家桌）
    if plant:
        gx, gy = cx + w_back * 0.15, y_back + depth * 0.32
        d.ellipse([gx - int(11 * scale), gy, gx + int(11 * scale), gy + int(10 * scale)],
                  fill=(198, 150, 110, alpha))
        for a in range(-60, 61, 30):
            import math
            rad = math.radians(a)
            ex = gx + int(20 * scale) * math.sin(rad)
            ey = gy - int(20 * scale) * math.cos(rad)
            d.ellipse([ex - int(7 * scale), ey - int(5 * scale), ex + int(7 * scale), ey + int(5 * scale)],
                      fill=(120, 168, 108, alpha))
    if label:
        txt(d, cx, y_front + 12, label, 12, (110, 92, 62), center=True)


def make():
    img = Image.new("RGB", (W, H), (247, 246, 242))
    d = ImageDraw.Draw(img, "RGBA")

    # 标题
    txt(d, 40, 16, "图书馆主视角 · 2.5D 斜侧俯视", 22, (35, 35, 35))
    txt(d, 40, 46, "分层视差：背景 30% / 中景 60% / 前景 100% · 统一左上光、影子落右下 · 疏朗留过道，不塞满", 13, (105, 105, 105))

    # ===== 背景层（视差 30%，淡、冷）=====
    # 左窗
    d.rectangle([40, 84, 250, 286], fill=(224, 237, 246, 255), outline=(190, 205, 216, 255), width=2)
    d.line([(145, 84), (145, 286)], fill=(190, 205, 216, 200), width=2)
    d.line([(40, 184), (250, 184)], fill=(190, 205, 216, 200), width=2)
    for cx, cy, rx, ry in [(92, 138, 30, 18), (190, 122, 24, 15), (110, 244, 34, 20), (205, 250, 26, 16)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(198, 219, 192, 80))
    txt(d, 145, 292, "窗 · 树影慢移 · 侧光从左上进", 11, (110, 118, 122), center=True)
    # 右书架
    d.rectangle([870, 84, 1080, 286], fill=(216, 202, 180, 255), outline=(184, 168, 144, 255), width=2)
    bcols = [(158, 120, 105), (120, 140, 125), (185, 160, 110), (110, 125, 145), (170, 135, 120)]
    for i in range(4):
        yy = 84 + i * 51
        d.line([(870, yy), (1080, yy)], fill=(184, 168, 144, 200), width=2)
        for j in range(10):
            bx = 878 + j * 20
            bh = 30 + (j % 3) * 7
            d.rectangle([bx, yy + 5, bx + 15, yy + bh], fill=bcols[(i + j) % 5] + (220,))
    txt(d, 975, 292, "书架 · 图书馆身份", 11, (120, 106, 90), center=True)

    neutral = [((150, 158, 164, 210), (168, 176, 182, 220)),
               ((176, 164, 150, 210), (192, 180, 166, 220)),
               ((140, 152, 160, 210), (160, 172, 180, 220))]

    # ===== 远景桌（更小更淡，视差 30%）=====
    desk(img, d, 360, 150, 120, 140, 26, 0.55,
         [neutral[0], neutral[2]], tone=(230, 228, 222), alpha=150, lamp=False)
    desk(img, d, 690, 150, 120, 140, 26, 0.55,
         [neutral[1], neutral[0]], tone=(230, 228, 222), alpha=150, lamp=False)

    # ===== 中景桌（视差 60%）=====  右侧桌下移到书架下方空白处，避免重叠
    desk(img, d, 245, 226, 150, 186, 40, 0.78,
         [neutral[0], neutral[1], neutral[2]], tone=(232, 224, 208), alpha=225, lamp=True)
    desk(img, d, 815, 318, 150, 186, 40, 0.78,
         [neutral[2], neutral[1], neutral[0]], tone=(232, 224, 208), alpha=225, lamp=True)

    # ===== 近景：玩家桌（最大最清晰，视差 100%）=====
    me = ((246, 194, 96, 255), (250, 168, 70, 255))       # 你（橙）
    xiaolin = ((126, 196, 170, 255), (150, 214, 190, 255))  # 小林（青）
    desk(img, d, 560, 322, 250, 300, 66, 1.15,
         [me, xiaolin, neutral[1]], tone=(236, 224, 205), alpha=255,
         detail=True, lamp=True, plant=True, label="你这一桌 · 与别桌同样大小，只是最近")

    # ===== 前景虚化桌沿（最近层，视差 100%，模糊）=====
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fg, "RGBA")
    fd.polygon([(0, 600), (W, 590), (W, H), (0, H)], fill=(214, 200, 178, 150))
    fd.ellipse([120, 612, 360, 660], fill=(246, 244, 238, 130))  # 虚化的书角
    fg = fg.filter(ImageFilter.GaussianBlur(9))
    img = Image.alpha_composite(img.convert("RGBA"), fg).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    txt(d, 40, 616, "前景虚化桌沿（最近，视差 100%）", 11, (120, 120, 120))

    # ===== 分层图例（说明这是 2.5D）=====
    lx, ly = 40, 470
    d.rounded_rectangle([lx - 8, ly - 8, lx + 250, ly + 92], radius=8,
                        fill=(250, 249, 245, 235), outline=(210, 205, 195, 255))
    txt(d, lx, ly, "2.5D 三层怎么动", 13, (70, 70, 70))
    d.rectangle([lx, ly + 28, lx + 18, ly + 41], fill=(196, 212, 222, 255))
    txt(d, lx + 26, ly + 27, "背景 窗/书架/远景桌 → 移 30%", 11, (95, 95, 95))
    d.rectangle([lx, ly + 50, lx + 18, ly + 63], fill=(214, 200, 180, 255))
    txt(d, lx + 26, ly + 49, "中景 各桌的人 → 移 60%", 11, (95, 95, 95))
    d.rectangle([lx, ly + 72, lx + 18, ly + 85], fill=(236, 224, 205, 255))
    txt(d, lx + 26, ly + 71, "前景 虚化桌沿 → 移 100%", 11, (95, 95, 95))

    # 底部说明
    txt(d, 560, 636, "近桌清晰、远桌淡；看得见手在做事，不靠把人堆密 · 人群不可点、不看你", 12, (110, 110, 110), center=True)

    img = img.resize((W * S, H * S), Image.LANCZOS)
    out = os.path.join(HERE, "图书馆主视角.png")
    img.save(out)
    print("PNG saved:", out, img.size)
    return out


if __name__ == "__main__":
    make()
