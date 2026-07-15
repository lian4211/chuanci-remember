#!/usr/bin/env python3
"""把扫描书籍转纯文本，按顺序输出"""
import docx

BOOK = "C:/Users/a1370/Desktop/扫描书籍(1).docx"
OUT = "C:/Users/a1370/chuanci-remember/data/book_clean_text.txt"

doc = docx.Document(BOOK)
lines = []

for p in doc.paragraphs:
    t = p.text.strip()
    if t:
        lines.append(t)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"导出 {len(lines)} 行, {sum(len(l) for l in lines)} 字符")
