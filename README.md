# 🔍 SentimentScope

> **Social Media Sentiment & Emotion Analyzer** — powered by state-of-the-art HuggingFace Transformer models.

SentimentScope is a full-stack NLP web application that takes social media text and instantly classifies it by both **sentiment** (Positive / Negative / Neutral) and **deep emotion** (Joy / Anger / Fear / Sadness / Surprise / Disgust / Neutral) — all running locally on your machine, no API keys needed.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎯 **Dual-Model Analysis** | Two specialized RoBERTa/DistilRoBERTa models run in parallel for sentiment + emotion |
| 📊 **Score Breakdown** | Full probability scores for every label, shown as animated progress bars |
| 📋 **Batch Analysis** | Analyse up to **50 posts at once**, one per line |
| 🕑 **Session History** | Last 50 analyses persisted in browser `localStorage` — survives page refresh |
| 🌐 **LAN Sharing** | `start.bat` binds to `0.0.0.0` so any device on your network can use the app |
| 📖 **Auto API Docs** | FastAPI Swagger UI available at `/docs` — great for testing the REST API directly |
| 🎨 **Premium Dark UI** | Glassmorphism design with animated background orbs, Inter + JetBrains Mono fonts |

---

## 🖼️ Interface Overview

The app has three tabs:

- **Single Post** — Paste one post (up to 2 000 chars), press **Analyse** or `Ctrl+Enter`
- **Batch Analysis** — Enter up to 50 posts (one per line), press **Analyse All**
- **History** — Browse/clear past analyses from this session

---

## 🤖 Models Used

| Task | HuggingFace Model | Labels |
|---|---|---|
| Sentiment | [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) | Positive · Negative · Neutral |
| Emotion | [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) | Joy · Anger · Fear · Sadness · Surprise · Disgust · Neutral |

> **First launch note:** Both models are downloaded automatically from the HuggingFace Hub (~600 MB combined). They are cached locally after the first download — subsequent starts are instant.

---

## 📁 Project Structure

```
SentimentScope/               ← Git repository root
├── README.md                 ← You are here
├── .gitignore
├── desktop.ini               ← Windows folder display customization
└── SentimentScope/           ← Main application package
    ├── start.bat             ← ✅ One-click Windows launcher (activates venv + starts server)
    ├── frontend/             ← Static web UI (no build step required)
    │   ├── index.html        ← Single-page application (tabs, forms, result display)
    │   ├── style.css         ← Premium dark glassmorphism theme (496 lines)
    │   └── app.js            ← Vanilla JS: API calls, history, rendering (294 lines)
    └── backend/              ← FastAPI Python backend
        ├── main.py           ← FastAPI app, routes, CORS, static file serving
        ├── model.py          ← HuggingFace model loading & inference logic
        └── requirements.txt  ← Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **pip**
- **~600 MB** free disk space (for model downloads on first run)
- Internet connection on first run (for model downloads)

---

### Option A — One-click launch (Windows) ⭐ Recommended

> This uses the `start.bat` file you added. It activates the virtual environment and starts the server automatically.

**Step 1** — Set up a virtual environment and install dependencies (only needed once):

```bat
cd SentimentScope\SentimentScope
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
```

**Step 2** — Double-click `start.bat` (or run it from the terminal):

```bat
SentimentScope\SentimentScope\start.bat
```

The script will:
1. Activate the `venv` automatically
2. Detect your local IP address
3. Start the server on port `8000`
4. Print both local and LAN access URLs

**Step 3** — Open in your browser:

| Device | URL |
|---|---|
| This computer | `http://localhost:8000` |
| Other devices on Wi-Fi | `http://<your-local-IP>:8000` |

---

### Option B — Manual launch (any OS)

```bash
# 1. Create & activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r SentimentScope/backend/requirements.txt

# 3. Start the server
cd SentimentScope/backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000`.

---

## 🔌 REST API Reference

The backend is a fully documented FastAPI app. All endpoints are also browsable at `http://localhost:8000/docs`.

### `GET /health`
Liveness check.

```json
{ "status": "ok", "service": "SentimentScope" }
```

---

### `POST /analyse`
Analyse a **single** piece of text.

**Request body:**
```json
{
  "text": "I absolutely love this product! It changed my life."
}
```

**Response:**
```json
{
  "text": "I absolutely love this product! It changed my life.",
  "sentiment": "Positive",
  "sentiment_scores": [
    { "label": "Positive", "score": 97.43 },
    { "label": "Neutral",  "score": 1.84 },
    { "label": "Negative", "score": 0.73 }
  ],
  "emotion": "Joy",
  "emotion_scores": [
    { "label": "Joy",      "score": 89.12 },
    { "label": "Surprise", "score": 5.31 },
    ...
  ]
}
```

**Constraints:** `text` must be 1–2 000 characters.

---

### `POST /analyse/batch`
Analyse **up to 50 texts** in one request.

**Request body:**
```json
{
  "texts": [
    "I'm so happy today!",
    "This is the worst day ever.",
    "Feeling kind of meh today…"
  ]
}
```

**Response:**
```json
{
  "count": 3,
  "results": [ ...same shape as single /analyse response... ]
}
```

**Constraints:** 1–50 items in the list.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend framework** | [FastAPI](https://fastapi.tiangolo.com/) 0.111.0 |
| **ASGI server** | [Uvicorn](https://www.uvicorn.org/) 0.30.1 |
| **ML framework** | [PyTorch](https://pytorch.org/) 2.6.0 |
| **NLP library** | [HuggingFace Transformers](https://huggingface.co/docs/transformers) 4.45.2 |
| **Tokenizer** | HuggingFace Tokenizers 0.20.3 |
| **Data validation** | Pydantic (via FastAPI) |
| **Frontend** | Vanilla HTML5 + CSS3 + JavaScript — zero build step, zero dependencies |
| **Fonts** | Google Fonts: [Inter](https://fonts.google.com/specimen/Inter) + [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) |
| **Persistence** | Browser `localStorage` (client-side history only) |

---

## ⚙️ How It Works

```
Browser (app.js)
    │
    │  POST /analyse  {text: "..."}
    ▼
FastAPI (main.py)
    │
    │  analyse_text(text)
    ▼
model.py
    ├─► Sentiment pipeline  (cardiffnlp/twitter-roberta-base-sentiment-latest)
    │       └─► Returns: [{label: "Positive", score: 0.97}, ...]
    │
    └─► Emotion pipeline    (j-hartmann/emotion-english-distilroberta-base)
            └─► Returns: [{label: "joy", score: 0.89}, ...]
    │
    │  Normalise labels, multiply × 100, sort descending
    ▼
JSON response → browser renders animated score bars
```

- Both models use **`top_k=None`** — all label scores are returned (not just the top one), so you always get the full probability distribution.
- Models are **lazily loaded** on first request and then **cached in memory** as singletons for the lifetime of the server process.
- Text is **truncated** to 512 tokens (transformer limit) if longer than that.

---

## 🌐 Network / LAN Access

`start.bat` starts the server with `--host 0.0.0.0`, which means the app is reachable from **any device on the same Wi-Fi/LAN** (phones, tablets, other computers) — not just `localhost`.

The `app.js` frontend automatically detects whether it's being accessed locally or over the network and points the API calls at the correct host:

```js
const API_BASE = location.protocol === "file:"
  ? "http://localhost:8000"
  : `${location.protocol}//${location.hostname}:8000`;
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` / `Cmd + Enter` | Analyse the text in the Single Post tab |

---

## 🗂️ desktop.ini — Windows Folder Customization

The repository includes a `desktop.ini` file at the root level. This is a **Windows system file** that customizes how the folder appears in Windows Explorer.

```ini
[.ShellClassInfo]
LocalizedResourceName=@SentimentScope,0
```

| Key | Description |
|---|---|
| `[.ShellClassInfo]` | Section header read by the Windows Shell |
| `LocalizedResourceName` | Sets the folder's **display name** in Windows Explorer to `SentimentScope` |

> **Note:** `desktop.ini` is normally a hidden system file on Windows. If you don't see it in Explorer, enable **"Show hidden items"** in View settings. It has no effect on macOS or Linux — safe to ignore on those platforms.

---

## 🔒 Notes & Limitations

- **No authentication** — anyone on your LAN can access the app when running with `--host 0.0.0.0`
- **No database** — history is stored in the browser only (`localStorage`), not on the server
- **English only** — both models are trained primarily on English text
- **Max 512 tokens** — text longer than 512 tokens is truncated before inference
- **CPU inference** — runs on CPU by default; GPU acceleration is available if CUDA is installed (set `device=0` in the `pipeline()` calls in `model.py`)
- **Single-process** — both API and static file serving share one Uvicorn process

---

## 📝 License

This project is open source. See the repository for license details.

---

<p align="center">
  SentimentScope · Built with ♥ using RoBERTa &amp; DistilRoBERTa
</p>

