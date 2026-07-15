// ==================== 单词书模块 ====================
// 将 wordbook.json 转换为 app 可用的列表格式

export let wordbookLoaded = false;

export async function loadWordbook() {
  try {
    const r = await fetch('data/wordbook.json');
    const wb = await r.json();
    return wb;
  } catch (e) {
    console.error('单词书加载失败:', e);
    return null;
  }
}

/** 将单词书单元转换为 app 列表格式 */
export function unitToList(unit) {
  return {
    name: unit.title,
    words: unit.words.map(w => ({
      english: w.english,
      chinese: (w.definitions || []).join('；'),
      phonetic: (w.phonetic && (w.phonetic.us || w.phonetic.uk))
        ? [w.phonetic.us, w.phonetic.uk].filter(Boolean).join(' ')
        : '',
      example: (w.exam_sentences || []).map(s => s.sentence).join('\n'),
      exampleCN: (w.exam_sentences || []).map(s => s.translation || '').filter(Boolean).join('\n'),
      note: w.memory_aid || '',
      extensions: w.extensions || [],
      // SM-2 默认值
      easeFactor: 2.5, interval: 0, repetitions: 0,
      nextReview: null, lastReview: null,
      // FSRS 默认值
      stability: 0, difficulty: 0, fsrsState: 0, fsrsReps: 0, fsrsLastReview: null,
      passed: false, starred: false
    })),
    ecMistakes: [],
    ceMistakes: []
  };
}
