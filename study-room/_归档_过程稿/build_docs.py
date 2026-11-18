# -*- coding: utf-8 -*-
"""生成俯视图 PNG，并把两份 markdown 定稿转成 Word。全黑字、微软雅黑。"""
import os
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import RGBColor, Pt, Inches
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
BLACK = (0, 0, 0)


def f(size):
    return ImageFont.truetype(FONT_PATH, size)


def make_topview():
    """画一张图书馆俯视布局图：一屋子长桌、桌桌有人，你和小林只是其中一桌。"""
    S = 2
    W, H = 690, 470
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    def box(x, y, w, h, fill, outline=(150, 150, 150)):
        d.rectangle([x, y, x+w, y+h], fill=fill, outline=outline, width=1)

    def dot(cx, cy, r, fill, outline=(150, 150, 150)):
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=1)

    def txt(x, y, s, size=15, center=False, fill=BLACK):
        fo = f(size)
        if center:
            bbox = d.textbbox((0, 0), s, font=fo)
            x = x - (bbox[2]-bbox[0])//2
        d.text((x, y), s, font=fo, fill=fill)

    # 标题
    txt(40, 20, "图书馆俯视 · 一屋子长桌、桌桌有人", 24)
    txt(40, 50, "你和小林只是其中一桌：不居中、不追光；满屋子人都在各学各的", 14, fill=(90, 90, 90))

    # 窗户与书架（空间边界）
    d.rectangle([30, 80, 46, 350], fill=(232, 240, 246), outline=(185, 200, 212), width=1)
    txt(38, 210, "窗", 12, center=True, fill=(90, 90, 90))
    d.rectangle([644, 80, 660, 350], fill=(238, 232, 222), outline=(205, 195, 180), width=1)
    txt(652, 210, "书架", 12, center=True, fill=(90, 90, 90))

    # 背景行：3 张桌，每张 4 人（远）
    txt(60, 84, "背景行 · 每桌 4 人", 11, fill=(130, 130, 130))
    for x0 in (80, 300, 520):
        box(x0, 100, 110, 26, (242, 242, 240), outline=(205, 205, 205))
        for k in range(4):
            dot(x0 + 16 + k * 26, 113, 5, (208, 208, 206), outline=(190, 190, 190))

    # 中排行：3 张桌
    txt(60, 148, "中排行", 11, fill=(130, 130, 130))
    for x0 in (80, 300, 520):
        box(x0, 164, 110, 26, (242, 242, 240), outline=(205, 205, 205))
        for k in range(4):
            dot(x0 + 16 + k * 26, 177, 5, (208, 208, 206), outline=(190, 190, 190))

    # 前排三桌：你那桌和别桌一样大，只用颜色标出你和小林
    txt(60, 214, "前排", 11, fill=(130, 130, 130))
    for x0 in (80, 520):
        box(x0, 232, 110, 26, (242, 242, 240), outline=(205, 205, 205))
        for k in range(4):
            dot(x0 + 16 + k * 26, 245, 5, (208, 208, 206), outline=(190, 190, 190))
    box(290, 232, 110, 26, (242, 242, 240), outline=(205, 205, 205))
    for k, xx in enumerate((306, 332, 358, 384)):
        if k == 0:
            dot(xx, 245, 5, (250, 199, 117))
        elif k == 1:
            dot(xx, 245, 5, (159, 225, 203))
        else:
            dot(xx, 245, 5, (208, 208, 206), outline=(190, 190, 190))
    txt(319, 262, "你", 9, center=True, fill=(150, 120, 60))
    txt(345, 262, "小林", 9, center=True, fill=(70, 130, 110))

    # 密度说明
    txt(345, 300, "满屋子 20+ 人 · 各学各的 · 不可点、不看你、不互动", 12, center=True, fill=(100, 100, 100))

    # 底部规则
    txt(40, 348, "构图：以全景为主，镜头扫过整间屋子；你那桌只是画面里的一桌，不追光不居中", 13)
    txt(40, 378, "集体感来自「满屋子人都在做事」，不只靠小林一只；做到看得见手、看不清脸", 13, fill=(90, 90, 90))
    txt(40, 408, "光统一从左上（窗）进 → 影子落向右下；台灯各照一小块光池", 13, fill=(90, 90, 90))

    img = img.resize((W*S, H*S), Image.LANCZOS)
    out = os.path.join(HERE, "桌子俯视布局.png")
    img.save(out)
    print("PNG saved:", out, img.size)
    return out


def set_cn_font(style, name="Microsoft YaHei"):
    style.font.name = name
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), name)


def clean_runs(paragraph):
    """把段落里所有 run 强制设成黑色、微软雅黑。"""
    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
        if not run.font.name:
            run.font.name = "Microsoft YaHei"
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def add_inline(paragraph, text):
    """支持 **加粗** 的行内文本。"""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if part == "":
            continue
        run = paragraph.add_run(part)
        if i % 2 == 1:
            run.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.font.name = "Microsoft YaHei"
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def is_table_sep(line):
    cells = line.strip().strip("|").split("|")
    return len(cells) >= 1 and all("-" in c and set(c.strip()) <= set("-:") for c in cells)


def md_to_docx(md_path, docx_path):
    with open(md_path, "r", encoding="utf-8") as fp:
        lines = fp.read().split("\n")

    doc = Document()
    # 全黑字 + 中文样式（含标题样式定义本身）
    set_cn_font(doc.styles["Normal"])
    for sname in ["Title", "Heading 1", "Heading 2", "Heading 3", "Heading 4",
                  "List Bullet", "List Number", "Quote"]:
        try:
            set_cn_font(doc.styles[sname])
        except KeyError:
            pass

    sec = doc.sections[0]
    sec.top_margin = Inches(0.8)
    sec.bottom_margin = Inches(0.8)
    sec.left_margin = Inches(0.9)
    sec.right_margin = Inches(0.9)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()

        if stripped == "":
            i += 1
            continue

        # 图片
        if stripped.startswith("![") and "](" in stripped:
            p = stripped[stripped.find("(")+1: stripped.rfind(")")]
            imgp = os.path.join(HERE, p)
            if os.path.exists(imgp):
                para = doc.add_paragraph()
                para.alignment = 1  # 居中
                para.add_run().add_picture(imgp, width=Inches(6.0))
                clean_runs(para)
            i += 1
            continue

        # 代码块
        if stripped.startswith("```"):
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            para = doc.add_paragraph()
            run = para.add_run("\n".join(code))
            run.font.name = "Consolas"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0, 0, 0)
            rpr = run._element.get_or_add_rPr()
            rfonts = rpr.get_or_add_rFonts()
            rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")
            continue

        # 标题
        if stripped.startswith("#"):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            level = min(hashes, 4)
            text = stripped[hashes:].strip()
            para = doc.add_heading(level=level)
            add_inline(para, text)
            i += 1
            continue

        # 分隔线
        if stripped == "---":
            para = doc.add_paragraph()
            run = para.add_run("_" * 46)
            run.font.color.rgb = RGBColor(180, 180, 180)
            i += 1
            continue

        # 表格
        if stripped.startswith("|") and i + 1 < n and is_table_sep(lines[i+1]):
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            table = doc.add_table(rows=1, cols=len(header))
            table.style = "Table Grid"
            for j, h in enumerate(header):
                cell = table.rows[0].cells[j]
                cell.text = ""
                add_inline(cell.paragraphs[0], h)
                for r in cell.paragraphs[0].runs:
                    r.bold = True
            for row in rows:
                cells = table.add_row().cells
                for j, val in enumerate(row):
                    if j < len(cells):
                        cells[j].text = ""
                        add_inline(cells[j].paragraphs[0], val)
            doc.add_paragraph()
            continue

        # 引用
        if stripped.startswith("> "):
            para = doc.add_paragraph()
            para.paragraph_format.left_indent = Inches(0.25)
            add_inline(para, stripped[2:].strip())
            i += 1
            continue

        # 无序列表
        if stripped.startswith("- "):
            para = doc.add_paragraph(style="List Bullet")
            add_inline(para, stripped[2:].strip())
            i += 1
            continue

        # 有序列表
        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1:3] in (". ", "、") :
            para = doc.add_paragraph(style="List Number")
            add_inline(para, stripped[3:].strip() if stripped[1:3] == ". " else stripped[2:].strip())
            i += 1
            continue

        # 普通段落
        para = doc.add_paragraph()
        add_inline(para, stripped)
        i += 1

    # 最后兜底：遍历所有表格单元格 + 段落，确保全黑字
    for para in doc.paragraphs:
        clean_runs(para)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    clean_runs(para)

    doc.save(docx_path)
    print("DOCX saved:", docx_path)


if __name__ == "__main__":
    make_topview()
    md_to_docx(os.path.join(HERE, "小熊镇自习室-场景与体验设计.md"),
               os.path.join(HERE, "小熊镇自习室-场景与体验设计.docx"))
    print("ALL DONE")
