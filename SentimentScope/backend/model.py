"""
model.py
Loads two HuggingFace models:
  1. cardiffnlp/twitter-roberta-base-sentiment-latest  -> Positive / Negative / Neutral
  2. j-hartmann/emotion-english-distilroberta-base     -> Joy / Anger / Fear / Sadness / Surprise / Disgust / Neutral
Models are cached locally after first download.
"""

from transformers import pipeline


# ── Model identifiers ────────────────────────────────────────────────────────
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
EMOTION_MODEL   = "j-hartmann/emotion-english-distilroberta-base"

# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_sentiment_pipe = None
_emotion_pipe   = None


def get_sentiment_pipeline():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        print("[model] Loading sentiment model …")
        _sentiment_pipe = pipeline(
            "sentiment-analysis",
            model=SENTIMENT_MODEL,
            top_k=None,          # return all label scores
            truncation=True,
            max_length=512,
        )
        print("[model] Sentiment model ready.")
    return _sentiment_pipe


def get_emotion_pipeline():
    global _emotion_pipe
    if _emotion_pipe is None:
        print("[model] Loading emotion model …")
        _emotion_pipe = pipeline(
            "text-classification",
            model=EMOTION_MODEL,
            top_k=None,
            truncation=True,
            max_length=512,
        )
        print("[model] Emotion model ready.")
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

    # ── Sentiment ─────────────────────────────────────────────────────────────
    sent_raw    = get_sentiment_pipeline()(text)[0]   # list of {label, score}
    sent_scores = sorted(
        [{"label": _label_map(r["label"]), "score": round(r["score"] * 100, 2)}
         for r in sent_raw],
        key=lambda x: x["score"],
        reverse=True,
    )
    top_sentiment = sent_scores[0]["label"]

    # ── Emotion ───────────────────────────────────────────────────────────────
    emot_raw    = get_emotion_pipeline()(text)[0]
    emot_scores = sorted(
        [{"label": _label_map(r["label"]), "score": round(r["score"] * 100, 2)}
         for r in emot_raw],
        key=lambda x: x["score"],
        reverse=True,
    )
    top_emotion = emot_scores[0]["label"]

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
