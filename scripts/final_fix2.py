import json
with open("C:/Users/a1370/chuanci-remember/data/wordbook.json", encoding="utf-8") as f:
    wb = json.load(f)

FIXES = {
    "universe": "n. 宇宙；天地万物；领域",
    "versus": "prep. 对；对抗；与...相比；vs.",
    "discount": "n. 折扣；v. 打折；不重视",
    "underlie": "v. 构成...的基础；位于...之下",
    "underline": "v. 在...下面划线；强调",
    "underrate": "v. 低估；轻视",
    "undertake": "v. 承担；从事；保证",
    "underutilize": "v. 未充分利用",
    "catalogue": "n. 目录；一系列；v. 编入目录",
    "diversity": "n. 多样性；差异；多样化",
    "airport": "n. 机场；航空站",
}

for u in wb["units"]:
    for w in u["words"]:
        if w["english"] in FIXES:
            w["definitions"] = [FIXES[w["english"]]]

with open("C:/Users/a1370/chuanci-remember/data/wordbook.json", "w", encoding="utf-8") as f:
    json.dump(wb, f, ensure_ascii=False, indent=2)
print("done")
