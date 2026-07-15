import json, re

WB = "C:/Users/a1370/chuanci-remember/data/wordbook.json"
CTX = "C:/Users/a1370/Desktop/missing_words_context.json"

with open(WB, encoding="utf-8") as f:
    wb = json.load(f)
with open(CTX, encoding="utf-8") as f:
    ctx_data = json.load(f)

# Build context lookup
ctx_map = {item["word"]: item["contexts"] for item in ctx_data}

# Find all words with issues and dump for AI review
issues = []
for u in wb["units"]:
    for w in u["words"]:
        word = w["english"]
        defs = w.get("definitions", [])
        if not defs:
            issues.append((u["title"], word, "无释义", ""))
            continue
        d = defs[0]
        # Check for obvious issues
        if "(ai)" in d:
            issues.append((u["title"], word, "AI推断", d[:60]))
        elif "形容词词性" in d or "动词词性" in d or "名词词性" in d:
            issues.append((u["title"], word, "词根词性", d[:60]))
        elif d.startswith(("英/", "美/")) or "'" in d[:5]:
            issues.append((u["title"], word, "仅音标", d[:60]))
        elif re.match(r"^adj\.|^adv\.|^n\.|^v\.", d):
            # Has POS - might still be wrong POS
            # Flag all POS-only definitions for review
            issues.append((u["title"], word, "有词性", d[:60]))
        elif len(d) <= 3:
            issues.append((u["title"], word, "过短", d[:60]))

print(f"待检查: {len(issues)} 词")
print()
for u, w, reason, d in issues[:40]:
    ctx = ctx_map.get(w, [])
    ctx_str = " | ".join(c[:80] for c in ctx[:2]) if ctx else ""
    print(f"  [{reason}] {u} {w}: {d}")
    if ctx_str:
        print(f"    上下文: {ctx_str}")
