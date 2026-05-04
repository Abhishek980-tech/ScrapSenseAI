"""
image_processing.py
--------------------
Implements Dark Channel Prior (DCP) image enhancement for underwater images.
This preprocessing step improves visibility of submerged objects before detection.
"""

import numpy as np
from PIL import Image


def compute_dark_channel(image: np.ndarray, patch_size: int = 15) -> np.ndarray:
    """Compute the dark channel of an RGB image."""
    import cv2

    min_channel = np.min(image, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
    dark_channel = cv2.erode(min_channel, kernel)
    return dark_channel


def enhance_underwater_image(pil_image: Image.Image, blend_alpha: float = 0.6) -> Image.Image:
    """Enhance an underwater image using the Dark Channel Prior (DCP) technique."""
    import cv2

    img_np = np.array(pil_image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    img_float = img_bgr.astype(np.float32) / 255.0

    dark = compute_dark_channel(img_float)
    dark_norm = cv2.normalize(dark, None, 0, 1, cv2.NORM_MINMAX)
    dark_inv = 1.0 - dark_norm

    dark_3ch = np.stack([dark_inv, dark_inv, dark_inv], axis=2)
    enhanced = img_float + blend_alpha * dark_3ch * (1.0 - img_float)

    enhanced = np.clip(enhanced, 0, 1)
    enhanced_uint8 = (enhanced * 255).astype(np.uint8)
    enhanced_rgb = cv2.cvtColor(enhanced_uint8, cv2.COLOR_BGR2RGB)
    return Image.fromarray(enhanced_rgb)
