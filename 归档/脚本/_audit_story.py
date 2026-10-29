from pathlib import Path

from docx import Document


path = Path.cwd() / "剧情册" / "剧情册.docx"
doc = Document(path)
content = "\n".join(p.text for p in doc.paragraphs)
content += "\n" + "\n".join(
    cell.text for table in doc.tables for row in table.rows for cell in row.cells
)
checks = [
    "M02_LIBRARY",
    "E10b",
    "延期复核",
    "未转正",
    "第七月补充复核",
    "第八月不重复开放转正复核",
    "probation_status=not_confirmed",
]
lines = [
    f"file={path.resolve()}",
    f"bytes={path.stat().st_size}",
    f"paragraphs={len(doc.paragraphs)} tables={len(doc.tables)}",
]
lines.extend(f"{term}: {content.count(term)}" for term in checks)
m8_start = content.find("第八个月流程")
m9_start = content.find("第九个月流程", m8_start + 1)
m8_content = content[m8_start:m9_start] if m8_start >= 0 and m9_start > m8_start else ""
lines.append(f"stale_m8_review={('本月补充复核' in m8_content)}")
Path("_audit_merge.txt").write_text("\n".join(lines), encoding="utf-8")
context = []
terms = ("M02_LIBRARY", "E10b", "判定口径", "未转正版", "第七月补充复核", "第八月不重复", "M7 deferred", "王哥的反馈纸", "【3.2 时间】", "评估：第六月", "第七月是延期后的补充复核")
for i, paragraph in enumerate(doc.paragraphs):
    if any(term in paragraph.text for term in terms):
        context.append(f"P{i}: {paragraph.text}")
Path("_audit_context.txt").write_text("\n".join(context), encoding="utf-8")
section = [f"P{i}: {doc.paragraphs[i].text}" for i in range(525, 590)]
Path("_audit_month7.txt").write_text("\n".join(section), encoding="utf-8")
table_lines = []
for i, table in enumerate(doc.tables[:12]):
    table_lines.append(f"T{i}: " + " | ".join(cell.text for row in table.rows for cell in row.cells))
Path("_audit_tables.txt").write_text("\n".join(table_lines), encoding="utf-8")
