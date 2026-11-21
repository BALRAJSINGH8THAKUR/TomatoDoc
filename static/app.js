const $ = s => document.querySelector(s);

const fileIn = $('#file');
const drop = $('#drop');
const dropText = $('#dropText');
const previewWrap = $('#previewWrap');
const prev = $('#preview');
const scanOverlay = $('#scanOverlay');
const fileMeta = $('#fileMeta');
const btn = $('#analyze');
const reset = $('#reset');
const out = $('#result');

const MAX_BYTES = 8 * 1024 * 1024; // 8 MB server limit
let current = null;
let previewUrl = null;

const ICONS = {
  organic: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>',
  chemical: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31"/><path d="M14 9.3V1.99"/><path d="M8.5 2h7"/><path d="M14 9.3a6.5 6.5 0 1 1-4 0"/><path d="M5.52 16h12.96"/></svg>',
  prevention: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/></svg>'
};

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function careBox(iconSvg, title, text, extraCls = '') {
  const box = el('div', `care-box ${extraCls}`.trim());
  const head = el('h3', 'care-title');
  head.innerHTML = iconSvg;
  head.append(document.createTextNode(title));
  box.append(head, el('p', '', text));
  return box;
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function clearSelection() {
  current = null;
  fileIn.value = '';
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  }
  previewWrap.hidden = true;
  scanOverlay.hidden = true;
  dropText.hidden = false;
  fileMeta.textContent = 'No image selected';
  btn.disabled = true;
  reset.hidden = true;
  out.hidden = true;
}

function setFile(f) {
  if (!f) return;
  if (!f.type.startsWith('image/')) {
    return showMsg('err', 'Not an image', 'Please choose a JPG or PNG photo.');
  }
  if (f.size > MAX_BYTES) {
    return showMsg('err', 'File too large', 'Please choose an image smaller than 8 MB.');
  }
  if (previewUrl) URL.revokeObjectURL(previewUrl);

  current = f;
  previewUrl = URL.createObjectURL(f);
  prev.src = previewUrl;
  previewWrap.hidden = false;
  dropText.hidden = true;
  fileMeta.textContent = `${f.name} · ${formatSize(f.size)}`;
  btn.disabled = false;
  reset.hidden = false;
  out.hidden = true;
}

function showMsg(kind, title, text, extra) {
  out.className = `panel result-panel ${kind}`;
  out.replaceChildren(el('h2', '', title), el('p', 'summary', text));
  if (extra) out.append(extra);
  out.hidden = false;
  out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function shrink(file, max = 1024) {
  try {
    const bmp = await createImageBitmap(file);
    const k = Math.min(1, max / Math.max(bmp.width, bmp.height));
    const c = document.createElement('canvas');
    c.width = Math.round(bmp.width * k);
    c.height = Math.round(bmp.height * k);
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.drawImage(bmp, 0, 0, c.width, c.height);
    return await new Promise(resolve => c.toBlob(b => resolve(b || file), 'image/jpeg', 0.9));
  } catch {
    return file;
  }
}

function render(r) {
  if (r.status === 'rejected') {
    const tips = el('p', 'muted', 'Tips: one leaf, close-up, even daylight, sharp focus, plain background.');
    return showMsg('warn', 'Not a tomato leaf?', r.message, tips);
  }

  out.className = 'panel result-panel';

  const head = el('div', 'res-head');
  head.append(
    el('h2', '', r.name),
    el('span', `badge${r.healthy ? ' good' : ''}`, r.healthy ? 'Healthy' : 'Disease Detected')
  );

  const confRow = el('div', 'conf-row');
  confRow.append(el('span', '', 'Model confidence'), el('strong', '', `${r.confidence}%`));

  const bar = el('div', 'bar');
  const fill = el('i');
  fill.style.width = `${r.confidence}%`;
  bar.append(fill);

  const summary = el('p', 'summary', r.info.summary);

  const grid = el('div', 'care-grid');
  grid.append(
    careBox(ICONS.organic, 'Organic Treatment', r.info.organic),
    careBox(ICONS.chemical, 'Chemical Treatment', r.info.chemical)
  );

  const prevention = careBox(ICONS.prevention, 'Prevention', r.info.prevention, 'full');

  const list = el('ul', 'top3');
  r.top3.forEach(t => {
    const li = el('li');
    const miniBar = el('div', 'mini-bar');
    const miniFill = el('i');
    miniFill.style.width = `${t.confidence}%`;
    miniBar.append(miniFill);
    li.append(el('span', '', t.name), el('strong', '', `${t.confidence}%`), miniBar);
    list.append(li);
  });

  const footer = el('div', 'result-footer');
  const againBtn = el('button', 'btn ghost', 'Scan Another Leaf');
  againBtn.type = 'button';
  againBtn.addEventListener('click', () => {
    clearSelection();
    $('#scanner').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  footer.append(againBtn);

  out.replaceChildren(
    head,
    confRow,
    bar,
    summary,
    grid,
    prevention,
    el('h3', 'sub-heading', 'Top Predictions'),
    list,
    footer
  );

  out.hidden = false;
  out.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

btn.addEventListener('click', async () => {
  if (!current) return;
  btn.disabled = true;
  reset.disabled = true;
  scanOverlay.hidden = false;
  btn.replaceChildren(el('span', 'spin'), 'Analyzing…');

  try {
    const fd = new FormData();
    fd.append('image', await shrink(current), 'leaf.jpg');
    const res = await fetch('/predict', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.status === 'error') {
      showMsg('err', 'Something went wrong', data.message);
    } else {
      render(data);
    }
  } catch {
    showMsg('err', 'Network error', 'Could not reach the server. Check your connection and try again.');
  } finally {
    scanOverlay.hidden = true;
    btn.textContent = 'Analyze Leaf';
    btn.disabled = false;
    reset.disabled = false;
  }
});

reset.addEventListener('click', clearSelection);
fileIn.addEventListener('change', () => setFile(fileIn.files[0]));

drop.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    fileIn.click();
  }
});

['dragenter', 'dragover'].forEach(ev => {
  drop.addEventListener(ev, e => {
    e.preventDefault();
    drop.classList.add('over');
  });
});

['dragleave', 'drop'].forEach(ev => {
  drop.addEventListener(ev, e => {
    e.preventDefault();
    drop.classList.remove('over');
  });
});

drop.addEventListener('drop', e => setFile(e.dataTransfer.files[0]));

// Scroll-triggered reveal animations
const observer = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll('.reveal').forEach(node => observer.observe(node));