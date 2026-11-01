/* ════════════════════════════════════════════════════════════════════════════
   SentimentScope — app.js
   Handles: tab switching, single analysis, batch analysis, history
   Backend: FastAPI running at localhost:8000
   ════════════════════════════════════════════════════════════════════════════ */

// Auto-detect backend URL — works both locally and when served over the network
const API_BASE = location.protocol === "file:"
  ? "http://localhost:8000"
  : `${location.protocol}//${location.hostname}:8000`;

// ── Persistent history via localStorage ─────────────────────────────────────
const HISTORY_KEY = "sentimentscope_history";

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch { return []; }
}

function saveHistory(hist) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(hist));
}

let history = loadHistory();

// ── Emoji maps ────────────────────────────────────────────────────────────────
const SENTIMENT_EMOJI = { Positive: "😊", Negative: "😠", Neutral: "😐" };
const EMOTION_EMOJI   = {
  Joy: "😄", Anger: "😡", Fear: "😨",
  Sadness: "😢", Surprise: "😲", Disgust: "🤢", Neutral: "😐"
};

// ── Tab switching ─────────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll(".tab").forEach(t => {
    t.classList.remove("tab--active");
    t.setAttribute("aria-selected", "false");
  });
  document.querySelectorAll(".panel").forEach(p => p.classList.add("hidden"));

  document.getElementById(`tab-${name}`).classList.add("tab--active");
  document.getElementById(`tab-${name}`).setAttribute("aria-selected", "true");
  document.getElementById(`panel-${name}`).classList.remove("hidden");

  if (name === "history") renderHistory();
  if (name === "batch") updateLineCounter();
}

// ── Character counter ─────────────────────────────────────────────────────────
function updateCounter() {
  const ta  = document.getElementById("single-input");
  const cnt = document.getElementById("char-counter");
  cnt.textContent = `${ta.value.length} / 2000`;
  cnt.style.color = ta.value.length > 1800 ? "var(--negative)" : "";
}

// ── Line counter (batch) ───────────────────────────────────────────────────────
function updateLineCounter() {
  const ta  = document.getElementById("batch-input");
  const lines = ta.value.split("\n").filter(l => l.trim()).length;
  document.getElementById("line-counter").textContent =
    `${lines} line${lines !== 1 ? "s" : ""}`;
}
document.getElementById("batch-input").addEventListener("input", updateLineCounter);

// ── Clear single ──────────────────────────────────────────────────────────────
function clearSingle() {
  document.getElementById("single-input").value = "";
  updateCounter();
  const res = document.getElementById("single-result");
  res.classList.add("hidden");
  res.innerHTML = "";
}

// ── Loading state helpers ─────────────────────────────────────────────────────
function setLoading(btnId, spinnerId, loading) {
  const btn     = document.getElementById(btnId);
  const spinner = btn.querySelector(".btn-spinner");
  const text    = btn.querySelector(".btn-text");
  btn.disabled  = loading;
  spinner.classList.toggle("hidden", !loading);
  text.style.opacity = loading ? "0.5" : "1";
}

// ── API call wrapper ──────────────────────────────────────────────────────────
async function callApi(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || "API error");
  }
  return res.json();
}

// ── Single analysis ───────────────────────────────────────────────────────────
async function analyseSingle() {
  const text = document.getElementById("single-input").value.trim();
  if (!text) return showError("single-result", "Please enter some text first.");

  setLoading("analyse-btn", "btn-spinner", true);
  const resultEl = document.getElementById("single-result");
  resultEl.classList.remove("hidden");
  resultEl.innerHTML = `<div class="skeleton skeleton-block"></div>`;

  try {
    const data = await callApi("/analyse", { text });
    resultEl.innerHTML = buildResultCard(data);
    animateBars(resultEl);

    // add to history and persist
    history.unshift({ ...data, ts: new Date().toISOString() });
    if (history.length > 50) history.pop();
    saveHistory(history);
  } catch (err) {
    showError("single-result", err.message);
  } finally {
    setLoading("analyse-btn", "btn-spinner", false);
  }
}

// ── Batch analysis ────────────────────────────────────────────────────────────
async function analyseBatch() {
  const raw   = document.getElementById("batch-input").value;
  const texts = raw.split("\n").map(l => l.trim()).filter(Boolean);
  if (!texts.length) return showError("batch-result", "Please enter at least one line of text.");

  setLoading("batch-btn", "btn-spinner", true);
  const resultEl = document.getElementById("batch-result");
  resultEl.classList.remove("hidden");
  resultEl.innerHTML = `<div class="skeleton skeleton-block"></div>`;

  try {
    const data = await callApi("/analyse/batch", { texts });
    renderBatchResults(resultEl, data.results);

    // push to history and persist
    data.results.forEach(r => history.unshift({ ...r, ts: new Date().toISOString() }));
    if (history.length > 50) history = history.slice(0, 50);
    saveHistory(history);
  } catch (err) {
    showError("batch-result", err.message);
  } finally {
    setLoading("batch-btn", "btn-spinner", false);
  }
}

// ── Build result card HTML ────────────────────────────────────────────────────
function buildResultCard(data) {
  const sentClass = `sent-${data.sentiment.toLowerCase()}`;
  const emotClass = `emot-${data.emotion.toLowerCase()}`;

  const sentBars = data.sentiment_scores.map(s => buildBar(s.label, s.score, "sent")).join("");
  const emtBars  = data.emotion_scores.map(e => buildBar(e.label, e.score, "emot")).join("");

  return `
    <div class="result-card glass">
      <p class="result-card__text">"${escHtml(data.text)}"</p>
      <div class="result-grid">
        <div>
          <p class="result-section-title">Sentiment</p>
          <div class="top-label ${sentClass}">
            ${SENTIMENT_EMOJI[data.sentiment] || ""}
            ${data.sentiment}
          </div>
          <div class="bars-container">${sentBars}</div>
        </div>
        <div>
          <p class="result-section-title">Emotion</p>
          <div class="top-label ${emotClass}">
            ${EMOTION_EMOJI[data.emotion] || ""}
            ${data.emotion}
          </div>
          <div class="bars-container">${emtBars}</div>
        </div>
      </div>
    </div>`;
}

// ── Build single score bar ────────────────────────────────────────────────────
function buildBar(label, score, prefix) {
  // emotion "Neutral" uses fill-emot-neutral to avoid collision with sentiment "Neutral"
  const fillClass = (prefix === "emot" && label === "Neutral")
    ? "fill-emot-neutral"
    : `fill-${label.toLowerCase()}`;
  return `
    <div class="score-bar-wrap">
      <div class="score-bar-header">
        <span class="score-bar-label">${label}</span>
        <span class="score-bar-value">${score.toFixed(1)}%</span>
      </div>
      <div class="score-bar-track">
        <div class="score-bar-fill ${fillClass}" data-width="${score}"></div>
      </div>
    </div>`;
}

// ── Animate bars after render ─────────────────────────────────────────────────
function animateBars(container) {
  requestAnimationFrame(() => {
    container.querySelectorAll(".score-bar-fill").forEach(bar => {
      bar.style.width = bar.dataset.width + "%";
    });
  });
}

// ── Batch results renderer ────────────────────────────────────────────────────
function renderBatchResults(container, results) {
  if (!results.length) {
    container.innerHTML = `<div class="empty-state"><span class="empty-icon">🔍</span><p>No results.</p></div>`;
    return;
  }

  const items = results.map((r, i) => {
    const sentClass = `sent-${r.sentiment.toLowerCase()}`;
    const emotClass = `emot-${r.emotion.toLowerCase()}`;
    return `
      <div class="batch-item glass">
        <span class="batch-item__text">${i + 1}. ${escHtml(r.text)}</span>
        <div class="batch-item__chips">
          <span class="chip ${sentClass}">${SENTIMENT_EMOJI[r.sentiment] || ""} ${r.sentiment}</span>
          <span class="chip ${emotClass}">${EMOTION_EMOJI[r.emotion] || ""} ${r.emotion}</span>
        </div>
      </div>`;
  }).join("");

  container.innerHTML = `<div>${items}</div>`;
}

// ── History renderer ──────────────────────────────────────────────────────────
function renderHistory() {
  const listEl = document.getElementById("history-list");
  if (!history.length) {
    listEl.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">🗂️</span>
        <p>No analyses yet. Start by analysing a post!</p>
      </div>`;
    return;
  }

  listEl.innerHTML = history.map((item, i) => {
    const sentClass = `sent-${item.sentiment.toLowerCase()}`;
    const emotClass = `emot-${item.emotion.toLowerCase()}`;
    return `
      <div class="history-card glass">
        <div style="flex:1;min-width:0">
          <p class="history-card__text">${escHtml(item.text)}</p>
          <p class="history-card__meta">${formatTime(item.ts)}</p>
        </div>
        <div class="batch-item__chips">
          <span class="chip ${sentClass}">${SENTIMENT_EMOJI[item.sentiment] || ""} ${item.sentiment}</span>
          <span class="chip ${emotClass}">${EMOTION_EMOJI[item.emotion] || ""} ${item.emotion}</span>
        </div>
      </div>`;
  }).join("");
}

function clearHistory() {
  history = [];
  saveHistory(history);
  renderHistory();
}

// ── Error display ─────────────────────────────────────────────────────────────
function showError(containerId, message) {
  const el = document.getElementById(containerId);
  el.classList.remove("hidden");
  el.innerHTML = `
    <div class="error-box">
      ⚠️ <span>${escHtml(message)}</span>
    </div>`;
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function escHtml(str) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function formatTime(dateInput) {
  const date = typeof dateInput === "string" ? new Date(dateInput) : dateInput;
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) +
    " · " + date.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" });
}

// ── Keyboard shortcut: Ctrl+Enter to analyse ─────────────────────────────────
document.getElementById("single-input").addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") analyseSingle();
});
