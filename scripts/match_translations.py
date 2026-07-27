#!/usr/bin/env python3
"""为每个例句匹配中文翻译"""
import json, re

WB = "C:/Users/a1370/chuanci-remember/data/wordbook.json"
BOOK = "C:/Users/a1370/chuanci-remember/data/book_clean_text.txt"

with open(WB, encoding="utf-8") as f:
    wb = json.load(f)
with open(BOOK, encoding="utf-8") as f:
    lines = f.readlines()

# 构建句子→翻译的映射
sent_trans = {}
for i, l in enumerate(lines):
    t = l.strip()
    if t.startswith("参考译文"):
        # 往前找最近的例句
        trans = t.replace("参考译文", "").strip()
        for j in range(i-1, max(0, i-20), -1):
            prev = lines[j].strip()
            if re.match(r"^\d+[.)]\s", prev):
                sentence = re.sub(r"^\d+[.)]\s*", "", prev).strip()
                if sentence and len(sentence) > 20:
                    # Use sentence prefix (first 40 chars) as key
                    key = sentence[:40]
                    if key not in sent_trans:
                        sent_trans[key] = trans
                    break
            if prev.startswith(("Unit", "章节索引")):
                break

print(f"找到 {len(sent_trans)} 句翻译")

# Apply to wordbook
matched = 0
for u in wb["units"]:
    for w in u["words"]:
        for s in w.get("exam_sentences", []):
            if s.get("translation"):
                continue
            sen = s.get("sentence", "")
            if not sen: continue
            key = sen[:40]
            if key in sent_trans:
                s["translation"] = sent_trans[key]
                matched += 1
            else:
                # Try longer key
                for bk, bv in sent_trans.items():
                    if bk in sen or sen[:30] in bk:
                        s["translation"] = bv
                        matched += 1
                        break

with open(WB, "w", encoding="utf-8") as f:
    json.dump(wb, f, ensure_ascii=False, indent=2)

has_trans = sum(1 for u in wb["units"] for w in u["words"] for s in w.get("exam_sentences", []) if s.get("translation"))
total_sent = sum(1 for u in wb["units"] for w in u["words"] for _ in w.get("exam_sentences", []))
print(f"已匹配: {matched}, 有翻译: {has_trans}/{total_sent}")
