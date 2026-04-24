"""
model_loader.py
---------------
Handles loading of the RT-DETR object detection model using Ultralytics.
"""

import streamlit as st
from ultralytics import RTDETR
import os


@st.cache_resource(show_spinner="Loading detection model...")
def load_model(model_path: str = "best.pt"):
    """
    Load the RT-DETR model from the given path.
    Caches the model in session to avoid reloading on each run.

    Args:
        model_path (str): Path to the .pt model weights file.

    Returns:
        RTDETR model instance, or None if loading fails.
    """
    if not os.path.exists(model_path):
        st.error(
            f"❌ Model file `{model_path}` not found. "
            "Please place `best.pt` in the project root directory."
        )
        return None

    try:
        model = RTDETR(model_path)
        return model
    except Exception as e:
        st.error(f"❌ Failed to load model: {e}")
        return None
