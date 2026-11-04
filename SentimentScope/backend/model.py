"""
model.py
Loads two HuggingFace models:
  1. cardiffnlp/twitter-roberta-base-sentiment-latest  -> Positive / Negative / Neutral
  2. j-hartmann/emotion-english-distilroberta-base     -> Joy / Anger / Fear / Sadness / Surprise / Disgust / Neutral
Models are cached locally after first download.
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from transformers import pipeline

# ── Log file (sits next to this script: backend/inference.log) ────────────────
_LOG_FILE = Path(__file__).parent / "inference.log"

def _log(msg: str):
    """Print a timestamped line to stdout AND append it to inference.log."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"  [{ts}] {msg}"
    print(line, flush=True)
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Model identifiers ────────────────────────────────────────────────────────
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
EMOTION_MODEL   = "j-hartmann/emotion-english-distilroberta-base"

# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_sentiment_pipe = None
_emotion_pipe   = None


def get_sentiment_pipeline():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        _log("Loading sentiment model …")
        _sentiment_pipe = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL,
            top_k=None,          # return all label scores
            truncation=True,
            max_length=512,
        )
        _log("Sentiment model ready ✓")
    return _sentiment_pipe


def get_emotion_pipeline():
    global _emotion_pipe
    if _emotion_pipe is None:
        _log("Loading emotion model …")
        _emotion_pipe = pipeline(
            "text-classification",
            model=EMOTION_MODEL,
            top_k=None,
            truncation=True,
            max_length=512,
        )
        _log("Emotion model ready ✓")
    return _emotion_pipe


# ── Inference helpers ─────────────────────────────────────────────────────────

def _label_map(raw_label: str) -> str:
    """Normalise raw HuggingFace labels to pretty names."""
    mapping = {
        # sentiment
        "positive": "Positive",
        "negative": "Negative",
        # emotion
        "joy":      "Joy",
        "anger":    "Anger",
        "fear":     "Fear",
        "sadness":  "Sadness",
        "surprise": "Surprise",
        "disgust":  "Disgust",
        # shared
        "neutral":  "Neutral",
    }
    return mapping.get(raw_label.lower(), raw_label.title())


def analyse_text(text: str) -> dict:
    """
    Run both pipelines on *text* and return a unified result dict.
    """
    if not text or not text.strip():
        return {"error": "Empty input"}

    _log("─" * 50)
    _log(f'INPUT  : "{text[:80]}{"…" if len(text) > 80 else ""}"')

    # ── Sentiment ─────────────────────────────────────────────────────────────
    _log("STEP 1 : Running sentiment analysis …")
    sent_raw    = get_sentiment_pipeline()(text)[0]   # list of {label, score}
    sent_scores = sorted(
        [{"label": _label_map(r["label"]), "score": round(r["score"] * 100, 2)}
         for r in sent_raw],
        key=lambda x: x["score"],
        reverse=True,
    )
    top_sentiment = sent_scores[0]["label"]
    for s in sent_scores:
        bar = "█" * int(s["score"] / 5)
        _log(f"         {s['label']:<10} {s['score']:>6.2f}%  {bar}")
    _log(f"RESULT : Sentiment → {top_sentiment}")

    # ── Emotion ───────────────────────────────────────────────────────────────
    _log("STEP 2 : Running emotion detection …")
    emot_raw    = get_emotion_pipeline()(text)[0]
    emot_scores = sorted(
        [{"label": _label_map(r["label"]), "score": round(r["score"] * 100, 2)}
         for r in emot_raw],
        key=lambda x: x["score"],
        reverse=True,
    )
    top_emotion = emot_scores[0]["label"]
    for e in emot_scores:
        bar = "█" * int(e["score"] / 5)
        _log(f"         {e['label']:<10} {e['score']:>6.2f}%  {bar}")
    _log(f"RESULT : Emotion   → {top_emotion}")
    _log("─" * 50)

    return {
        "text":           text,
        "sentiment":      top_sentiment,
        "sentiment_scores": sent_scores,
        "emotion":        top_emotion,
        "emotion_scores": emot_scores,
    }


def analyse_batch(texts: list[str]) -> list[dict]:
    """Analyse a list of texts and return a list of result dicts."""
    return [analyse_text(t) for t in texts if t.strip()]


# ── Sentence splitter ──────────────────────────────────────────────────────────

# Matches sentence-ending punctuation followed by whitespace + capital letter,
# or a quote/bracket then capital. Handles common abbreviations gracefully.
_SENT_BOUNDARY = re.compile(
    r'(?<=[.!?])\s+(?=[A-Z"\'(\[])'
)

def split_sentences(text: str) -> list[str]:
    """
    Split *text* into individual sentences.
    Returns a list of non-empty stripped strings.
    """
    # Protect common abbreviations: Mr. Mrs. Dr. St. vs. etc.
    protected = re.sub(
        r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|approx|govt|Sen|Rep|Lt|Gen|Sgt|Cpl)\.',
        r'\1<DOT>',
        text
    )
    parts = _SENT_BOUNDARY.split(protected)
    sentences = [p.replace('<DOT>', '.').strip() for p in parts if p.strip()]
    # Further split on ". " inside a part if the splitter missed anything
    result = []
    for s in sentences:
        if len(s) < 8:          # too short to be a real sentence — skip
            continue
        result.append(s)
    return result


# ── Aspect (sentence-level) analysis ──────────────────────────────────────────

def analyse_aspects(text: str) -> dict:
    """
    Split *text* into sentences and analyse each one individually.
    Returns the overall result plus a per-sentence breakdown.
    """
    overall = analyse_text(text)

    sentences = split_sentences(text)
    aspects = []
    for i, sent in enumerate(sentences, 1):
        _log(f"  ASPECT {i}/{len(sentences)}: \"{sent[:60]}{'…' if len(sent) > 60 else ''}\"")
        result = analyse_text(sent)
        if "error" not in result:
            aspects.append(result)

    overall["aspects"] = aspects
    return overall
