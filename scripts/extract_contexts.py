#!/usr/bin/env python3
"""提取每个词的全部上下文（大幅窗口）"""
import json, re

BOOK = "C:/Users/a1370/chuanci-remember/data/book_clean_text.txt"
IDX = "C:/Users/a1370/chuanci-remember/data/index_words.json"
OUT = "C:/Users/a1370/chuanci-remember/data/word_contexts.json"

with open(BOOK, encoding="utf-8") as f:
    lines = [l.rstrip("\n\r") for l in f.readlines()]

with open(IDX, encoding="utf-8") as f:
    unit_words = json.load(f)

CIRCLE_CHARS = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿"

def is_entry_start(word, text):
    """判断文本是否以word的词条开始"""
    t = re.sub(r"^[" + CIRCLE_CHARS + r"\s　]+", "", text.strip())
    if re.match(r"^" + re.escape(word) + r"\b", t, re.I):
        return True
    return False

all_contexts = {}
uniq_words = set()
for ws in unit_words.values():
    uniq_words.update(ws)

for w in sorted(uniq_words):
    # Find positions where word appears as entry start
    positions = []
    for i, l in enumerate(lines):
        if is_entry_start(w, l):
            positions.append(i)
            if len(positions) >= 3:
                break
    
    if not positions:
        # Any occurrence
        for i, l in enumerate(lines):
            if re.search(r"\b" + re.escape(w) + r"\b", l, re.I):
                positions.append(i)
                if len(positions) >= 3:
                    break
    
    # Use first/main position
    pos = positions[0] if positions else -1
    if pos < 0:
        all_contexts[w] = {"word": w, "context": "", "found": False}
        continue
    
    # Take big window: 5 lines before, 30 lines after
    start = max(0, pos - 5)
    end = min(len(lines), pos + 40)
    ctx_lines = lines[start:end]
    
    all_contexts[w] = {
        "word": w,
        "position": pos,
        "found": True,
        "context": "\n".join(ctx_lines)
    }

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(all_contexts, f, ensure_ascii=False, indent=2)

found = sum(1 for v in all_contexts.values() if v["found"])
print(f"总{len(all_contexts)}词, 找到上下文{found}词")
