// ==================== 语音播放模块 ====================
// 使用 Web Speech API

import { data, saveData } from './data.js';
import { showToast } from './ui.js';

let selectedVoice = null;

function findBestVoice(voices) {
  const priorityPatterns = [
    /Microsoft.*(?:Zira|Jenny|Aria|Nancy|Sara)/i,
    /Microsoft.*English/i,
    /Google UK/i,
    /Google US/i,
  ];
  const enVoices = voices.filter(v => v.lang && v.lang.startsWith('en'));
  for (const pattern of priorityPatterns) {
    const match = enVoices.find(v => pattern.test(v.name));
    if (match) return match;
  }
  return enVoices.find(v => v.lang === 'en-US') || enVoices[0] || null;
}

function parseSetting(value, isPitch) {
  value = value.replace(/[+%Hz]/g, '');
  return parseInt(value) || 0;
}

export async function playVoice(text) {
  try {
    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0 && !selectedVoice) {
      selectedVoice = findBestVoice(voices);
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const rate = parseSetting(data.voiceSettings.rate);
    const volume = parseSetting(data.voiceSettings.volume);
    const pitch = parseSetting(data.voiceSettings.pitch, true);

    utterance.rate = Math.max(0.5, Math.min(2, 1 + (rate / 100)));
    utterance.volume = Math.max(0, Math.min(1, 1 + (volume / 100)));
    utterance.pitch = Math.max(0, Math.min(2, 1 + (pitch / 20)));
    utterance.lang = 'en-US';
    if (selectedVoice) utterance.voice = selectedVoice;

    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.error('语音播放失败:', e);
    showToast('语音播放失败，请开启浏览器语音权限');
  }
}

export function getCurrentVoiceName() {
  return selectedVoice?.name || '默认';
}

export function initVoiceSettings() {
  // 填充语音选择器
  setTimeout(() => {
    const voices = window.speechSynthesis.getVoices();
    const sel = document.getElementById('voice-select');
    if (!sel || voices.length === 0) return;
    const enVoices = voices.filter(v => v.lang && v.lang.startsWith('en'));
    const saved = data.voiceSettings?.voiceName;
    if (!selectedVoice) selectedVoice = findBestVoice(voices);
    sel.innerHTML = '<option value="">自动选择</option>' +
      enVoices.map(v =>
        `<option value="${v.name}" ${v.name === saved || v.name === selectedVoice?.name ? 'selected' : ''}>${v.name}</option>`
      ).join('');
    sel.addEventListener('change', () => {
      const name = sel.value;
      data.voiceSettings.voiceName = name;
      saveData();
      selectedVoice = name ? voices.find(v => v.name === name) : findBestVoice(voices);
      showToast('语音已切换');
    });
  }, 300);

  const rateSlider = document.getElementById('rate-slider');
  const volumeSlider = document.getElementById('volume-slider');
  const pitchSlider = document.getElementById('pitch-slider');

  const rate = parseSetting(data.voiceSettings.rate);
  const volume = parseSetting(data.voiceSettings.volume);
  const pitch = parseSetting(data.voiceSettings.pitch, true);

  rateSlider.value = rate;
  volumeSlider.value = volume;
  pitchSlider.value = pitch;
  document.getElementById('rate-value').textContent = `${rate}%`;
  document.getElementById('volume-value').textContent = `${volume}%`;
  document.getElementById('pitch-value').textContent = `${pitch}Hz`;

  rateSlider.addEventListener('input', () => {
    document.getElementById('rate-value').textContent = `${rateSlider.value}%`;
  });
  volumeSlider.addEventListener('input', () => {
    document.getElementById('volume-value').textContent = `${volumeSlider.value}%`;
  });
  pitchSlider.addEventListener('input', () => {
    document.getElementById('pitch-value').textContent = `${pitchSlider.value}Hz`;
  });

  document.getElementById('save-voice-btn').addEventListener('click', () => {
    data.voiceSettings = {
      rate: `${rateSlider.value >= 0 ? '+' : ''}${rateSlider.value}%`,
      volume: `${volumeSlider.value >= 0 ? '+' : ''}${volumeSlider.value}%`,
      pitch: `${pitchSlider.value >= 0 ? '+' : ''}${pitchSlider.value}Hz`
    };
    saveData();
    showToast('语音设置已保存');
  });

  const nameEl = document.getElementById('voice-name-display');
  if (nameEl) {
    const updateVoiceName = () => {
      nameEl.textContent = `当前语音: ${getCurrentVoiceName()}`;
    };
    updateVoiceName();
    setTimeout(updateVoiceName, 500);
  }
}
