// ==================== 串词记忆闪卡模块 (v3) ====================
// 三档记忆：完全记住了 / 有印象 / 没印象
// SM-2 算法简化版

let _fcState = null;

export function startWordbookFlashcard(words, startIdx) {
  _fcState = { items: words, index: startIdx || 0 };
  window.goToPage('flashcard');
  renderCard();
}

function renderCard() {
  if (!_fcState) return;
  const { items, index } = _fcState;
  if (index >= items.length) {
    document.getElementById('flashcard-content').innerHTML =
      '<div style="text-align:center;padding:3rem"><p style="font-size:3rem">🎉</p><p style="font-size:1.2rem">全部完成!</p></div>';
    return;
  }
  
  const word = items[index];
  const ph = (word.phonetic && (word.phonetic.us || word.phonetic.uk))
    ? [word.phonetic.us, word.phonetic.uk].filter(Boolean).join(' ') : '';
  const defs = (word.definitions || []).join('<br>');
  const sents = (word.exam_sentences || []).map(s =>
    `<div class="fc-sent"><p class="fc-sent-en">${esc(s.sentence)}</p>` +
    (s.translation ? `<p class="fc-sent-cn">${esc(s.translation)}</p>` : '') +
    (s.source ? `<p class="fc-sent-src">— ${esc(s.source)}</p>` : '') +
    `</div>`
  ).join('');
  const exts = (word.extensions || []).map(e =>
    `<span class="fc-ext">${esc(e.word)} ${esc(e.meaning)}</span>`
  ).join(' ');
  
  const container = document.getElementById('flashcard-content');
  container.innerHTML = `
    <div class="fc-wrap">
      <div class="fc-en">${esc(word.english)}</div>
      ${ph ? `<div class="fc-ph">${esc(ph)}</div>` : ''}
      <div class="fc-def">${defs}</div>
      ${sents ? `<div class="fc-sents"><div class="fc-section-label">例句</div>${sents}</div>` : ''}
      ${exts ? `<div class="fc-exts"><div class="fc-section-label">拓展</div>${exts}</div>` : ''}
      <div class="fc-btns">
        <button class="fc-btn fc-btn-3" onclick="window._fcGrade(3)">😞 没印象</button>
        <button class="fc-btn fc-btn-2" onclick="window._fcGrade(2)">🤔 有印象</button>
        <button class="fc-btn fc-btn-1" onclick="window._fcGrade(1)">✅ 完全记住了</button>
      </div>
      <div class="fc-progress">${index + 1} / ${items.length}</div>
    </div>
  `;
  
  window._fcGrade = (grade) => {
    sm2Update(word, grade);
    _fcState.index++;
    renderCard();
  };
}

function sm2Update(word, grade) {
  // grade: 1=完美 2=有印象 3=没印象
  const q = word._sm2 || { ef: 2.5, interval: 0, reps: 0, nextReview: 0 };
  
  if (grade === 1) { // 完全记住了
    q.reps++;
    if (q.reps === 1) q.interval = 1;
    else if (q.reps === 2) q.interval = 6;
    else q.interval = Math.round(q.interval * q.ef);
    q.ef = q.ef + (0.1 - (3 - grade) * (0.08 + (3 - grade) * 0.02));
  } else if (grade === 2) { // 有印象
    q.reps = Math.max(0, q.reps - 1);
    q.interval = 1;
    q.ef = Math.max(1.3, q.ef - 0.2);
  } else { // 没印象
    q.reps = 0;
    q.interval = 1;
    q.ef = Math.max(1.3, q.ef - 0.5);
  }
  
  if (q.ef < 1.3) q.ef = 1.3;
  q.nextReview = Date.now() + q.interval * 86400000;
  word._sm2 = q;
  
  // Save to localStorage
  try {
    const key = 'wb_sm2_' + word.english;
    localStorage.setItem(key, JSON.stringify(q));
  } catch(e) {}
}

// 从localStorage加载记忆状态
export function loadSM2(word) {
  try {
    const key = 'wb_sm2_' + word.english;
    const d = localStorage.getItem(key);
    if (d) word._sm2 = JSON.parse(d);
  } catch(e) {}
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
