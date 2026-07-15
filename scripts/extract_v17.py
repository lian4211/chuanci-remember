#!/usr/bin/env python3
"""v17 — 区分索引行和词条行"""
import json, re

BOOK = "C:/Users/a1370/chuanci-remember/data/book_clean_text.txt"
IDX = "C:/Users/a1370/chuanci-remember/data/index_words.json"
OUT = "C:/Users/a1370/chuanci-remember/data/wordbook.json"

with open(BOOK, encoding="utf-8") as f:
    lines = [l.rstrip("\n\r") for l in f.readlines()]
with open(IDX, encoding="utf-8") as f:
    unit_words = json.load(f)

CIRCLE = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿"

def is_entry(word, line):
    l = line.strip()
    if not l: return False
    # Strip circled numbers and whitespace
    l_clean = re.sub(r"^[" + CIRCLE + r"\s]+", "", l)
    p = r"^" + re.escape(word)
    if re.match(p + r"\s+[\u4e00-\u9fff]", l_clean, re.I): return "word_cn"
    if re.match(p + r"\s+(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)", l_clean, re.I): return "pos"
    if re.match(p + r"\s+[美英]\s*/[^/]+/", l_clean, re.I): return "ph"
    if re.match(p + r"\s*=", l_clean, re.I): return "aid"
    return False

def parse(collected, word):
    defs=[]; sents=[]; exts=[]; mem=""; ph={}
    for l in collected:
        pm = re.search(r"[美英]\s*(/[^/]+/)", l)
        if pm:
            if "美" in l[:5]: ph["us"] = pm.group(1)
            elif "英" in l[:5]: ph["uk"] = pm.group(1)
            else: ph["us"] = pm.group(1)
        m = re.match(r"^(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)", l)
        if m: defs.append(l); continue
        if re.match(r"^\d+[.)]\s", l):
            sents.append({"sentence":re.sub(r"^\d+[.)]\s*","",l).strip(),"translation":"","source":""}); continue
        if l.startswith("参考译文"):
            if sents: sents[-1]["translation"] = l.replace("参考译文","").strip(); continue
        if l in ("真题例句","助记","拓展","拓展：","章节索引"): continue
        em = re.match(r"^([a-z][a-z\'\-]+)\s+(n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)", l)
        if em:
            ew = em.group(1).lower()
            if ew != word: exts.append({"word": ew, "meaning": re.sub(r"^\S+\s+","",l,count=1).strip()})
            continue
        if "=" in l and len(l) > 8 and not l.startswith("考研"):
            mem = (mem + " " + l).strip(); continue
    return {"english":word,"phonetic":ph,"definitions":defs,"exam_sentences":sents,"extensions":exts,"memory_aid":mem,"phrases":[]}

all_entries = {}
for uid_str, words in unit_words.items():
    # Find unit section
    ui = -1; ue = len(lines)
    for i,l in enumerate(lines):
        if l.strip() == f"Unit {int(uid_str)}":
            if ui < 0: ui = i
        elif ui >= 0 and re.match(r"^Unit \d+", l.strip()) and i > ui:
            ue = i; break
    
    for w in words:
        # Try unit section first
        found = False
        for si in range(ui, ue):
            r = is_entry(w, lines[si])
            if r:
                # Collect
                ei = si + 1
                for j in range(si+1, ue):
                    nj = False
                    for w2 in words:
                        if w2 != w and is_entry(w2, lines[j]):
                            nj = True; break
                    if nj: ei = j; break
                    else: ei = j + 1
                all_entries[w] = parse(lines[si:ei], w)
                found = True; break
        
        if found: continue
        # Fallback: scan whole file for any match
        for i,l in enumerate(lines):
            r = is_entry(w, l)
            if r:
                ei = min(i + 300, len(lines))
                for j in range(i+1, ei):
                    nj = False
                    for w2 in unit_words[uid_str]:
                        if w2 != w and is_entry(w2, lines[j]):
                            nj = True; break
                    if nj: ei = j; break
                all_entries[w] = parse(lines[i:ei], w)
                found = True; break

# Build output
all_units = []; total = 0
for uid_str, words in unit_words.items():
    ws = [all_entries[w] for w in words if w in all_entries]
    all_units.append({"id":int(uid_str),"title":f"Unit {uid_str}","words":[{"id":i+1,**w} for i,w in enumerate(ws)]})
    total += len(ws)
    hd = sum(1 for w in ws if w.get("definitions"))
    print(f"Unit {uid_str}: {len(ws)}/{len(words)} 词 (有释义{hd})")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"name":"考研英语串词记忆","version":"1.0","total_units":len(all_units),"units":all_units}, f, ensure_ascii=False, indent=2)
print(f"\n总计 {total} 词")
