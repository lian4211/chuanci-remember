#!/usr/bin/env python3
"""
chuanci-remember: 从 docx 提取考研英语串词记忆数据
"""
import docx
import json
import re
import os

DOCX_PATH = "C:/Users/a1370/Desktop/扫描书籍_章节索引(1).docx"
OUTPUT_DIR = "C:/Users/a1370/chuanci-remember/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

doc = docx.Document(DOCX_PATH)
paras = [p.text.strip() for p in doc.paragraphs]

# =========== 第一步：按 Unit 分割 ===========
units_raw = {}
current_unit = None
current_lines = []

for t in paras:
    m = re.match(r'^Unit\s+(\d+)$', t)
    if m:
        if current_unit:
            units_raw[current_unit] = current_lines
        current_unit = int(m.group(1))
        current_lines = []
    else:
        if current_unit is not None and t:
            current_lines.append(t)

if current_unit is not None:
    units_raw[current_unit] = current_lines

print(f"找到 {len(units_raw)} 个单元: {sorted(units_raw.keys())}")

# =========== 第二步：从每单元文本提取单词 ===========
def extract_words(lines):
    """从段落列表中提取单词条目"""
    words = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 检测单词行：英文单词开头，后跟中文或POS
        m = re.match(r'^([a-zA-Z][a-zA-Z\-\'\.]+)\s+', line)
        if m:
            word = m.group(1).lower()
            rest = line[len(word):].strip()

            # 跳过章节索引行
            if '章节索引' in line:
                i += 1
                continue

            entry = {
                "english": word,
                "definitions": [],
                "exam_sentences": [],
                "extensions": [],
                "memory_aid": "",
                "phrases": [],
                "collocations": [],
                "word_chain": ""
            }

            # 提取定义行（连续的行，以n./v./adj./adv./prep.等开头）
            while i < len(lines):
                curr = lines[i]
                # 检查是否是定义行
                pos_m = re.match(
                    r'^((?:n\.|v\.|vt\.|vi\.|adj\.|adv\.|prep\.|conj\.|pron\.|interj\.|art\.|num\.|det\.|int\.|abbr\.|pl\.|sing\.)\s*.*?)(?=\s*(?:真题例句|参考译文|拓展|助记|串词|搭配|$))',
                    curr
                )
                if pos_m and len(curr) > 3:
                    # 这行是定义
                    entry["definitions"].append(curr)
                    i += 1
                    continue

                # 真题例句
                if curr == '真题例句':
                    i += 1
                    # 读取例句（编号1. 2. 3.）
                    while i < len(lines):
                        sent_line = lines[i]
                        # 检测例句行
                        sent_m = re.match(r'^(\d+)[.)]\s*(.+?)(?:\(\d{4}\s*年.*?\))?$', sent_line)
                        if sent_m:
                            sent_text = sent_m.group(2).strip()
                            entry["exam_sentences"].append({
                                "sentence": sent_text,
                                "source": ""
                            })
                            i += 1
                            # 读取参考译文（下一行是参考译文）
                            if i < len(lines) and lines[i].startswith('参考译文'):
                                entry["exam_sentences"][-1]["translation"] = lines[i].replace('参考译文', '').strip()
                                i += 1
                            continue
                        # 检测下一标题
                        if curr in ('拓展', '助记', '串词', '搭配') or re.match(r'^[a-z]', sent_line):
                            break
                        # 检测年份来源
                        year_m = re.search(r'(\(\d{4}\s*年.*?\))', sent_line)
                        if year_m and entry["exam_sentences"]:
                            entry["exam_sentences"][-1]["source"] = year_m.group(1)
                            # 这行可能也有例句文本
                            before_year = sent_line[:year_m.start()].strip()
                            if before_year and len(before_year) > 5:
                                entry["exam_sentences"][-1]["sentence"] = before_year
                            i += 1
                            continue
                        i += 1
                    continue

                # 拓展
                if curr.startswith('拓展'):
                    i += 1
                    while i < len(lines):
                        ext_line = lines[i]
                        if re.match(r'^[a-z]', ext_line) and not ext_line.startswith('参考译文'):
                            # 拓展词行
                            ext_m = re.match(r'^([a-zA-Z][a-zA-Z\-\'\.\s]+?)\s{2,}(.+)$', ext_line)
                            if not ext_m:
                                ext_m = re.match(r'^([a-zA-Z][a-zA-Z\-\'\.]+)\s+(.+)$', ext_line)
                            if ext_m:
                                entry["extensions"].append({
                                    "word": ext_m.group(1).strip(),
                                    "meaning": ext_m.group(2).strip()
                                })
                            else:
                                # 短语行 (如 "child labor 童工")
                                phrase_m = re.match(r'^([a-zA-Z\s]+?)\s+([\u4e00-\u9fff].+)$', ext_line)
                                if phrase_m:
                                    entry["phrases"].append({
                                        "phrase": phrase_m.group(1).strip(),
                                        "meaning": phrase_m.group(2).strip()
                                    })
                            i += 1
                        else:
                            break
                    continue

                # 助记
                if curr.startswith('助记') or curr.startswith('串词'):
                    key = 'memory_aid' if curr.startswith('助记') else 'word_chain'
                    i += 1
                    if i < len(lines):
                        entry[key] = lines[i]
                        i += 1
                    continue

                # 搭配
                if curr.startswith('搭配'):
                    i += 1
                    while i < len(lines):
                        coll_line = lines[i]
                        coll_m = re.match(r'^([a-zA-Z\s]+?)\s+([\u4e00-\u9fff].+)$', coll_line)
                        if coll_m:
                            entry["collocations"].append({
                                "text": coll_m.group(1).strip(),
                                "meaning": coll_m.group(2).strip()
                            })
                            i += 1
                        else:
                            break
                    continue

                # 下一个单词（英文开头）
                if re.match(r'^[a-zA-Z][a-zA-Z\-\']+\s', curr) and len(curr.split()[0]) > 1:
                    break

                i += 1

            # 过滤掉章节索引中的行
            if not entry["definitions"] and not entry["exam_sentences"] and not entry["extensions"]:
                word = None
            else:
                words.append(entry)

        i += 1

    return words

all_units = []
for unit_id in sorted(units_raw.keys()):
    lines = units_raw[unit_id]
    words = extract_words(lines)
    all_units.append({
        "id": unit_id,
        "title": f"Unit {unit_id}",
        "words": [{"id": j+1, **w} for j, w in enumerate(words)]
    })
    print(f"Unit {unit_id}: {len(words)} 词")

# 生成 wordbook.json
wordbook = {
    "name": "考研英语串词记忆",
    "version": "1.0",
    "total_units": len(all_units),
    "units": all_units
}

output_path = os.path.join(OUTPUT_DIR, "wordbook.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(wordbook, f, ensure_ascii=False, indent=2)

total = sum(len(u["words"]) for u in all_units)
print(f"\n总共: {total} 词, {len(all_units)} 单元")
print(f"输出: {output_path}")
