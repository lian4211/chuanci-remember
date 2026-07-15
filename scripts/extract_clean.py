#!/usr/bin/env python3
"""从整理版docx提取单词数据"""
import docx, json, re

DOCX = "C:/Users/a1370/Desktop/考研英语串词记忆单词书（整理版）.docx"
OUT = "C:/Users/a1370/chuanci-remember/data/wordbook.json"

doc = docx.Document(DOCX)

# 按顺序解析段落
units = []
cu = None
current_word = None
in_example = False
in_extension = False

def add_word():
    global current_word
    if current_word and current_word.get("english"):
        if cu is not None:
            units[cu-1]["words"].append(current_word)
    current_word = None

for p in doc.paragraphs:
    t = p.text.strip()
    if not t: continue
    
    # Unit header
    m = re.match(r"^Unit\s+(\d+)$", t)
    if m:
        add_word()
        uid = int(m.group(1))
        while len(units) < uid:
            units.append({"id": len(units)+1, "title": f"Unit {len(units)+1}", "words": []})
        cu = uid
        in_example = False
        in_extension = False
        continue
    
    # Numbered word: "1. word" or "1.word"
    m = re.match(r"^(\d+)[.．]\s*([a-zA-Z][a-zA-Z\'\-]*)", t)
    if m:
        add_word()
        word = m.group(2).lower()
        current_word = {
            "english": word,
            "phonetic": {},
            "definitions": [],
            "exam_sentences": [],
            "extensions": [],
            "memory_aid": "",
            "phrases": []
        }
        in_example = False
        in_extension = False
        continue
    
    if current_word is None:
        continue
    
    # "例句：" section header
    if t == "例句：" or t.startswith("例句："):
        in_example = True
        in_extension = False
        continue
    
    # "拓展单词：" section header
    if t.startswith("拓展单词") or t.startswith("拓展"):
        in_example = False
        in_extension = True
        continue
    
    if in_extension:
        # Parse extension words: "word POS 中文；word2 POS 中文"
        parts = re.split(r"[；;]", t)
        for part in parts:
            part = part.strip()
            em = re.match(r"^([a-z][a-z\'\-]+)\s+(n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)(.*)", part, re.I)
            if em:
                current_word["extensions"].append({
                    "word": em.group(1).lower(),
                    "meaning": em.group(3).strip()
                })
            else:
                # Try "word 中文" format
                em2 = re.match(r"^([a-z][a-z\'\-]+)\s+([\u4e00-\u9fff].*)", part, re.I)
                if em2:
                    current_word["extensions"].append({
                        "word": em2.group(1).lower(),
                        "meaning": em2.group(2).strip()
                    })
        continue
    
    if in_example:
        # Remove leading "1." etc.
        sent = re.sub(r"^\d+[.．]\s*", "", t).strip()
        if sent and len(sent) > 10:
            current_word["exam_sentences"].append({
                "sentence": sent,
                "translation": "",
                "source": ""
            })
            # Try to extract year/source
            ym = re.search(r"(\d{4}\s*年[^)]*)", t)
            if ym and current_word["exam_sentences"]:
                current_word["exam_sentences"][-1]["source"] = ym.group(1)
        continue
    
    # If not in example or extension, it's a definition line
    if re.search(r"[\u4e00-\u9fff]", t):
        current_word["definitions"].append(t)

add_word()  # Last word

# Clean up: remove empty words
for u in units:
    u["words"] = [w for w in u["words"] if w.get("english") and w.get("definitions")]

total = sum(len(u["words"]) for u in units)
print(f"{len(units)} 单元, {total} 词")
for u in units:
    if u["words"]:
        print(f"  {u['title']}: {len(u['words'])} 词 ({u['words'][0]['english']} ~ {u['words'][-1]['english']})")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"name":"考研英语串词记忆","version":"1.0","total_units":len(units),"units":units}, f, ensure_ascii=False, indent=2)
