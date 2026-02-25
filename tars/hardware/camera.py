"""Camera integration for TARS — Pi Camera v2 with YOLO detection.

Features:
    - Capture frames from Pi Camera Module v2 (via picamera2)
    - Local object/person detection using YOLOv8n (runs on Pi 5)
    - Cloud vision queries via GPT-4o-mini (detailed scene descriptions)
"""

import base64
import io

from tars import config

# Try to import camera and detection libraries
_camera = None
_camera_available = False
_yolo_model = None
_yolo_available = False

try:
    from picamera2 import Picamera2

    _PICAMERA_AVAILABLE = True
except ImportError:
    _PICAMERA_AVAILABLE = False

try:
    from ultralytics import YOLO

    _ULTRALYTICS_AVAILABLE = True
except ImportError:
    _ULTRALYTICS_AVAILABLE = False


def initialize():
    """Initialize camera and YOLO model."""
    global _camera, _camera_available, _yolo_model, _yolo_available

    # Initialize Pi Camera
    if _PICAMERA_AVAILABLE:
        try:
            _camera = Picamera2()
            camera_config = _camera.create_still_configuration(
                main={"size": (640, 480)},
            )
            _camera.configure(camera_config)
            _camera.start()
            _camera_available = True
            print("Pi Camera initialized")
        except Exception as e:
            print(f"Camera init failed: {e}")
    else:
        print("picamera2 not installed (Pi only)")

    # Initialize YOLO
    if _ULTRALYTICS_AVAILABLE:
        try:
            _yolo_model = YOLO("yolov8n.pt")
            _yolo_available = True
            print("YOLO detection ready (yolov8n)")
        except Exception as e:
            print(f"YOLO init failed: {e}")
    else:
        print("ultralytics not installed — local detection disabled")


def is_available():
    """Check if camera is available."""
    return _camera_available


def is_yolo_available():
    """Check if YOLO detection is available."""
    return _yolo_available


def capture_frame():
    """Capture a single frame from the camera.

    Returns:
        PIL Image or None on failure.
    """
    if not _camera_available:
        return None
    try:
        from PIL import Image

        array = _camera.capture_array()
        return Image.fromarray(array)
    except Exception as e:
        print(f"Capture error: {e}")
        return None


def capture_to_bytes(format="jpeg"):
    """Capture a frame and return as bytes.

    Returns:
        bytes or None on failure.
    """
    frame = capture_frame()
    if frame is None:
        return None
    try:
        buf = io.BytesIO()
        frame.save(buf, format=format)
        return buf.getvalue()
    except Exception as e:
        print(f"Image conversion error: {e}")
        return None


def detect_objects(frame=None):
    """Run YOLO object detection on a frame.

    Args:
        frame: PIL Image (captures new frame if None).

    Returns:
        List of dicts: [{"label": "person", "confidence": 0.92, "box": [x1,y1,x2,y2]}, ...]
    """
    if not _yolo_available:
        return []

    if frame is None:
        frame = capture_frame()
    if frame is None:
        return []

    try:
        results = _yolo_model(frame, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                label = result.names[int(box.cls[0])]
                confidence = float(box.conf[0])
                coords = box.xyxy[0].tolist()
                detections.append({
                    "label": label,
                    "confidence": confidence,
                    "box": coords,
                })
        return detections
    except Exception as e:
        print(f"Detection error: {e}")
        return []


def count_people(frame=None):
    """Count the number of people visible.

    Returns:
        int: Number of people detected.
    """
    detections = detect_objects(frame)
    return sum(1 for d in detections if d["label"] == "person")


def describe_scene():
    """Get a detailed scene description using GPT-4o-mini vision.

    Captures a frame and sends it to OpenAI's vision API.

    Returns:
        str: Scene description, or error message.
    """
    image_bytes = capture_to_bytes()
    if image_bytes is None:
        return "I can't see anything — camera is not available."

    # Check if OpenAI is available for vision
    try:
        from openai import OpenAI

        if not config.OPENAI_API_KEY:
            return _describe_with_yolo_only()

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model=config.AI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are TARS from Interstellar. Describe what you see "
                                "in this image in 1-2 sentences with your signature sarcasm. "
                                "Be specific about objects and people you notice."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=150,
            timeout=15,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Vision API error: {e}")
        return _describe_with_yolo_only()


def _describe_with_yolo_only():
    """Fallback: describe scene using only YOLO detections."""
    detections = detect_objects()
    if not detections:
        return "I can see... absolutely nothing interesting. My camera works but my brain doesn't, apparently."

    # Count objects by label
    counts = {}
    for d in detections:
        label = d["label"]
        counts[label] = counts.get(label, 0) + 1

    parts = []
    for label, count in sorted(counts.items(), key=lambda x: -x[1]):
        if count == 1:
            parts.append(f"a {label}")
        else:
            parts.append(f"{count} {label}s")

    items = ", ".join(parts)
    return f"I can see {items}. Not the most exciting view, but it's what you've got."


def cleanup():
    """Stop camera and release resources."""
    global _camera, _camera_available
    if _camera:
        try:
            _camera.stop()
        except Exception:
            pass
        _camera = None
        _camera_available = False
