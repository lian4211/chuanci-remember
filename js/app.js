// ==================== chuanci remember app ====================
import { showToast } from './ui.js';

let wordbook = null;
let fcState = null;
let testState = null;

async function loadWordbook() {
  if (wordbook) return wordbook;
  const r = await fetch('data/wordbook.json');
  wordbook = await r.json();
  return wordbook;
}

// ==================== 首页 ====================
export async function renderHome() {
  const wb = await loadWordbook();
  const container = document.getElementById('home-content');
  
  const unitCards = wb.units.map(u => `
    <div class="unit-card" onclick="window._openUnit(${u.id})">
      <div class="unit-num">${u.title}</div>
      <div class="unit-stat">${u.words.length} 词</div>
    </div>
  `).join('');

  container.innerHTML = `
    <div style="text-align:center;margin-bottom:0.75rem">
      <p style="font-size:0.9rem;font-weight:700;color:var(--primary)">📚 ${wb.name}</p>
      <p style="font-size:0.7rem;color:var(--text-muted)">${wb.total_units} 单元 · ${wb.units.reduce((s,u) => s+u.words.length, 0)} 词</p>
    </div>

    <div class="app-grid">
      <div class="feature-card" onclick="window._openUnit(1)">
        <span class="icon">📖</span>
        <span class="label">词表</span>
      </div>
      <div class="feature-card" onclick="window._openTest()">
        <span class="icon">📝</span>
        <span class="label">测试</span>
      </div>
      <div class="feature-card" onclick="window._randomStudy()">
        <span class="icon">🎲</span>
        <span class="label">随机</span>
      </div>
    </div>

    <div class="unit-grid">${unitCards}</div>
  `;

  window._openUnit = (id) => { showWordlist(id); };
  window._openTest = () => { startGlobalTest(); };
  window._randomStudy = () => {
    const all = wb.units.flatMap(u => u.words.map(w => ({word: w, unit: u})));
    const shuffled = all.sort(() => Math.random() - 0.5);
    startFlashcard(shuffled, 0);
  };

  document.getElementById('page-title').textContent = 'chuanci remember';
}

// ==================== 词表 ====================
function showWordlist(unitId) {
  const unit = wordbook.units.find(u => u.id === unitId);
  if (!unit) return;

  document.getElementById('page-title').textContent = unit.title;
  showPage('wordlist');

  const container = document.getElementById('wordlist-content');
  container.innerHTML = `
    <div style="display:flex;gap:0.5rem;margin-bottom:0.75rem">
      <button class="btn-primary" style="flex:1" onclick="window._studyUnit(${unitId})">▶ 背诵</button>
      <button class="btn-ghost" style="flex:1" onclick="window._testUnitEC(${unitId})">📜 英译汉</button>
      <button class="btn-ghost" style="flex:1" onclick="window._testUnitCE(${unitId})">✍️ 汉译英</button>
    </div>
    <div>
      ${unit.words.map(w => `
        <div class="wl-item" onclick="window._studyWord(${unitId}, ${w.id})">
          <span class="wl-en">${esc(w.english)}</span>
          <span class="wl-def">${esc(w.definitions?.map?.(d => d).join(';')?.substring(0,60) || '')}</span>
        </div>
      `).join('')}
    </div>
  `;

  window._studyUnit = (id) => {
    const u = wordbook.units.find(uu => uu.id === id);
    startFlashcard(u.words.map(w => ({word: w, unit: u})), 0);
  };
  window._testUnitEC = (id) => startTest(id, 'ec');
  window._testUnitCE = (id) => startTest(id, 'ce');
  window._studyWord = (uid, wid) => {
    const u = wordbook.units.find(uu => uu.id === uid);
    const items = u.words.map(w => ({word: w, unit: u}));
    const idx = items.findIndex(i => i.word.id === wid);
    startFlashcard(items, idx >= 0 ? idx : 0);
  };
}

// ==================== 闪卡 ====================
function startFlashcard(items, startIdx) {
  fcState = { items, index: startIdx };
  showPage('flashcard');
  renderFlashcard();
}

function renderFlashcard() {
  if (!fcState) return;
  const { items, index } = fcState;
  if (index >= items.length) {
    document.getElementById('flashcard-content').innerHTML =
      '<p style="text-align:center;padding:2rem;font-size:1.2rem">🎉 完成!</p>';
    return;
  }

  const { word, unit } = items[index];
  document.getElementById('page-title').textContent = `${unit?.title || ''} ${index+1}/${items.length}`;

  const container = document.getElementById('flashcard-content');
  container.innerHTML = `
    <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem">
      <span style="color:var(--text-muted);font-size:0.8rem">${index+1}/${items.length}</span>
      <button class="btn-icon" onclick="window._fcBack()" style="font-size:0.9rem">← 返回</button>
    </div>

    <div class="fc-card">
      <div class="fc-word">${esc(word.english)}</div>
      ${word.phonetic?.us || word.phonetic?.uk ? `<div class="fc-phonetic">${[word.phonetic?.us, word.phonetic?.uk].filter(Boolean).join(' ')}</div>` : ''}

      ${word.definitions?.length ? `
        <div class="fc-section">
          <div class="fc-section-title">释义</div>
          ${word.definitions.map(d => `<div class="fc-def">${esc(d)}</div>`).join('')}
        </div>
      ` : ''}

      ${word.memory_aid ? `
        <div class="fc-section">
          <div class="fc-section-title">💡 助记</div>
          <div style="font-size:0.85rem;color:var(--text-secondary)">${esc(word.memory_aid)}</div>
        </div>
      ` : ''}

      ${word.exam_sentences?.length ? `
        <div class="fc-section">
          <div class="fc-section-title">📖 真题例句</div>
          ${word.exam_sentences.map(s => `
            <div class="fc-exam">
              <div>${esc(s.sentence)}</div>
              ${s.translation ? `<div style="color:var(--text-secondary);font-size:0.8rem;margin-top:0.25rem">${esc(s.translation)}</div>` : ''}
              ${s.source ? `<div style="font-size:0.65rem;color:var(--text-muted)">${esc(s.source)}</div>` : ''}
            </div>
          `).join('')}
        </div>
      ` : ''}

      ${word.extensions?.length ? `
        <div class="fc-section">
          <div class="fc-section-title">🌱 拓展</div>
          <div style="display:flex;flex-wrap:wrap;gap:0.3rem">
            ${word.extensions.map(e => `<span style="font-size:0.8rem;background:var(--primary-bg);padding:0.15rem 0.4rem;border-radius:4px">${esc(e.word)} ${esc(e.meaning?.substring(0,20) || '')}</span>`).join('')}
          </div>
        </div>
      ` : ''}
    </div>

    <div class="fc-nav">
      ${index > 0 ? `<button class="btn-ghost" onclick="window._fcPrev()">◀ 上一个</button>` : ''}
      <button class="btn-primary" onclick="window._fcNext()">下一个 ▶</button>
    </div>
  `;

  window._fcNext = () => { fcState.index++; renderFlashcard(); };
  window._fcPrev = () => { fcState.index--; renderFlashcard(); };
  window._fcBack = () => { fcState = null; showPage('home'); renderHome(); };
}

// ==================== 测试 ====================
function startTest(unitId, mode) {
  const unit = wordbook.units.find(u => u.id === unitId);
  if (!unit) return;
  const words = [...unit.words].sort(() => Math.random() - 0.5).slice(0, 15);
  testState = { words, index: 0, correct: 0, wrong: 0, mode, unitId };
  showPage('test');
  renderTest();
}

function startGlobalTest() {
  const all = wordbook.units.flatMap(u => u.words);
  const words = [...all].sort(() => Math.random() - 0.5).slice(0, 20);
  testState = { words, index: 0, correct: 0, wrong: 0, mode: 'ec', unitId: 0, global: true };
  showPage('test');
  renderTest();
}

function renderTest() {
  if (!testState) return;
  const s = testState;
  if (s.index >= s.words.length) {
    document.getElementById('test-content').innerHTML =
      `<p style="text-align:center;font-size:1.2rem;padding:2rem">🎉 完成! 正确: ${s.correct}/${s.words.length}</p>
       <button class="btn-primary" onclick="window._testBack()" style="display:block;margin:0 auto">← 返回</button>`;
    return;
  }

  const word = s.words[s.index];
  const isEC = s.mode === 'ec';
  
  // 生成选项
  const allDefs = wordbook.units.flatMap(u => u.words.flatMap(w => w.definitions || []));
  const correct = (word.definitions || []).join(';');
  const others = allDefs.filter(d => d !== correct).sort(() => Math.random() - 0.5).slice(0, 3);
  const options = [correct, ...others].sort(() => Math.random() - 0.5);

  document.getElementById('page-title').textContent = `测试 ${s.index+1}/${s.words.length}`;
  const container = document.getElementById('test-content');
  container.innerHTML = `
    <p style="font-size:1.25rem;font-weight:700;text-align:center;margin:1rem 0">${esc(isEC ? word.english : (word.definitions?.[0]?.substring(0,60) || word.english))}</p>
    <div style="margin-bottom:0.75rem">
      ${options.map((opt, i) =>
        `<div class="test-opt" onclick="window._testAnswer(${i}, this)">${esc(opt.substring(0,80))}</div>`
      ).join('')}
    </div>
    <button class="btn-ghost" onclick="window._testBack()">← 返回</button>
  `;

  window._testAnswer = (idx, el) => {
    if (s._answered) return;
    s._answered = true;
    const btns = container.querySelectorAll('.test-opt');
    const selected = btns[idx].textContent;
    if (selected === correct) {
      btns[idx].className = 'test-opt correct';
      s.correct++;
    } else {
      btns[idx].className = 'test-opt wrong';
      s.wrong++;
      btns.forEach(b => { if (b.textContent === correct) b.className = 'test-opt correct'; });
    }
    setTimeout(() => { s.index++; s._answered = false; renderTest(); }, 1200);
  };
  window._testBack = () => {
    testState = null;
    if (s.global) { showPage('home'); renderHome(); }
    else showWordlist(s.unitId);
  };
}

// ==================== 工具 ====================
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const el = document.getElementById(id + '-page');
  if (el) el.classList.add('active');
}

function esc(s) {
  if (typeof s !== 'string') return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// ==================== 启动 ====================
renderHome();
