# server.py
"""Flask server exposing emotion detection on /emotionDetector."""

from flask import Flask, request, render_template, jsonify
from EmotionDetection import emotion_detector

APP = Flask(__name__)


def _format_response_text(scores: dict) -> str:
    """Format the scores dict into the required text response string."""
    # Example required:
    # For the given statement, the system response is 'anger': 0.00, 'disgust': 0.00, ...
    formatted = (
        f"'anger': {scores.get('anger')}, 'disgust': {scores.get('disgust')}, "
        f"'fear': {scores.get('fear')}, 'joy': {scores.get('joy')} and "
        f"'sadness': {scores.get('sadness')}"
    )
    return f"For the given statement, the system response is {formatted}. The dominant emotion is {scores.get('dominant_emotion')}."


@APP.route("/emotionDetector", methods=["GET", "POST"])
def emotion_detector_route():
    """
    Handle web requests for emotion detection.
    Accepts form field 'statement' via POST or 'q' via GET.
    """
    if request.method == "POST":
        text = request.form.get("statement", "")
    else:
        text = request.args.get("q", "")

    result = emotion_detector(text)
    if result is None:
        # Could not parse API response
        return "Invalid text! Please try again!", 400

    # If error handling set dominant_emotion to None earlier, catch here
    if result.get("dominant_emotion") is None:
        return "Invalid text! Please try again!", 400

    response_text = _format_response_text(result)
    # Return plain text (the lab shows text response)
    return response_text, 200


if __name__ == "__main__":
    # Run on localhost:5000 as requested
    APP.run(host="0.0.0.0", port=5000)
