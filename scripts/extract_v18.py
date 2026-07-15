#!/usr/bin/env python3
"""v18 — 从完整上下文窗口提取释义"""
import json, re

CTX = "C:/Users/a1370/chuanci-remember/data/word_contexts.json"
IDX = "C:/Users/a1370/chuanci-remember/data/index_words.json"
OUT = "C:/Users/a1370/chuanci-remember/data/wordbook.json"

with open(CTX, encoding="utf-8") as f:
    ctxs = json.load(f)
with open(IDX, encoding="utf-8") as f:
    unit_words = json.load(f)

entries = {}

for w, data in ctxs.items():
    if not data["found"] or not data["context"]:
        continue
    
    ctx = data["context"]
    defs = []; sents = []; exts = []; mem = ""; ph = {}
    
    for line in ctx.split("\n"):
        if not line.strip(): continue
        
        # Phonetic
        pm = re.search(r"[美英]\s*(/[^/]+/)", line)
        if pm:
            if "美" in line[:5]: ph["us"] = pm.group(1)
            elif "英" in line[:5]: ph["uk"] = pm.group(1)
            else: ph["us"] = pm.group(1)
        
        # POS definition (at line start, after circled numbers)
        line_clean = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿\s]+", "", line)
        
        pm2 = re.match(r"^(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)", line_clean)
        if pm2:
            defs.append(line_clean)
            continue
        
        # Example
        if re.match(r"^\d+[.)]\s", line):
            sents.append({"sentence": re.sub(r"^\d+[.)]\s*","",line).strip(),"translation":"","source":""})
            continue
        
        if line.startswith("参考译文"):
            if sents: sents[-1]["translation"] = line.replace("参考译文","").strip()
            continue
        
        if line.strip() in ("真题例句","助记","拓展","拓展：","章节索引"): continue
        
        # Extension
        if re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿]*\s*([a-z][a-z\'\-]+)\s+(n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)", line):
            em = re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿]*\s*([a-z][a-z\'\-]+)\s+(n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)(.*)", line)
            if em:
                ew = em.group(1).lower()
                if ew != w:
                    exts.append({"word": ew, "meaning": em.group(2) + " " + em.group(3).strip()})
                continue
        
        # Memory aid
        if "=" in line and len(line) > 8 and "考研" not in line and "真题" not in line:
            if re.search(r"[\u4e00-\u9fff]", line):
                mem = (mem + " " + line).strip()
                continue
    
    # Clean defs: remove entries that are just memory aid/circle-number artifacts
    defs = [d for d in defs if not re.match(r"^[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿]", d)]
    
    entries[w] = {"english": w, "phonetic": ph, "definitions": defs,
        "exam_sentences": sents, "extensions": exts, "memory_aid": mem, "phrases": []}

# Group by unit
all_units = []; total = 0
for uid_str, words in unit_words.items():
    ws = [entries[w] for w in words if w in entries and entries[w].get("definitions")]
    if not ws:
        ws = [entries[w] for w in words if w in entries]
    all_units.append({"id": int(uid_str), "title": f"Unit {uid_str}", "words": [{"id": i+1,**w} for i,w in enumerate(ws)]})
    total += len(ws)
    hd = sum(1 for w in ws if w.get("definitions"))
    print(f"Unit {uid_str}: {len(ws)}/{len(words)} 词 ({hd}有释义)")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"name":"考研英语串词记忆","version":"1.0","total_units":len(all_units),"units":all_units}, f, ensure_ascii=False, indent=2)
print(f"\n总计 {total} 词")
