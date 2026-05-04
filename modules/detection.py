"""
detection.py
------------
Handles running RT-DETR inference on images and drawing annotated bounding boxes.
"""

import numpy as np
from PIL import Image


# 15 detection classes for the underwater trash model
DETECTION_CLASSES = [
    "Mask", "can", "cellphone", "electronics", "gbottle",
    "glove", "metal", "misc", "net", "pbag",
    "pbottle", "plastic", "rod", "sunglasses", "tire"
]

# Color palette for bounding boxes (BGR format for OpenCV)
# Each class gets a consistent, visually distinct color
CLASS_COLORS = [
    (255, 99,  71),   # Mask       – Tomato Red
    (255, 165,  0),   # can        – Orange
    (50,  205,  50),  # cellphone  – Lime Green
    (30,  144, 255),  # electronics– Dodger Blue
    (186,  85, 211),  # gbottle    – Medium Orchid
    (255, 215,   0),  # glove      – Gold
    (0,   206, 209),  # metal      – Dark Turquoise
    (240, 128, 128),  # misc       – Light Coral
    (127, 255, 212),  # net        – Aquamarine
    (255, 105, 180),  # pbag       – Hot Pink
    (100, 149, 237),  # pbottle    – Cornflower Blue
    (152, 251, 152),  # plastic    – Pale Green
    (255, 160, 122),  # rod        – Light Salmon
    (135, 206, 250),  # sunglasses – Light Sky Blue
    (218, 165,  32),  # tire       – Goldenrod
]

UNKNOWN_COLOR = (180, 180, 180)  # Gray for unknown/low-confidence detections


def get_class_color(class_id: int) -> tuple:
    """Return the BGR color for a given class index."""
    if 0 <= class_id < len(CLASS_COLORS):
        return CLASS_COLORS[class_id]
    return UNKNOWN_COLOR


def run_detection(model, pil_image: Image.Image, confidence_threshold: float = 0.35):
    """
    Run RT-DETR inference on a PIL image and return annotated results.

    Args:
        model: Loaded Ultralytics RT-DETR model instance.
        pil_image (Image.Image): Enhanced or raw input image (RGB).
        confidence_threshold (float): Minimum confidence to label with class name.
                                      Below threshold → labeled as "Unknown Debris".

    Returns:
        annotated_image (Image.Image): Image with bounding boxes drawn.
        detections (list[dict]): List of detection dicts with keys:
            - label (str): Class name or "Unknown Debris"
            - confidence (float): Detection confidence score
            - bbox (list[int]): [x1, y1, x2, y2]
    """
    try:
        import cv2
    except Exception as exc:
        raise RuntimeError(
            "OpenCV is unavailable in this environment. Install system dependency libGL.so.1 and python package opencv-python."
        ) from exc

    # Convert PIL image to NumPy array (RGB → BGR for OpenCV drawing)
    img_np = np.array(pil_image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Run inference (no filtering here – we apply our own threshold logic)
    results = model.predict(source=pil_image, conf=0.1, verbose=False)

    detections = []

    for result in results:
        boxes = result.boxes

        if boxes is None or len(boxes) == 0:
            continue

        for box in boxes:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Apply confidence threshold to determine label
            if confidence >= confidence_threshold:
                label = DETECTION_CLASSES[class_id] if class_id < len(DETECTION_CLASSES) else "Unknown Debris"
                color = get_class_color(class_id)
            else:
                label = "Unknown Debris"
                color = UNKNOWN_COLOR

            # Store detection metadata
            detections.append({
                "label": label,
                "confidence": round(confidence, 3),
                "bbox": [x1, y1, x2, y2]
            })

            # Draw bounding box
            cv2.rectangle(img_bgr, (x1, y1), (x2, y2), color, 2)

            # Prepare annotation text
            annotation = f"{label} {confidence:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.55
            font_thickness = 1

            # Compute text size for background rectangle
            (text_w, text_h), baseline = cv2.getTextSize(
                annotation, font, font_scale, font_thickness
            )

            # Draw filled background for text readability
            cv2.rectangle(
                img_bgr,
                (x1, y1 - text_h - baseline - 4),
                (x1 + text_w + 4, y1),
                color,
                thickness=-1
            )

            # Draw annotation text in white
            cv2.putText(
                img_bgr,
                annotation,
                (x1 + 2, y1 - baseline - 2),
                font,
                font_scale,
                (255, 255, 255),
                font_thickness,
                lineType=cv2.LINE_AA
            )

    # Convert annotated BGR image back to RGB PIL
    annotated_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    annotated_image = Image.fromarray(annotated_rgb)

    return annotated_image, detections
    try:
        import cv2
    except Exception as exc:
        raise RuntimeError(
            "OpenCV is unavailable in this environment. Install system dependency libGL.so.1 and python package opencv-python."
        ) from exc
