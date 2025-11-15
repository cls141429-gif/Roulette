// web/static/app.js
const multEl = document.getElementById('mult');
const betBtn = document.getElementById('betBtn');
const cashBtn = document.getElementById('cashout');
const betInput = document.getElementById('bet');
const digestEl = document.getElementById('digest');
const log = document.getElementById('log');
const info = document.getElementById('info');

let running = false;
let currentMult = 1.0;
let crashAt = null;
let rafId = null;

function appendLog(txt) {
  const d = document.createElement('div');
  d.textContent = txt;
  log.prepend(d);
}

async function startRound(bet) {
  appendLog('Запрос на создание раунда...');
  const r = await fetch('/api/next-round').then(r => r.json());
  digestEl.textContent = 'Digest: ' + r.digest;
  appendLog('Round created: ' + r.round_id);
  // В демо мы сразу разрешаем раунд (server самостоятельно резолвит). В реальном приложении сервер делает это через таймер.
  const res = await fetch('/api/resolve-round', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({round_id: r.round_id})
  }).then(r => r.json());
  appendLog('Round resolved; multiplier = ' + res.multiplier.toFixed(2) + 'x');
  crashAt = res.multiplier;
  runMultiplierLoop();
}

function runMultiplierLoop() {
  running = true;
  currentMult = 1.0;
  multEl.innerText = currentMult.toFixed(2) + 'x';
  cashBtn.disabled = false;
  let last = performance.now();

  function step(now) {
    const dt = (now - last)/1000;
    last = now;
    // экспоненциальный рост: скорость настроена для визуала
    currentMult *= Math.pow(1.02, dt*60);
    multEl.innerText = currentMult.toFixed(2) + 'x';
    if (currentMult >= crashAt) {
      multEl.innerText = crashAt.toFixed(2) + 'x ✖';
      running = false;
      cashBtn.disabled = true;
      appendLog('Раунд крашнулся на ' + crashAt.toFixed(2) + 'x');
      cancelAnimationFrame(rafId);
      return;
    }
    rafId = requestAnimationFrame(step);
  }
  rafId = requestAnimationFrame(step);
}

betBtn.addEventListener('click', () => {
  const bet = Number(betInput.value) || 0;
  if (bet <= 0) { info.textContent = 'Введите корректную ставку'; return; }
  startRound(bet);
});

cashBtn.addEventListener('click', () => {
  if (!running) return;
  running = false;
  appendLog('Кэш-аут на ' + currentMult.toFixed(2) + 'x');
  cashBtn.disabled = true;
  cancelAnimationFrame(rafId);
});
