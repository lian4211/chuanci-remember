#!/usr/bin/env python3
"""v19 — 精确定位词条边界"""
import json, re

CTX = "C:/Users/a1370/chuanci-remember/data/word_contexts.json"
IDX = "C:/Users/a1370/chuanci-remember/data/index_words.json"
OUT = "C:/Users/a1370/chuanci-remember/data/wordbook.json"

with open(CTX, encoding="utf-8") as f:
    ctx_data = json.load(f)
with open(IDX, encoding="utf-8") as f:
    unit_words = json.load(f)

ALL_WORDS = set()
for ws in unit_words.values():
    ALL_WORDS.update(ws)

CIRCLE = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿"

def clean_line(line):
    return re.sub(r"^[" + CIRCLE + r"\s　]+", "", line.strip())

def is_entry_start(word, line):
    cl = clean_line(line)
    if re.match(r"^" + re.escape(word) + r"\b", cl, re.I):
        rest = cl[len(word):].strip()
        if rest and not rest.startswith(("的", "人", "者", "地", "了", "是")):
            return True
    return False

def find_entry_lines(word, context):
    lines = context.split("\n")
    
    # Strategy 1: Find word at line start
    start = -1
    for i, l in enumerate(lines):
        if is_entry_start(word, l):
            start = i
            break
    
    # Strategy 2: Find POS line with word in next 2 lines
    if start < 0:
        for i, l in enumerate(lines):
            cl = clean_line(l)
            if re.match(r"^(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)", cl):
                for j in range(i+1, min(i+3, len(lines))):
                    if re.search(r"\b" + re.escape(word) + r"\b", lines[j], re.I):
                        start = i
                        break
                if start >= 0:
                    break
    
    if start < 0:
        return []
    
    # Include 1-2 lines before (some entries have POS on line above)
    max_back = 3
    while start > 0 and max_back > 0:
        prev = lines[start - 1].strip()
        if not prev:
            max_back -= 1; start -= 1
            continue
        # Check if prev looks like POS definition for the word
        if re.match(r"^(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)", clean_line(prev)):
            max_back -= 1; start -= 1
            continue
        # Check if prev is phonetic
        if re.search(r"[美英]\s*/[^/]+/", prev):
            max_back -= 1; start -= 1
            continue
        # Don't go back if prev is clearly another word's content
        cm = re.match(r"^([a-z][a-z\'\-]+)\b", clean_line(prev), re.I)
        if cm:
            cw = cm.group(1).lower()
            if cw in ALL_WORDS and cw != word.lower():
                break
        break
    
    end = len(lines)
    for i in range(start + 1, len(lines)):
        cl = clean_line(lines[i])
        found_end = False
        cm = re.match(r"^([a-z][a-z\'\-]+)\b", cl, re.I)
        if cm:
            cw = cm.group(1).lower()
            if cw != word.lower() and cw in ALL_WORDS:
                rest = cl[len(cw):].strip()
                if rest and not rest.startswith(("的","人","者","地","了")):
                    end = i
                    break
        if found_end:
            break
    
    return lines[start:end]

def parse(word, lines):
    defs = []; sents = []; exts = []; mem = ""; ph = {}
    for l in lines:
        ll = l.strip()
        if not ll: continue
        pm = re.search(r"[美英]\s*(/[^/]+/)", ll)
        if pm:
            if "美" in ll[:5]: ph["us"] = pm.group(1)
            elif "英" in ll[:5]: ph["uk"] = pm.group(1)
            else: ph["us"] = pm.group(1)
        cl = clean_line(ll)
        if cl in ("真题例句","助记","拓展","拓展：","章节索引"): continue
        if cl.startswith("参考译文"):
            if sents: sents[-1]["translation"] = ll.replace("参考译文","").strip(); continue
        # Skip if this line is another word's entry
        candidate = re.match(r"^([a-z][a-z\'\-]+)\b", cl, re.I)
        if candidate:
            cw = candidate.group(1).lower()
            if cw != word.lower() and cw in ALL_WORDS:
                rest = cl[len(cw):].strip()
                if rest and not rest.startswith(("的","人","者","地","了")):
                    continue
        if re.match(r"^(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)", cl):
            defs.append(ll); continue
        if "=" in ll and re.search(r"[\u4e00-\u9fff]", ll) and "考研" not in ll:
            mem = (mem + " " + ll).strip(); continue
        em = re.match(r"^([a-z][a-z\'\-]+)\s+(n\.|v\.|adj\.|adv\.|prep\.|conj\.|vt\.|vi\.)", cl)
        if em:
            ew = em.group(1).lower()
            if ew != word.lower(): exts.append({"word": ew, "meaning": re.sub(r"^\S+\s+","",cl,count=1).strip()})
            continue
        if re.match(r"^\d+[.)]\s", ll):
            sents.append({"sentence":re.sub(r"^\d+[.)]\s*","",ll).strip(),"translation":"","source":""}); continue
    return {"english":word,"phonetic":ph,"definitions":defs,"exam_sentences":sents,"extensions":exts,"memory_aid":mem,"phrases":[]}

entries = {}
for w in sorted(ALL_WORDS):
    if w not in ctx_data: continue
    lines = find_entry_lines(w, ctx_data[w].get("context",""))
    entries[w] = parse(w, lines) if lines else {"english":w,"phonetic":{},"definitions":[],"exam_sentences":[],"extensions":[],"memory_aid":"","phrases":[]}

units = []; total = 0
for uid_str, words in unit_words.items():
    ws = [entries[w] for w in words if w in entries]
    units.append({"id":int(uid_str),"title":f"Unit {uid_str}","words":[{"id":i+1,**w} for i,w in enumerate(ws)]})
    total += len(ws)
    hd = sum(1 for w in ws if w.get("definitions"))
    print(f"Unit {uid_str}: {len(ws)}/{len(words)} 词 ({hd}有释义)")

with open(OUT,"w",encoding="utf-8") as f:
    json.dump({"name":"考研英语串词记忆","version":"1.0","total_units":len(units),"units":units}, f, ensure_ascii=False, indent=2)
print(f"\n总计 {total} 词")
