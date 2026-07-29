// ==================== 语音播放模块 (v2) ====================
// 优先 Edge TTS 云端, 回退 Web Speech

import { data, saveData } from './data.js';
import { showToast } from './ui.js';

// ---------- Edge TTS (云端高质量, 不需要API Key) ----------
// 使用 Edge 浏览器 "朗读" 功能的底层接口
const EDGE_TTS_BASE = 'https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1';

let _edgeVoice = 'en-US-JennyNeural';
let _edgeToken = null;
let _edgeOk = true;

async function getEdgeToken() {
  try {
    const r = await fetch(EDGE_TTS_BASE + '?TrustedClientToken=6A5AA1D4EAFF4E9FB37E23D68491D6F4', {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0' }
    });
    const text = await r.text();
    return text;  // Token 是纯文本
  } catch (e) {
    return null;
  }
}

async function playEdgeTTS(text) {
  if (!_edgeToken) _edgeToken = await getEdgeToken();
  if (!_edgeToken) return false;

  const voice = data.voiceSettings?.edgeVoice || 'en-US-JennyNeural';
  // SSML with prosody
  const rate = parseSetting(data.voiceSettings.rate);
  const pitch = parseSetting(data.voiceSettings.pitch, true);
  const rateStr = rate >= 0 ? `+${rate}%` : `${rate}%`;
  const pitchStr = `${pitch >= 0 ? '+' : ''}${pitch}Hz`;

  const ssml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="${voice}">
      <prosody rate="${rateStr}" pitch="${pitchStr}">${escXml(text)}</prosody>
    </voice>
  </speak>`;

  try {
    const r = await fetch(`${EDGE_TTS_BASE}?TrustedClientToken=6A5AA1D4EAFF4E9FB37E23D68491D6F4&ConnectionId=${Date.now()}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0',
        'Authorization': 'Bearer ' + _edgeToken
      },
      body: ssml
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.onended = () => { URL.revokeObjectURL(url); };
    await audio.play();
    return true;
  } catch (e) {
    console.warn('Edge TTS 失败:', e.message);
    _edgeOk = false;
    return false;
  }
}

function escXml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ---------- Web Speech (备选) ----------
function playWebSpeech(text) {
  try {
    const voices = window.speechSynthesis.getVoices();
    let sv = null;
    if (voices.length > 0) {
      const saved = data.voiceSettings?.voiceName;
      if (saved) sv = voices.find(v => v.name === saved);
      if (!sv) {
        const pats = [/Google US/i, /Google UK/i, /Microsoft.*(?:Zira|Jenny|Aria)/i, /Samantha|Karen/i];
        for (const p of pats) { sv = voices.find(v => p.test(v.name)); if (sv) break; }
        if (!sv) sv = voices.find(v => v.lang === 'en-US') || voices[0];
      }
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    const rate = parseSetting(data.voiceSettings.rate);
    u.rate = Math.max(0.5, Math.min(2, 1 + (rate / 100)));
    u.lang = 'en-US';
    if (sv) u.voice = sv;
    window.speechSynthesis.speak(u);
  } catch(e) { console.error(e); }
}

// ---------- 公共API ----------
export async function playVoice(text) {
  if (_edgeOk) {
    const ok = await playEdgeTTS(text);
    if (ok) return;
  }
  playWebSpeech(text);
}

function parseSetting(v) {
  return parseInt(String(v).replace(/[+%Hz]/g, '')) || 0;
}

export function getCurrentVoiceName() {
  return data.voiceSettings?.edgeVoice || data.voiceSettings?.voiceName || '';
}

export function initVoiceSettings() {
  setTimeout(() => {
    const sel = document.getElementById('voice-select');
    if (!sel) return;
    const ev = ['en-US-JennyNeural','en-US-AriaNeural','en-GB-SoniaNeural','en-US-SaraNeural','en-US-GuyNeural'];
    const saved = data.voiceSettings?.edgeVoice || 'en-US-JennyNeural';
    sel.innerHTML = '<option value="">Web Speech(系统语音)</option>' +
      ev.map(v => `<option value="${v}" ${v === saved ? 'selected' : ''}>Edge ${v.replace(/^en-/,'').replace('Neural','')}</option>`).join('');
    sel.addEventListener('change', () => {
      data.voiceSettings = data.voiceSettings || {};
      if (sel.value) data.voiceSettings.edgeVoice = sel.value;
      else delete data.voiceSettings.edgeVoice;
      saveData();
      showToast('语音已切换');
    });
  }, 200);

  const rs = document.getElementById('rate-slider');
  if (!rs) return;
  const rate = parseSetting(data.voiceSettings.rate);
  rs.value = rate;
  document.getElementById('rate-value').textContent = rate + '%';
  rs.addEventListener('input', () => {
    document.getElementById('rate-value').textContent = rs.value + '%';
  });

  document.getElementById('save-voice-btn')?.addEventListener('click', () => {
    data.voiceSettings = data.voiceSettings || {};
    data.voiceSettings.rate = `${rs.value >= 0 ? '+' : ''}${rs.value}%`;
    saveData();
    showToast('语音设置已保存');
  });

  const ne = document.getElementById('voice-name-display');
  if (ne) { ne.textContent = '语音: ' + getCurrentVoiceName(); setTimeout(() => { ne.textContent = '语音: ' + getCurrentVoiceName(); }, 500); }
}
