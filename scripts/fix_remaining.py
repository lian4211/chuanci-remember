import json
with open("C:/Users/a1370/chuanci-remember/data/wordbook.json", encoding="utf-8") as f:
    wb = json.load(f)

FIXES = {
    "versus": "prep. 对；对抗；与…相对；vs.",
    "discount": "n. 折扣；v. 打折；不重视",
}

for u in wb["units"]:
    for w in u["words"]:
        if w["english"] in FIXES:
            w["definitions"] = [FIXES[w["english"]]]

still = []
for u in wb["units"]:
    for w in u["words"]:
        if not w.get("definitions"):
            still.append(f"{u['title']}:{w['english']}")

with open("C:/Users/a1370/chuanci-remember/data/wordbook.json", "w", encoding="utf-8") as f:
    json.dump(wb, f, ensure_ascii=False, indent=2)
print(f"仍缺 {len(still)}: {', '.join(still[:20])}")
