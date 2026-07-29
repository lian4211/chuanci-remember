// ==================== 语音播放模块 (v4) ====================
// 优先使用预录 MP3 (Edge TTS 生成, 最高质量)
// 回退 Web Speech API

import { data, saveData } from './data.js';
import { showToast } from './ui.js';

let _audioMap = null;

// 加载音频映射表
async function loadAudioMap() {
  if (_audioMap) return _audioMap;
  try {
    const r = await fetch('data/audio_map.json');
    _audioMap = await r.json();
  } catch(e) { _audioMap = {}; }
  return _audioMap;
}

function parseV(v) { return parseInt(String(v).replace(/[+%Hz]/g,'')) || 0; }

export async function playVoice(text) {
  const word = text.toLowerCase().trim();

  // 1. 尝试预录 MP3 (Edge TTS 生成, 最高品质)
  const map = await loadAudioMap();
  const key = word.replace(/'/g, '_').replace(/-/g, '_');
  if (map[key] || map[word]) {
    const filename = map[key] || map[word];
    try {
      const audio = new Audio('data/audio/' + filename);
      const rate = parseV(data.voiceSettings.rate);
      audio.playbackRate = Math.max(0.5, Math.min(2, 1 + (rate / 100)));
      await audio.play();
      return;
    } catch(e) {
      // 播放失败, 继续尝试 Web Speech
    }
  }

  // 2. 回退 Web Speech API
  try {
    const voices = window.speechSynthesis.getVoices();
    let voice = null;
    const saved = data.voiceSettings?.voiceName;
    if (saved) voice = voices.find(v => v.name === saved);
    if (!voice && voices.length > 0) {
      const prefs = [/Google US English/i, /Google UK English/i, /Google.*English/i,
        /Samantha/i, /Karen/i, /Microsoft.*(?:Jenny|Aria|Zira)/i, /Microsoft.*English/i];
      for (const p of prefs) { voice = voices.find(v => p.test(v.name)); if (voice) break; }
      if (!voice) voice = voices.find(v => v.lang === 'en-US') || voices[0];
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = Math.max(0.5, Math.min(2, 1 + (parseV(data.voiceSettings.rate) / 100)));
    u.lang = 'en-US';
    if (voice) u.voice = voice;
    window.speechSynthesis.speak(u);
  } catch(e) { console.error('语音失败:', e); }
}

export function getCurrentVoiceName() {
  return data.voiceSettings?.voiceName || 'Edge TTS 预录';
}

export function initVoiceSettings() {
  setTimeout(() => {
    const sel = document.getElementById('voice-select');
    if (!sel) return;
    const voices = window.speechSynthesis.getVoices();
    const enVoices = voices.filter(v => v.lang && v.lang.startsWith('en'));
    const saved = data.voiceSettings?.voiceName;
    sel.innerHTML = '<option value="">Edge TTS 预录(推荐)</option>' +
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

  document.getElementById('test-voice-btn')?.addEventListener('click', () => { playVoice('Elaborate'); });

  const ne = document.getElementById('voice-name-display');
  if (ne) { ne.textContent = '语音: ' + getCurrentVoiceName(); }
}
