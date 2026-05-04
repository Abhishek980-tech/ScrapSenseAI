"""
model_loader.py
---------------
Handles loading of the RT-DETR object detection model using Ultralytics.
"""

import streamlit as st



import os
import streamlit as st


@st.cache_resource(show_spinner="Loading detection model...")
def load_model(model_path: str = "best.pt"):
    try:
        from ultralytics import RTDETR
    except ImportError:
        st.error(
            "❌ Missing dependency: OpenCV is required by Ultralytics. "
            "Install it with `pip install opencv-python-headless` or `pip install -r requirements.txt`."
        )
        return None

    """
    Load the RT-DETR model from the given path.
    Caches the model in session to avoid reloading on each run.

    Args:
        model_path (str): Path to the .pt model weights file.

    Returns:
        RTDETR model instance, or None if loading fails.
    """
    candidate_paths = [
        model_path,
        os.path.join(os.getcwd(), model_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), model_path),
        os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), model_path),
    ]

    model_file = None
    for path in candidate_paths:
        if os.path.exists(path):
            model_file = path
            break

    if model_file is None:
        attempted = "\n".join([f"- {p}" for p in candidate_paths])
        st.error(
            f"❌ Model file `{model_path}` not found. Tried the following locations:\n{attempted}\n"
            "Please place `best.pt` in the project root or in the same folder as `app.py`."
        )
        return None

    try:



        model = RTDETR(model_file)
        return model
    except Exception as e:
        st.error(f"❌ Failed to load model from `{model_file}`: {e}")

        from ultralytics import RTDETR
        model = RTDETR(model_path)
        return model

        from ultralytics import RTDETR

        return RTDETR(model_path)


        from ultralytics import RTDETR

        return RTDETR(model_path)

    except Exception as e:
        st.error(
            "❌ Failed to load model. "
            "This environment may be missing system OpenCV dependencies (e.g., libGL). "
            f"Details: {e}"
        )



        return None
