import json

with open("C:/Users/a1370/chuanci-remember/data/wordbook.json", encoding="utf-8") as f:
    wb = json.load(f)

print(f"总计: {sum(len(u['words']) for u in wb['units'])} 词, {len(wb['units'])} 单元")
for u in wb['units'][:5]:
    w = u['words']
    print(f"\n{u['title']} ({len(w)}词): {w[0]['english']} ~ {w[-1]['english']}")
    fw = w[0]
    print(f"  defs={len(fw.get('definitions',[]))} sents={len(fw.get('exam_sentences',[]))} exts={len(fw.get('extensions',[]))}")
    for d in fw.get('definitions',[])[:2]:
        print(f"  def: {d[:80]}")
    if fw.get('exam_sentences'):
        print(f"  sent: {fw['exam_sentences'][0]['sentence'][:60]}")
    if fw.get('extensions'):
        print(f"  ext: {fw['extensions'][0]['word']} - {fw['extensions'][0]['meaning'][:40]}")
