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
  const wb = window._wbWordbook;
  const rawWord = findRawWord(word.english);

  // Parse sentences from app format (example + exampleCN multiline)
  const sents = [];
  if (word.example) {
    const lines = word.example.split('\n').filter(Boolean);
    const transLines = (word.exampleCN || '').split('\n').filter(Boolean);
    lines.forEach((sen, i) => {
      sents.push({
        sentence: sen,
        translation: transLines[i] || '',
        source: ''
      });
    });
  }
  // Fallback to raw wordbook format
  if (sents.length === 0 && rawWord && rawWord.exam_sentences) {
    rawWord.exam_sentences.forEach(s => sents.push(s));
  }

  const sentsHtml = sents.map(s =>
    `<div class="fc-sent">
      <p class="fc-sent-en">${esc(s.sentence)}</p>
      ${s.translation ? `<p class="fc-sent-cn">${esc(s.translation)}</p>` : ''}
      ${s.source ? `<p class="fc-sent-src">— ${esc(s.source)}</p>` : ''}
    </div>`
  ).join('');

  // Parse extensions
  let exts = word.extensions || [];
  if (exts.length === 0 && rawWord && rawWord.extensions) {
    exts = rawWord.extensions;
  }
  const extsHtml = exts.map(e =>
    `<div class="fc-ext-item"><span class="fc-ext-word">${esc(e.word)}</span> ${esc(e.meaning || '')}</div>`
  ).join('');

  const ph = word.phonetic || '';
  const defs = word.chinese || '';
  const note = word.note || '';
  const hasSents = sents.length > 0;
  const hasExts = exts.length > 0;

  const container = document.getElementById('flashcard-content');
  container.innerHTML = `
    <div class="fc-wrap">
      <div class="fc-card-main">
        <div class="fc-en">${esc(word.english)}</div>
        ${ph ? `<div class="fc-ph">${esc(ph)}</div>` : ''}
        <div class="fc-def">${esc(defs)}</div>
        <button class="fc-voice-btn" onclick="window._fcPlayVoice()">🔊 朗读</button>
      </div>

      ${hasSents ? `
      <div class="fc-section">
        <div class="fc-section-label">📝 真题例句</div>
        ${sentsHtml}
      </div>` : ''}

      ${hasExts ? `
      <div class="fc-section">
        <div class="fc-section-label">🔗 拓展词汇</div>
        <div class="fc-exts">${extsHtml}</div>
      </div>` : ''}

      ${note ? `<div class="fc-note">💡 ${esc(note)}</div>` : ''}

      <div class="fc-btns">
        <button class="fc-btn fc-btn-3" onclick="window._fcGrade(3)">😞 没印象</button>
        <button class="fc-btn fc-btn-2" onclick="window._fcGrade(2)">🤔 有印象</button>
        <button class="fc-btn fc-btn-1" onclick="window._fcGrade(1)">✅ 记住了</button>
      </div>
      <div class="fc-progress">${index + 1} / ${items.length}</div>
    </div>
  `;

  window._fcGrade = (grade) => {
    sm2Update(word, grade);
    _fcState.index++;
    renderCard();
  };
  window._fcPlayVoice = function() {
    if (window.playVoice) window.playVoice(word.english);
  };
}

function findRawWord(english) {
  try {
    if (window._wbWordbook) {
      for (const u of window._wbWordbook.units) {
        for (const w of u.words) {
          if (w.english === english) return w;
        }
      }
    }
  } catch(e) {}
  return null;
}

function sm2Update(word, grade) {
  const q = word._sm2 || { ef: 2.5, interval: 0, reps: 0, nextReview: 0 };

  if (grade === 1) {
    q.reps++;
    if (q.reps === 1) q.interval = 1;
    else if (q.reps === 2) q.interval = 6;
    else q.interval = Math.round(q.interval * q.ef);
    q.ef = q.ef + (0.1 - (3 - grade) * (0.08 + (3 - grade) * 0.02));
  } else if (grade === 2) {
    q.reps = Math.max(0, q.reps - 1);
    q.interval = 1;
    q.ef = Math.max(1.3, q.ef - 0.2);
  } else {
    q.reps = 0;
    q.interval = 1;
    q.ef = Math.max(1.3, q.ef - 0.5);
  }

  if (q.ef < 1.3) q.ef = 1.3;
  q.nextReview = Date.now() + q.interval * 86400000;
  word._sm2 = q;

  try {
    localStorage.setItem('wb_sm2_' + word.english, JSON.stringify(q));
  } catch(e) {}
}

export function loadSM2(word) {
  try {
    const d = localStorage.getItem('wb_sm2_' + word.english);
    if (d) word._sm2 = JSON.parse(d);
  } catch(e) {}
}

function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
