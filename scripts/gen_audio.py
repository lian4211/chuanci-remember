#!/usr/bin/env python3
"""生成所有单词的 MP3 音频文件"""
import json, os, asyncio
import edge_tts

WB = "C:/Users/a1370/chuanci-remember/data/wordbook.json"
AUDIO_DIR = "C:/Users/a1370/chuanci-remember/data/audio"
MAPPING = "C:/Users/a1370/chuanci-remember/data/audio_map.json"

with open(WB, encoding="utf-8") as f:
    wb = json.load(f)

os.makedirs(AUDIO_DIR, exist_ok=True)

# Collect unique words
words = []
for u in wb["units"]:
    for w in u["words"]:
        words.append(w["english"])

# Deduplicate
words = list(dict.fromkeys(w.lower() for w in words))
print(f"需要生成: {len(words)} 个音频")

VOICE = "en-US-JennyNeural"

async def generate_one(word):
    filename = word.replace("'", "_").replace("-", "_") + ".mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(filepath):
        return word, filename  # Already exists
    try:
        communicate = edge_tts.Communicate(word, VOICE)
        await communicate.save(filepath)
        return word, filename
    except Exception as e:
        print(f"  FAIL: {word} - {e}")
        return word, None

async def main():
    mapping = {}
    # Process in batches to avoid overwhelming the API
    batch_size = 20
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        tasks = [generate_one(w) for w in batch]
        results = await asyncio.gather(*tasks)
        for word, filename in results:
            if filename:
                mapping[word] = filename
        print(f"  进度: {min(i+batch_size, len(words))}/{len(words)} ({len(mapping)}成功)")
    
    # Save mapping
    with open(MAPPING, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"完成! {len(mapping)}/{len(words)} 词")

asyncio.run(main())
