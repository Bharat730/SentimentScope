# 🔍 SentimentScope

> **Social Media Sentiment & Emotion Analyzer** — powered by HuggingFace Transformer models.

SentimentScope is a full-stack NLP web application that takes social media text and classifies it by both **sentiment** (Positive / Negative / Neutral) and **emotion** (Joy / Anger / Fear / Sadness / Surprise / Disgust / Neutral). It can also break a longer post down **sentence by sentence**. Everything runs locally on your machine — no API keys and no external services needed.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎯 **Dual-model analysis** | Two specialised models (RoBERTa for sentiment, DistilRoBERTa for emotion) run on every text |
| 📊 **Score breakdown** | Full probability for every label, shown as animated progress bars |
| 📋 **Sentence-by-sentence breakdown** | Multi-sentence posts get an expandable per-sentence sentiment + emotion view (`/analyse/aspects`) |
| 📦 **Batch analysis** | Analyse up to **50 posts at once**, one per line |
| 🕑 **History** | Last 50 analyses saved in the browser (`localStorage`) — survives page refresh |
| 🌐 **LAN sharing** | `start.bat` binds to `0.0.0.0`, so phones and other computers on the same Wi-Fi can use the app |
| 📖 **Auto API docs** | FastAPI Swagger UI at `/docs` for testing the REST API directly |
| 📝 **Inference log** | Every analysis is printed to the console and appended to `backend/inference.log` |
| 🎨 **Dark glassmorphism UI** | Animated background orbs, Inter + JetBrains Mono fonts (loaded from Google Fonts) |

---

## 🖼️ Interface Overview

The app has three tabs:

- **Single Post** — paste one post (up to 2,000 characters) and press **Analyse** or `Ctrl+Enter`. If the text contains two or more sentences, a *Sentence-by-Sentence Breakdown* appears below the overall result; click a sentence to expand its scores.
- **Batch Analysis** — enter up to 50 posts (one per line) and press **Analyse All**.
- **History** — browse or clear previous analyses.

---

## 🤖 Models Used

| Task | HuggingFace model | Labels | Trained on |
|---|---|---|---|
| Sentiment | [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) | Positive · Negative · Neutral | RoBERTa-base trained on ~124M tweets (2018–2021), fine-tuned on the TweetEval benchmark |
| Emotion | [`j-hartmann/emotion-english-distilroberta-base`](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) | Joy · Anger · Fear · Sadness · Surprise · Disgust · Neutral | DistilRoBERTa fine-tuned on 6 emotion datasets (~20k balanced examples; ~66% evaluation accuracy) |

SentimentScope does **not** train anything itself — it uses these pre-trained models for inference only.

> **First launch note:** both models are downloaded automatically from the HuggingFace Hub (roughly 800 MB combined) and cached locally. After that they load from disk, but the **first analysis after each server start takes a few extra seconds** while the models are loaded into memory.

---

## 📁 Project Structure

```
SentimentScope/                  ← Git repository root
├── README.md                    ← You are here
├── .gitignore
└── SentimentScope/              ← Application folder
    ├── start.bat                ← One-click Windows launcher (activates venv + starts server)
    ├── frontend/                ← Static web UI (no build step)
    │   ├── index.html           ← Single-page app (tabs, forms, result areas)
    │   ├── style.css            ← Dark glassmorphism theme
    │   └── app.js               ← Vanilla JS: API calls, rendering, history
    └── backend/                 ← FastAPI backend
        ├── main.py              ← App, routes, CORS, static file serving
        ├── model.py             ← Model loading, inference, sentence splitting, logging
        ├── requirements.txt     ← Python dependencies
        └── inference.log        ← Created at runtime (git-ignored)
```

The `venv/` folder you create during setup lives inside `SentimentScope/SentimentScope/` and is git-ignored.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** and **pip**
- About **1 GB** of free disk space (models + PyTorch)
- Internet connection on first run (model download)

### Option A — Windows, one-click launcher ⭐

**Step 1 — one-time setup** (run from a terminal):

```bat
git clone https://github.com/Bharat730/SentimentScope.git
cd SentimentScope\SentimentScope
python -m venv venv
venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

**Step 2 — start the server:** double-click `start.bat`, or run it from the terminal:

```bat
start.bat
```

The script activates the virtual environment, detects your local IP, starts the server on port `8000` and prints both URLs.

**Step 3 — open it:**

| Device | URL |
|---|---|
| This computer | `http://localhost:8000` |
| Other devices on the same Wi-Fi | `http://<your-pc-ip>:8000` (shown by `start.bat`, or run `ipconfig`) |

### Option B — Manual launch (any OS)

```bash
cd SentimentScope/SentimentScope
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r backend/requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Use `--host 127.0.0.1` instead of `0.0.0.0` if you want the app reachable from this computer only. Stop the server with `Ctrl+C`.

---

## 🔌 REST API Reference

All endpoints are also browsable at `http://localhost:8000/docs`.

### `GET /health`
Liveness check.

```json
{ "status": "ok", "service": "SentimentScope" }
```

### `POST /analyse`
Analyse a **single** text (overall result only).

```json
{ "text": "I absolutely love this product! It changed my life." }
```

Response:

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
    { "label": "Surprise", "score": 5.31 }
  ]
}
```

*(Scores are percentages, sorted highest first; the emotion list contains all 7 labels.)*
**Constraints:** `text` must be 1–2,000 characters.

### `POST /analyse/aspects`
Same request as `/analyse`. Returns the overall result **plus** an `aspects` list with one entry per detected sentence:

```json
{
  "text": "The camera is great. The battery life is awful.",
  "sentiment": "...", "sentiment_scores": [ ... ],
  "emotion": "...",   "emotion_scores": [ ... ],
  "aspects": [
    { "text": "The camera is great.",       "sentiment": "Positive", "emotion": "Joy",   "sentiment_scores": [ ... ], "emotion_scores": [ ... ] },
    { "text": "The battery life is awful.", "sentiment": "Negative", "emotion": "Anger", "sentiment_scores": [ ... ], "emotion_scores": [ ... ] }
  ]
}
```

The web UI calls this endpoint for the Single Post tab and shows the breakdown when at least two sentences are found.

### `POST /analyse/batch`
Analyse **up to 50 texts** in one request.

```json
{ "texts": ["I'm so happy today!", "This is the worst day ever."] }
```

Response: `{ "count": 2, "results": [ ...same shape as /analyse... ] }`
**Constraints:** 1–50 items. Blank items are skipped.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | [FastAPI](https://fastapi.tiangolo.com/) 0.111.0 |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) 0.30.1 |
| ML framework | [PyTorch](https://pytorch.org/) 2.6.0 |
| NLP library | [HuggingFace Transformers](https://huggingface.co/docs/transformers) 4.45.2 (+ Tokenizers 0.20.3) |
| Data validation | Pydantic (via FastAPI) |
| Frontend | Vanilla HTML5 + CSS3 + JavaScript — no build step |
| Fonts | Google Fonts: Inter + JetBrains Mono |
| Persistence | Browser `localStorage` (history only) |

---

## ⚙️ How It Works

```
Browser (app.js)
    │  POST /analyse/aspects  {text}
    ▼
FastAPI (main.py)
    ▼
model.py
    ├─► Sentiment pipeline  (cardiffnlp/twitter-roberta-base-sentiment-latest)
    ├─► Emotion pipeline    (j-hartmann/emotion-english-distilroberta-base)
    │      → normalise labels, ×100, sort descending
    └─► Sentence splitter → the same two models run on each sentence
    ▼
JSON → browser renders score bars, chips and the sentence breakdown
```

- Both models use **`top_k=None`**, so every label's score is returned, not just the winner.
- Models are **lazily loaded** on the first request and kept in memory for the life of the server process.
- Text is **truncated** to 512 tokens (the model limit).
- Sentence splitting is **rule-based** (a regular expression that also protects common abbreviations such as *Dr.* and *Mr.*). Fragments shorter than 8 characters are skipped.
- Each analysis writes a log entry (console + `backend/inference.log`) containing the first 80 characters of the input and the scores.

---

## 🌐 Network / LAN Access

`start.bat` runs the server with `--host 0.0.0.0`, so the app is reachable from any device on the same Wi-Fi/LAN. The frontend works out the API address automatically:

```js
const API_BASE = location.protocol === "file:"
  ? "http://localhost:8000"
  : `${location.protocol}//${location.hostname}:8000`;
```

This assumes the server is running on port `8000`.

---

## 🧰 Troubleshooting

| Problem | Fix |
|---|---|
| Phone/other device can't connect | Make sure both devices are on the **same Wi-Fi** (not a guest network). Some campus/hostel networks block device-to-device traffic — try a phone hotspot. |
| Windows Firewall blocks it | When prompted, allow Python on **Private** networks. Or run once in an *Administrator* PowerShell: `New-NetFirewallRule -DisplayName "SentimentScope 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private` |
| `Address already in use` | An old server is still running. Close it, or start on another port: `--port 8001`. (The frontend expects port 8000 when opened from another device.) |
| `start.bat` says it cannot find `venv` | Create it first (see *Getting Started*). The venv must be in `SentimentScope/SentimentScope/venv`. |
| First analysis is slow | Normal — the models load on the first request after each start. |
| Console shows "Some weights … were not used" | Harmless HuggingFace notice for the sentiment model. |
| `GET /favicon.ico 404` in the console | Harmless — the app has no favicon yet. |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` / `Cmd + Enter` | Analyse the text in the Single Post tab |

---

## 🔒 Notes & Limitations

- **No authentication** — anyone on your network can use the app while it runs with `--host 0.0.0.0`. Use it on trusted networks only.
- **No database** — history lives in the browser only, not on the server.
- **Privacy** — `backend/inference.log` stores the first 80 characters of every analysed text and grows over time. It is git-ignored; delete it whenever you like.
- **English only** — both models are trained on English text.
- **Accuracy** — the emotion model reaches about 66% on its own test split across 7 classes; sarcasm, slang and mixed emotions are hard for both models.
- **Max 512 tokens** per text; the API accepts at most 2,000 characters.
- **CPU inference** by default; for a CUDA GPU set `device=0` in the `pipeline()` calls in `model.py`.
- **Single process** — the API and static files are served by one Uvicorn process.

---

## 🤝 Contributing

The `main` branch is protected: changes go in through **pull requests**.

```bash
git checkout main
git pull
git checkout -b my-change
# ...edit files...
git add .
git commit -m "Describe the change"
git push -u origin my-change
```

Then open a pull request on GitHub.

---

## 👥 Authors

- **Bharat Lakhanpal** — [@Bharat730](https://github.com/Bharat730)
- **Piyush Grover** — [@PiyushGrover435](https://github.com/PiyushGrover435)

---

## 📝 License

No license has been chosen yet. Until one is added, all rights remain with the authors.

---

<p align="center">
  SentimentScope · Built with ♥ using RoBERTa &amp; DistilRoBERTa
</p>
