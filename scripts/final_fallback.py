import json

WB = "C:/Users/a1370/chuanci-remember/data/wordbook.json"
CTX = "C:/Users/a1370/chuanci-remember/data/word_contexts.json"
IDX = "C:/Users/a1370/chuanci-remember/data/index_words.json"

with open(WB, encoding="utf-8") as f:
    wb = json.load(f)
with open(CTX, encoding="utf-8") as f:
    ctxs = json.load(f)
with open(IDX, encoding="utf-8") as f:
    unit_words = json.load(f)

# Known word-chainer meanings from context
FALLBACK = {
    "centre": "n. 中心；中央；v. 以…为中心",
    "comfort": "n. 舒适；安慰；v. 安慰",
    "compete": "v. 竞争；比赛；对抗",
    "desolate": "adj. 荒凉的；无人烟的",
    "force": "n. 力；力量；军队；v. 强迫",
    "fort": "n. 堡垒；要塞",
    "indispensable": "adj. 不可或缺的；必需的",
    "pedagogy": "n. 教育学；教学法",
    "pedal": "n. 踏板；v. 踩踏板",
    "pedestrian": "n. 行人；adj. 徒步的",
    "pension": "n. 退休金；抚恤金",
    "perpetual": "adj. 永久的；不断的",
    "roborant": "n. 强壮剂；adj. 增强体力的",
    "robust": "adj. 强健的；稳固的",
    "corroborate": "v. 证实；确证",
    "sole": "adj. 唯一的；独占的",
    "solo": "n. 独奏；独唱；adj. 单独的",
    "solar": "adj. 太阳的；日光的",
    "solitude": "n. 孤独；独居",
    "solitary": "adj. 孤独的；独居的",
    "operation": "n. 运作；操作；手术；运营",
    "inspire": "v. 激励；鼓舞；赋予灵感",
    "memo": "n. 备忘录；便笺",
    "fortify": "v. 加强；巩固",
    "fortitude": "n. 坚韧；刚毅",
    "consolable": "adj. 可安慰的",
    "soothe": "v. 安慰；缓和",
    "discourage": "v. 使泄气；劝阻",
    "stimulate": "v. 刺激；激励",
    "pen-pal": "n. 笔友",
    "accentuate": "v. 强调；重读",
    "chant": "n. 圣歌；v. 吟唱",
    "chant": "n. 圣歌；v. 反复唱",
    "strive": "v. 努力；奋斗",
    "expanse": "n. 广阔；浩瀚",
    "atlas": "n. 地图集；图谱",
    "spacious": "adj. 宽敞的；广阔的",
    "extraterrestrial": "adj. 地球外的；外星人",
    "terrain": "n. 地形；地势",
    "territory": "n. 领土；领域",
    "terrestrial": "adj. 陆地的；地球的",
    "mediterranean": "adj. 地中海的",
    "subterranean": "adj. 地下的；隐秘的",
    "inter": "v. 埋葬；埋藏",
    "interment": "n. 埋葬；葬礼",
}

fixed = 0
for u in wb["units"]:
    for w in u["words"]:
        if w.get("definitions"):
            continue
        wl = w["english"].lower()
        if wl in FALLBACK:
            w["definitions"] = [FALLBACK[wl]]
            fixed += 1
        elif wl in ctxs and ctxs[wl].get("found"):
            ctx = ctxs[wl]["context"]
            # Try to extract any meaningful Chinese from context
            import re
            for m in re.finditer(r"(n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)([^。\n]{3,40})", ctx):
                rest = m.group(2).strip()
                if re.search(r"[\u4e00-\u9fff]", rest):
                    w["definitions"].append(m.group(1) + " " + rest)
                    fixed += 1
                    break

still_no = sum(1 for u in wb["units"] for w in u["words"] if not w.get("definitions"))
print(f"补全 {fixed} 词, 仍缺 {still_no}")

with open(WB, "w", encoding="utf-8") as f:
    json.dump(wb, f, ensure_ascii=False, indent=2)
