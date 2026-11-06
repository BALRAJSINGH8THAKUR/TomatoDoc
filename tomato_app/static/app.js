const $ = s => document.querySelector(s);
const fileIn = $('#file'), drop = $('#drop'), prev = $('#preview'), btn = $('#analyze'), reset = $('#reset'), out = $('#result');
let current = null;

function el(tag, cls, text) { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
function box(title, text) { const b = el('div', 'box'); b.append(el('h3', '', title), el('p', '', text)); return b; }

function setFile(f) {
  if (!f) return;
  if (!f.type.startsWith('image/')) return showMsg('err', 'Not an image', 'Please choose a JPG or PNG photo.');
  current = f;
  prev.src = URL.createObjectURL(f); prev.hidden = false; $('#dropText').hidden = true;
  btn.disabled = false; reset.hidden = false; out.hidden = true;
}

function showMsg(kind, title, text, extra) {
  out.className = 'card ' + kind; out.replaceChildren(el('h2', '', title), el('p', '', text));
  if (extra) out.append(extra);
  out.hidden = false; out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function shrink(file, max = 1024) {  // smaller upload on phones; falls back to the original file
  try {
    const bmp = await createImageBitmap(file);
    const k = Math.min(1, max / Math.max(bmp.width, bmp.height));
    const c = document.createElement('canvas'); c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
    const ctx = c.getContext('2d'); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, c.width, c.height); ctx.drawImage(bmp, 0, 0, c.width, c.height);
    return await new Promise(r => c.toBlob(b => r(b || file), 'image/jpeg', 0.9));
  } catch { return file; }
}

function render(r) {
  if (r.status === 'rejected') {
    const tips = el('p', 'muted', 'Tips: one leaf, close-up, good daylight, in focus, plain background.');
    return showMsg('warn', 'Not a tomato leaf?', r.message, tips);
  }
  out.className = 'card';
  const head = el('div', 'head');
  head.append(el('h2', '', r.name), el('span', 'badge' + (r.healthy ? ' good' : ''), r.healthy ? 'Healthy' : 'Disease detected'));
  const bar = el('div', 'bar'), fill = el('i'); fill.style.width = r.confidence + '%'; bar.append(fill);
  const g = el('div', 'grid');
  g.append(box('🌱 Organic treatment', r.info.organic), box('💊 Chemical treatment', r.info.chemical));
  const tip = box('🧠 Prevention', r.info.prevention); tip.style.marginTop = '12px';
  const list = el('ul', 'top3');
  r.top3.forEach(t => { const li = el('li'); li.append(el('span', '', t.name), el('b', '', t.confidence + '%')); list.append(li); });
  out.replaceChildren(head, el('p', 'muted', 'Confidence: ' + r.confidence + '%'), bar, el('p', '', r.info.summary), g, tip, el('h3', '', 'Top predictions'), list);
  out.hidden = false; out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

btn.addEventListener('click', async () => {
  if (!current) return;
  btn.disabled = true; btn.replaceChildren(el('span', 'spin'), 'Analyzing…');
  try {
    const fd = new FormData(); fd.append('image', await shrink(current), 'leaf.jpg');
    const res = await fetch('/predict', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.status === 'error') showMsg('err', 'Something went wrong', data.message); else render(data);
  } catch { showMsg('err', 'Network error', 'Could not reach the server. Check your connection and try again.'); }
  btn.textContent = 'Analyze leaf'; btn.disabled = false;
});
reset.addEventListener('click', () => { current = null; fileIn.value = ''; prev.hidden = true; $('#dropText').hidden = false; btn.disabled = true; reset.hidden = true; out.hidden = true; });
fileIn.addEventListener('change', () => setFile(fileIn.files[0]));
drop.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileIn.click(); } });
['dragenter', 'dragover'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', e => setFile(e.dataTransfer.files[0]));
