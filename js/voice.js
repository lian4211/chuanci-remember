// ==================== 语音播放模块 (v3) ====================
// 策略: Google TTS(Android首选) → Apple(iOS) → Microsoft(Windows) → 默认

import { data, saveData } from './data.js';
import { showToast } from './ui.js';

function parseV(v) { return parseInt(String(v).replace(/[+%Hz]/g,'')) || 0; }

export async function playVoice(text) {
  try {
    const voices = window.speechSynthesis.getVoices();
    let voice = null;

    // 1. 用户手动选的语音
    const saved = data.voiceSettings?.voiceName;
    if (saved) voice = voices.find(v => v.name === saved);

    // 2. 自动选最佳
    if (!voice && voices.length > 0) {
      // 移动端优先 Google (Android) / Samantha (iOS)
      const prefs = [
        /Google US English/i, /Google UK English/i, /Google.*English/i,
        /Samantha/i, /Karen/i, /Moira/i, /Tessa/i,
        /Microsoft.*(?:Jenny|Aria|Zira)/i,
        /Microsoft.*English/i
      ];
      for (const p of prefs) {
        voice = voices.find(v => p.test(v.name));
        if (voice) break;
      }
      if (!voice) voice = voices.find(v => v.lang === 'en-US') || voices[0];
    }

    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    const rate = parseV(data.voiceSettings.rate);
    u.rate = Math.max(0.5, Math.min(2, 1 + (rate / 100)));
    u.lang = 'en-US';
    if (voice) u.voice = voice;
    window.speechSynthesis.speak(u);
  } catch(e) { console.error('语音失败:', e); }
}

export function getCurrentVoiceName() { return data.voiceSettings?.voiceName || '自动'; }

export function initVoiceSettings() {
  // 填充语音选择器
  setTimeout(() => {
    const sel = document.getElementById('voice-select');
    if (!sel) return;
    const voices = window.speechSynthesis.getVoices();
    const enVoices = voices.filter(v => v.lang && v.lang.startsWith('en'));
    const saved = data.voiceSettings?.voiceName;
    sel.innerHTML = '<option value="">自动选择最佳</option>' +
      enVoices.map(v =>
        `<option value="${v.name}" ${v.name === saved ? 'selected' : ''}>${v.name}</option>`
      ).join('');
    sel.addEventListener('change', () => {
      data.voiceSettings = data.voiceSettings || {};
      data.voiceSettings.voiceName = sel.value;
      saveData();
      showToast('语音已切换');
    });
  }, 500);

  const rs = document.getElementById('rate-slider');
  if (!rs) return;
  const rate = parseV(data.voiceSettings.rate);
  rs.value = rate;
  document.getElementById('rate-value').textContent = rate + '%';
  rs.addEventListener('input', () => { document.getElementById('rate-value').textContent = rs.value + '%'; });

  document.getElementById('save-voice-btn')?.addEventListener('click', () => {
    data.voiceSettings = data.voiceSettings || {};
    data.voiceSettings.rate = `${rs.value >= 0 ? '+' : ''}${rs.value}%`;
    saveData();
    showToast('语音设置已保存');
  });

  // 测试语音按钮
  document.getElementById('test-voice-btn')?.addEventListener('click', () => { playVoice('Hello, this is a test of the voice system.'); });

  const ne = document.getElementById('voice-name-display');
  if (ne) {
    const up = () => { ne.textContent = '当前语音: ' + getCurrentVoiceName(); };
    up(); setTimeout(up, 600);
  }
}
