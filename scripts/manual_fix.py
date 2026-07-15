import json

WB = "C:/Users/a1370/chuanci-remember/data/wordbook.json"
FIXES = {}

# 手工矫正明显错误的词性和释义
FIXES = {
    # 词性错误
    "adversarial": "adj. 敌对的；对立的",
    "avert": "v. 转移；防止",
    "controversial": "adj. 有争议的；引起争议的",
    "conversation": "n. 对话；交谈；会话",
    "convert": "vt. 使转变；转换；使改变信仰",
    "disorder": "n. 混乱；杂乱；失调",
    "margin": "n. 边缘；余地；幅度",
    "remark": "n. 评论；v. 评论；注意到",
    "reverse": "v. 颠倒；逆转；adj. 相反的；n. 反面",
    "versatile": "adj. 多才多艺的；多功能的",
    "deport": "v. 驱逐出境；举止",
    "collaborative": "adj. 合作的；协作的",
    "diversity": "n. 多样性；差异",
    "log": "n. 原木；日志；记录",
    "march": "n. 三月；行军；示威游行",
    "subordinate": "adj. 从属的；次要的；n. 下属",
    "verse": "n. 诗句；韵文",
    "avert": "v. 转移；防止，避免",
    "catalogue": "n. 目录；一系列",
    "airport": "n. 机场；航空站",
    "aspire": "v. 渴望；追求；有志于",
    "conspire": "v. 共谋；密谋；协同",
    "perspire": "v. 出汗；流汗；排汗",
    "respire": "v. 呼吸；恢复精神",
    "volunteer": "n. 志愿者；v. 自愿",
    "portable": "adj. 便携的；手提的；轻便的",
    "spirit": "n. 精神；心灵；勇气",
    "support": "v./n. 支持；支援；维持",
    "report": "v. 报告；汇报；n. 报告",
    "despair": "n. 绝望；v. 绝望",
    "desperate": "adj. 绝望的；不顾一切的",
    "prosper": "v. 繁荣；成功；兴旺",
    "expire": "v. 期满；终止；死亡",
    "port": "n. 港口；口岸",
    "opportunity": "n. 机会；时机",
    "memorial": "n. 纪念碑；纪念物；adj. 纪念的",
    "acentric": "adj. 无中心的；偏心的",
    "afford": "v. 负担得起；提供",
    "appetite": "n. 食欲；胃口；欲望",
    "concentrate": "v. 集中；专注；浓缩",
    "consolidate": "v. 巩固；合并；统一",
    "corroborate": "v. 证实；确证",
    "decentralize": "v. 分散；下放权力",
    "enforce": "v. 实施；执行；强制",
    "expenditure": "n. 支出；花费；消费",
    "expense": "n. 费用；代价；开支",
    "pedagogy": "n. 教育学；教学法",
    "solar": "adj. 太阳的；日光的",
    "solidarity": "n. 团结；团结一致",
    "solitary": "adj. 孤独的；独居的",
    "incentive": "n. 激励；刺激；动力",
    "antipathy": "n. 反感；厌恶",
    "apathy": "n. 冷漠；漠不关心",
    "catastrophe": "n. 灾难；灾祸",
    "preclude": "v. 排除；阻止；妨碍",
    "enchant": "v. 使迷醉；施魔法",
    "artifact": "n. 人工制品；手工艺品",
    "asymmetry": "n. 不对称",
    "deficit": "n. 赤字；逆差；不足",
    "facility": "n. 设施；设备；天赋",
    "simile": "n. 明喻",
    "symmetry": "n. 对称；匀称",
    "symphony": "n. 交响乐；交响曲",
    "demography": "n. 人口统计学",
    "epidemic": "n. 流行病；adj. 流行的",
    "pandemic": "n. 大流行病；adj. 大流行的",
    "essence": "n. 本质；实质；精华",
    "malformed": "adj. 畸形的；变形的",
    "nonsense": "n. 胡说；废话",
    "popularize": "v. 推广；普及；使流行",
    "simulate": "v. 模拟；模仿；假装",
    "catastrophe": "n. 灾难；灾祸",
    "universe": "n. 宇宙；天地万物；领域",
    "versus": "prep. 对；相对；与...相比",
    "quintessence": "n. 精华；典型；典范",
    "deceive": "v. 欺骗；蒙蔽",
    "exhume": "v. 掘出；发掘",
    "perceive": "v. 察觉；理解；认知",
    "underlie": "v. 构成...的基础；位于...之下",
    "underline": "v. 在...下面划线；强调",
    "underrate": "v. 低估；轻视",
    "undertake": "v. 承担；从事；保证",
    "underutilize": "v. 未充分利用",
    "discount": "n. 折扣；v. 打折；不重视",
    "conquest": "n. 征服；战胜；战利品",
    "increase": "v./n. 增加；增长",
    "recreate": "v. 再创造；重现；娱乐",
    "defame": "v. 诽谤；诋毁",
    "liability": "n. 责任；债务；不利因素",
    "disprove": "v. 反驳；证明...为假",
    "inspect": "v. 检查；审视",
    "agenda": "n. 议程；议事日程",
    "agency": "n. 机构；代理处",
    "agent": "n. 代理人；代理商；特工",
    "agile": "adj. 敏捷的；灵活的",
    "decadent": "adj. 颓废的；衰退的",
    "simultaneous": "adj. 同时的；同步的",
    "synchronous": "adj. 同步的；同时的",
}

with open(WB, encoding="utf-8") as f:
    wb = json.load(f)

fixed = 0
for u in wb["units"]:
    for w in u["words"]:
        if w["english"] in FIXES:
            w["definitions"] = [FIXES[w["english"]]]
            fixed += 1

with open(WB, "w", encoding="utf-8") as f:
    json.dump(wb, f, ensure_ascii=False, indent=2)

print(f"手工矫正 {fixed} 词")
