"""Tests for tars/hardware/camera.py — fast scene summaries."""

from tars.hardware import camera


def test_summarize_detections_counts_and_confidence():
    detections = [
        {"label": "cup", "confidence": 0.91, "box": [0, 0, 1, 1]},
        {"label": "cup", "confidence": 0.88, "box": [0, 0, 1, 1]},
        {"label": "laptop", "confidence": 0.76, "box": [0, 0, 1, 1]},
    ]

    summary = camera.summarize_detections(detections, max_objects=3)
    assert "2 cups (91% confidence)" in summary
    assert "1 laptop (76% confidence)" in summary


def test_describe_scene_prefers_local_yolo_summary(monkeypatch):
    monkeypatch.setattr(camera, "_yolo_available", True)
    monkeypatch.setattr(camera, "capture_frame", lambda: object())
    monkeypatch.setattr(
        camera,
        "detect_objects",
        lambda frame=None: [{"label": "person", "confidence": 0.95, "box": [0, 0, 1, 1]}],
    )

    summary = camera.describe_scene(quick=True)
    assert summary == "I see 1 person (95% confidence)."


def test_describe_scene_without_local_detection_returns_fast_fallback(monkeypatch):
    monkeypatch.setattr(camera, "_yolo_available", False)
    monkeypatch.setattr(camera, "capture_frame", lambda: object())
    monkeypatch.setattr(camera.config, "OPENAI_API_KEY", "", raising=False)

    summary = camera.describe_scene(quick=True)
    assert summary == "Camera is online, but local detection is unavailable."
