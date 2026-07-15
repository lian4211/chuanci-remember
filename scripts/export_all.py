import json

WB = "C:/Users/a1370/chuanci-remember/data/wordbook.json"
OUT = "C:/Users/a1370/Desktop/ai_fix_batch.json"

with open(WB, encoding="utf-8") as f:
    wb = json.load(f)

# Export all words with definitions for AI review
items = []
for u in wb["units"]:
    for w in u["words"]:
        items.append({
            "unit": u["title"],
            "word": w["english"],
            "definition": (w.get("definitions") or [""])[0],
            "phonetic": w.get("phonetic", {}),
            "examples": [s["sentence"][:100] for s in (w.get("exam_sentences") or [])[:2]],
            "extensions": [e["word"] for e in (w.get("extensions") or [])[:3]],
            "memory_aid": (w.get("memory_aid") or "")[:100]
        })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"导出 {len(items)} 词到桌面")
