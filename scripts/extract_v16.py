#!/usr/bin/env python3
"""v16 — 纯文本逐词定位提取"""
import json, re

BOOK = "C:/Users/a1370/chuanci-remember/data/book_clean_text.txt"
IDX = "C:/Users/a1370/chuanci-remember/data/index_words.json"
OUT = "C:/Users/a1370/chuanci-remember/data/wordbook.json"

with open(BOOK, encoding="utf-8") as f:
    lines = f.readlines()

with open(IDX, encoding="utf-8") as f:
    unit_words = json.load(f)

# Clean lines
lines = [l.rstrip("\n\r") for l in lines]

all_entries = {}

for uid_str, words in unit_words.items():
    uid = int(uid_str)
    unit_text = []
    in_unit = False
    
    # Extract lines for this unit section
    for i, l in enumerate(lines):
        if l.strip() == f"Unit {uid}":
            in_unit = True
            continue
        if in_unit:
            if l.strip().startswith("Unit ") and l.strip() != f"Unit {uid}" and re.match(r"^Unit \d+", l.strip()):
                break
            unit_text.append(l)
    
    # Find entries for each word
    for w in words:
        if not w or len(w) <= 1:
            continue
        
        entry_start = -1
        entry_lines = []
        
        # Clean pattern: word may appear as "word 中文" or "word=" or "word\t操作" etc.
        for i, l in enumerate(unit_text):
            # Match word at line start (possibly with phonetic before it)
            l_stripped = l.strip()
            if not l_stripped:
                continue
            
            # Check if word appears at the start (possibly after 美/英 phonetic)
            m = re.match(r"^[美英]\s*/[^/]*/\s*" + re.escape(w) + r"\b", l, re.IGNORECASE)
            if m:
                entry_start = i
                continue
            
            m2 = re.match(r"^" + re.escape(w) + r"\b", l, re.IGNORECASE)
            if m2:
                entry_start = i
                continue
        
        if entry_start < 0:
            # Try any occurrence
            for i, l in enumerate(unit_text):
                if re.search(r"\b" + re.escape(w) + r"\b", l, re.IGNORECASE):
                    entry_start = i
                    break
        
        if entry_start < 0:
            continue
        
        # Collect entry from position to next word or end
        collected = []
        next_word_found = False
        for i in range(entry_start, len(unit_text)):
            l = unit_text[i].strip()
            if not l:
                continue
            # Check if this line starts a new vocabulary entry
            if i > entry_start:
                is_new = False
                for w2 in words:
                    if w2 == w: continue
                    pat = r"^" + re.escape(w2) + r"\b"
                    if re.match(pat, l, re.IGNORECASE) and len(re.match(pat, l, re.IGNORECASE).group()) == len(w2):
                        is_new = True
                        break
                if is_new:
                    break
            collected.append(l)
        
        # Parse collected lines
        defs = []
        sents = []
        exts = []
        mem = ""
        ph = {}
        
        for l in collected:
            # Phonetic
            pm = re.search(r"[美英]\s*(/[^/]+/)", l)
            if pm:
                if "美" in l[:10]: ph["us"] = pm.group(1)
                elif "英" in l[:10]: ph["uk"] = pm.group(1)
                else: ph["us"] = pm.group(1)
            
            # POS definition
            pm2 = re.match(r"^(n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.|abbr\.|int\.|num\.|det\.)", l)
            if pm2:
                defs.append(l)
                continue
            
            # Example sentence
            if re.match(r"^\d+[.)]\s", l):
                sents.append({"sentence": re.sub(r"^\d+[.)]\s*", "", l).strip(), "translation": "", "source": ""})
                continue
            
            if l.startswith("参考译文"):
                if sents: sents[-1]["translation"] = l.replace("参考译文", "").strip()
                continue
            
            if l.startswith(("真题例句", "助记", "拓展", "拓展：", "章节索引")):
                continue
            
            # Extension
            em = re.match(r"^([a-z][a-z\'\-]+)\s+(n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)", l)
            if em:
                ew = em.group(1).lower()
                if ew != w:
                    exts.append({"word": ew, "meaning": re.sub(r"^\S+\s+", "", l, count=1).strip()})
                continue
            
            # Memory aid
            if "=" in l and len(l) > 8 and not l.startswith("考研"):
                mem = (mem + " " + l).strip()
                continue
        
        entry = {
            "english": w,
            "phonetic": ph,
            "definitions": defs,
            "exam_sentences": sents,
            "extensions": exts,
            "memory_aid": mem,
            "phrases": []
        }
        all_entries[w] = entry

# Group by unit
all_units = []
total = 0
for uid_str, words in unit_words.items():
    uid = int(uid_str)
    ws = [all_entries[w] for w in words if w in all_entries]
    all_units.append({"id": uid, "title": f"Unit {uid}", "words": [{"id": i+1, **w} for i, w in enumerate(ws)]})
    total += len(ws)
    has_def = sum(1 for w in ws if w.get("definitions"))
    print(f"Unit {uid}: {len(ws)}/{len(words)} 词 ({has_def}有释义)")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"name": "考研英语串词记忆", "version": "1.0", "total_units": len(all_units), "units": all_units}, f, ensure_ascii=False, indent=2)
print(f"\n总计 {total} 词")
