"""
image_processing.py
--------------------
Implements Dark Channel Prior (DCP) image enhancement for underwater images.
This preprocessing step improves visibility of submerged objects before detection.
"""

import cv2
import numpy as np
from PIL import Image


def compute_dark_channel(image: np.ndarray, patch_size: int = 15) -> np.ndarray:
    """
    Compute the dark channel of an RGB image.

    The dark channel is the minimum pixel value across color channels
    within a local patch — used to estimate haze/turbidity in underwater images.

    Args:
        image (np.ndarray): Input BGR image (float32, range 0–1).
        patch_size (int): Size of the local patch for minimum filtering.

    Returns:
        np.ndarray: 2D dark channel map (float32).
    """
    # Take the per-pixel minimum across all color channels
    min_channel = np.min(image, axis=2)

    # Apply morphological erosion to find the local minimum within each patch
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (patch_size, patch_size)
    )
    dark_channel = cv2.erode(min_channel, kernel)

    return dark_channel


def enhance_underwater_image(pil_image: Image.Image, blend_alpha: float = 0.6) -> Image.Image:
    """
    Enhance an underwater image using the Dark Channel Prior (DCP) technique.

    Steps:
        1. Convert PIL image to OpenCV BGR format.
        2. Normalize to float32 [0, 1].
        3. Compute the dark channel map.
        4. Normalize the dark channel.
        5. Blend the inverted dark channel with the original image to reduce turbidity.
        6. Clip and convert back to uint8 PIL image.

    Args:
        pil_image (Image.Image): Input PIL image (RGB).
        blend_alpha (float): Blending weight for enhancement (0 = no effect, 1 = full).

    Returns:
        Image.Image: Enhanced PIL image (RGB).
    """
    # Convert PIL (RGB) → NumPy (BGR for OpenCV)
    img_np = np.array(pil_image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Normalize to [0, 1] float32
    img_float = img_bgr.astype(np.float32) / 255.0

    # Step 1: Compute dark channel
    dark = compute_dark_channel(img_float)

    # Step 2: Normalize dark channel to [0, 1]
    dark_norm = cv2.normalize(dark, None, 0, 1, cv2.NORM_MINMAX)

    # Step 3: Invert the dark channel (bright areas indicate haze/scattering)
    dark_inv = 1.0 - dark_norm

    # Step 4: Blend the inverted dark channel with the original image
    # Expand dark_inv to 3 channels for blending
    dark_3ch = np.stack([dark_inv, dark_inv, dark_inv], axis=2)
    enhanced = img_float + blend_alpha * dark_3ch * (1.0 - img_float)

    # Clip to valid range and convert back to uint8
    enhanced = np.clip(enhanced, 0, 1)
    enhanced_uint8 = (enhanced * 255).astype(np.uint8)

    # Convert back to RGB PIL image
    enhanced_rgb = cv2.cvtColor(enhanced_uint8, cv2.COLOR_BGR2RGB)
    return Image.fromarray(enhanced_rgb)
