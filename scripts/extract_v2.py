#!/usr/bin/env python3
"""
Chuanci Remember — docx 解析器 v2
处理分栏截断、跨行词条、拓展词识别
"""
import docx, json, re, os
from collections import OrderedDict

DOCX = "C:/Users/a1370/Desktop/扫描书籍_章节索引(1).docx"
OUT = "C:/Users/a1370/chuanci-remember/data/wordbook.json"

doc = docx.Document(DOCX)
text = "\n".join(p.text for p in doc.paragraphs)

# 按 Unit 分割
units_raw = re.split(r'\nUnit (\d+)\n', text)[1:]  # [num, content, num, content, ...]
units = OrderedDict()
for i in range(0, len(units_raw), 2):
    units[int(units_raw[i])] = units_raw[i+1].strip()

print(f"找到 {len(units)} 个单元")

# 清理噪音行
def clean_line(l):
    l = l.strip()
    if not l: return ""
    if '考研英语申词记忆' in l or '考研英语串词记忆' in l: return ""
    if l == '章节索引': return ""
    # 去除页码
    if re.match(r'^\d{1,3}$', l): return ""
    return l

def extract_words_from_unit(text):
    """从单元文本中提取单词"""
    lines = [clean_line(l) for l in text.split('\n') if clean_line(l)]
    
    words = []
    i = 0
    seen = set()
    
    while i < len(lines):
        line = lines[i]
        
        # 检测英文单词开头行（词条起始）
        m = re.match(r'^([a-zA-Z][a-zA-Z\'\-]+)\s', line)
        if not m:
            i += 1
            continue
        
        word = m.group(1).lower()
        rest = line[len(word):].strip()
        
        # 跳过纯索引行（"labor 劳动"格式，且后无POS行）
        if rest and not re.search(r'(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.)', rest) \
           and not re.search(r'[/ˈ]', rest):
            # 检查下一行是否是POS行
            if i+1 < len(lines) and re.match(r'^(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.)', lines[i+1]):
                pass  # 这是真词条
            elif i+1 < len(lines) and '/' in lines[i+1]:
                pass  # 音标行
            else:
                # 可能是章节索引中的快速索引行
                i += 1
                continue
        
        if word in seen:
            i += 1
            continue
            
        entry = {
            "english": word,
            "definitions": [],
            "phonetic": {"us": "", "uk": ""},
            "exam_sentences": [],
            "extensions": [],
            "memory_aid": "",
            "phrases": [],
            "word_chain": ""
        }
        
        # 收集本词条所有内容，直到遇到下一个单词或空段
        j = i + 1
        block_lines = []
        while j < len(lines):
            next_line = lines[j]
            # 下一个单词起始
            if re.match(r'^[a-zA-Z][a-zA-Z\'\-]+\s', next_line):
                nword = re.match(r'^([a-zA-Z][a-zA-Z\'\-]+)\s', next_line).group(1).lower()
                # 检查下一行确定是否为真词条
                if j+1 < len(lines):
                    next_next = lines[j+1]
                    if re.match(r'^(?:n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.|[/ˈ])', next_next) or \
                       re.match(r'^(?:真题例句|拓展|助记)', next_next):
                        break
            if next_line.startswith('Unit ') and re.match(r'^Unit \d+$', next_line):
                break
            block_lines.append(next_line)
            j += 1
        
        # 解析收集到的块
        for bl in block_lines:
            # 音标
            ph_m = re.search(r'[/][^/]+[/]', bl)
            if ph_m and not entry["phonetic"]["us"]:
                entry["phonetic"]["us"] = ph_m.group()
            
            # 定义行 (POS开头)
            if re.match(r'^(?:n\.|v\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.|vt\.|vi\.|abbr\.|int\.|num\.|det\.|pl\.|sing\.)', bl):
                if bl not in entry["definitions"]:
                    entry["definitions"].append(bl)
            # 真题例句
            elif bl.startswith('真题例句'):
                pass
            elif re.match(r'^\d+[.)]\s', bl):
                # 例句行
                sent_text = re.sub(r'^\d+[.)]\s*', '', bl).strip()
                entry["exam_sentences"].append({"sentence": sent_text, "translation": "", "source": ""})
            elif bl.startswith('参考译文'):
                if entry["exam_sentences"]:
                    entry["exam_sentences"][-1]["translation"] = bl.replace('参考译文', '').strip()
            # 年份来源
            elif re.search(r'\(\d{4}\s*年', bl):
                if entry["exam_sentences"]:
                    entry["exam_sentences"][-1]["source"] = bl
                    # 可能也有例句文本
            # 拓展
            elif bl.startswith('拓展') or bl.startswith('拓展：'):
                pass
            elif re.match(r'^[a-zA-Z][a-zA-Z\'\-]+\s+(?:n\.|v\.|adj\.|adv\.|prep\.|vt\.|vi\.)', bl):
                if entry["extensions"] or True:  # 是拓展词
                    ext_m = re.match(r'^([a-zA-Z][a-zA-Z\'\-]+)\s+(.+)', bl)
                    if ext_m:
                        ew = ext_m.group(1).lower()
                        if ew != word:
                            entry["extensions"].append({"word": ew, "meaning": ext_m.group(2).strip()})
            # 短语 (英文+中文)
            elif re.match(r'^[a-zA-Z\s]+\s+[\u4e00-\u9fff]', bl):
                if not re.match(r'^[a-z]', bl.split()[0]) or len(bl) < 5:
                    pass
                elif not re.search(r'[/ˈ]', bl) and not bl.startswith(('美', '英')):
                    entry["phrases"].append({"phrase": bl.split()[0] if ' ' not in bl else bl[:bl.index(' ')], "meaning": bl})
            # 助记
            elif '=' in bl and len(bl) > 10:
                entry["memory_aid"] = bl
        
        # 清理空音标
        if not entry["phonetic"]["us"] and not entry["phonetic"]["uk"]:
            entry["phonetic"] = {}
        
        # 只保留有定义的词
        if entry["definitions"] or entry["exam_sentences"]:
            seen.add(word)
            words.append(entry)
        
        i = j
    
    return words

all_units = []
total_words = 0
for uid in sorted(units.keys()):
    words = extract_words_from_unit(units[uid])
    all_units.append({
        "id": uid,
        "title": f"Unit {uid}",
        "words": [{"id": j+1, **w} for j, w in enumerate(words)]
    })
    total_words += len(words)
    print(f"Unit {uid}: {len(words)} 词")

wb = {
    "name": "考研英语串词记忆",
    "version": "1.0",
    "total_units": len(all_units),
    "units": all_units
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(wb, f, ensure_ascii=False, indent=2)

print(f"\n总共 {total_words} 词, {len(all_units)} 单元")
