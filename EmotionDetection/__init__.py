# emotion_detection.py
"""Emotion detection module using Watson NLP EmotionPredict endpoint."""

import json
import requests
from typing import Any, Dict, Optional

_ENDPOINT = (
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict"
)
_HEADERS = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}


def _call_watson_emotion(text_to_analyze: str) -> requests.Response:
    """Call the Watson NLP EmotionPredict endpoint and return the Response."""
    payload = {"raw_document": {"text": text_to_analyze}}
    response = requests.post(_ENDPOINT, headers=_HEADERS, json=payload, timeout=10)
    return response


def emotion_detector(text_to_analyze: str) -> Optional[Dict[str, Any]]:
    """
    Send text to Watson EmotionPredict and return a formatted dictionary:
    {
        'anger': anger_score or None,
        'disgust': disgust_score or None,
        'fear': fear_score or None,
        'joy': joy_score or None,
        'sadness': sadness_score or None,
        'dominant_emotion': '<name>' or None
    }
    If server returns status_code == 400 (blank input), returns dict with None values.
    """
    response = _call_watson_emotion(text_to_analyze)

    # Handle blank input case
    if response.status_code == 400:
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None,
        }

    try:
        data = response.json()
    except ValueError:
        return None

    text_field = data.get("text", data)
    if isinstance(text_field, str):
        try:
            parsed = json.loads(text_field)
        except (ValueError, TypeError):
            parsed = {}
    elif isinstance(text_field, dict):
        parsed = text_field
    else:
        parsed = {}

    def _get_score(dct: dict, key: str) -> float:
        val = dct.get(key)
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    scores_source = parsed
    for path in (
        ("emotion", "document", "emotion"),
        ("emotion", "document"),
        ("document", "emotion"),
        ("emotion",),
    ):
        tmp = parsed
        for p in path:
            if isinstance(tmp, dict) and p in tmp:
                tmp = tmp[p]
            else:
                tmp = None
                break
        if isinstance(tmp, dict):
            scores_source = tmp
            break

    anger_score = _get_score(scores_source, "anger")
    disgust_score = _get_score(scores_source, "disgust")
    fear_score = _get_score(scores_source, "fear")
    joy_score = _get_score(scores_source, "joy")
    sadness_score = _get_score(scores_source, "sadness")

    emotions = {
        "anger": anger_score,
        "disgust": disgust_score,
        "fear": fear_score,
        "joy": joy_score,
        "sadness": sadness_score,
    }
    dominant_emotion = max(emotions, key=emotions.get) if emotions else None

    return {
        "anger": anger_score,
        "disgust": disgust_score,
        "fear": fear_score,
        "joy": joy_score,
        "sadness": sadness_score,
        "dominant_emotion": dominant_emotion,
    }
