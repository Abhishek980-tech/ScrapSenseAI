

import streamlit as st
import pandas as pd
from PIL import Image
import io

# ── Module imports ────────────────────────────────────────────────────────────
from modules.model_loader import load_model
from modules.image_processing import enhance_underwater_image
from modules.detection import run_detection, DETECTION_CLASSES
from modules.report_manager import save_report, save_detection_report, load_reports, get_valid_map_reports
from modules.map_view import build_pollution_map
from streamlit_folium import st_folium
from modules.auth import create_user, verify_user
from modules.db import check_db_connection

# PAGE CONFIGURATION

if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

st.set_page_config(
    page_title="ScrapSenseAI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS 
st.markdown("""
<style>
    /* ── Global font & background ── */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }

    /* ── Header banner ── */
    .app-header {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6b8a 50%, #22a6b3 100%);
        padding: 1.6rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .app-header h1 {
        color: #ffffff;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 0;
    }
    .app-header p {
        color: #b2ebf2;
        font-size: 1rem;
        margin-top: 0.4rem;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: linear-gradient(135deg, #1a6b8a, #22a6b3);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 3px 12px rgba(0,0,0,0.15);
        color: white;
    }
    .metric-card h2 { font-size: 2rem; margin: 0; }
    .metric-card p  { font-size: 0.9rem; margin: 0.2rem 0 0; opacity: 0.85; }

    /* ── Section headings ── */
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0a3d62;
        border-left: 4px solid #22a6b3;
        padding-left: 0.6rem;
        margin: 1.2rem 0 0.6rem;
    }

    /* ── About tech badges ── */
    .tech-badge {
        display: inline-block;
        background: #e0f7fa;
        color: #00838f;
        border: 1px solid #b2ebf2;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* ── Sidebar tweaks ── */
    [data-testid="stSidebar"] {
        background: #0a3d62;
    }
    [data-testid="stSidebar"] * {
        color: #e0f7fa !important;
    }

    /* ── Success / Info boxes ── */
    .success-box {
        background: #e8f5e9;
        border-left: 5px solid #43a047;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        color: #1b5e20;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# HEADER


st.markdown("""
<div class="app-header">
    <h1>🌊 ScrapSenseAI</h1>
    <p>Underwater Automated Trash Detection & Classification System</p>
</div>
""", unsafe_allow_html=True)

# SIDEBAR SETTINGS

with st.sidebar:
    st.markdown("## ⚙️ Detection Settings")
    st.markdown("---")

    confidence_threshold = st.slider(
        label="Confidence Threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.35,
        step=0.05,
        help="Objects detected below this score are labeled as 'Unknown Debris'."
    )

    st.markdown(f"""
    <div style='margin-top:0.5rem; font-size:0.85rem; color:#b2ebf2;'>
        Current threshold: <strong>{confidence_threshold:.2f}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗑️ Detectable Classes")
    for cls in DETECTION_CLASSES:
        st.markdown(f"• `{cls}`")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.78rem; color:#90caf9; text-align:center;'>"
        "ScrapSenseAI v1.0<br>Powered by RT-DETR + OpenCV"
        "</div>",
        unsafe_allow_html=True
    )


# LOAD MODEL (cached across all tabs)


model = load_model("best.pt")


# TABS

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Trash Detection",
    "📊 Detection Analytics",
    "📋 Community Reports",
    "🗺️ Global Pollution Map",
    "ℹ️ About Project"
])


# AUTH
st.sidebar.markdown("## 🔐 Account")

db_connection_error = None
try:
    check_db_connection()
except Exception as exc:
    db_connection_error = str(exc)

if db_connection_error:
    st.sidebar.error(
        "Database connection failed. "
        "Please verify Streamlit Secrets and MongoDB Atlas network access."
    )
    st.sidebar.markdown(f"**Detail:** {db_connection_error}")

if st.session_state["auth_user"] is None:
    auth_tab1, auth_tab2 = st.sidebar.tabs(["Login", "Signup"])

    with auth_tab1:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if db_connection_error:
                st.error("Login disabled: database connection is unavailable.")
                st.stop()

            try:
                user = verify_user(login_email, login_password)
            except ConnectionError as exc:
                st.error(f"Login failed: {exc}")
                user = None
            except Exception as exc:
                st.error(f"Login failed: {exc}")
                user = None

            if user:
                st.session_state["auth_user"] = {
                    "name": user.get("name", "User"),
                    "email": user.get("email")
                }
                st.success("Logged in successfully")
                st.rerun()
            else:
                if login_email and login_password and not db_connection_error:
                    st.error("Invalid email or password")

    with auth_tab2:
        signup_name = st.text_input("Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account"):
            if db_connection_error:
                st.error("Signup disabled: database connection is unavailable.")
                st.stop()

            if len(signup_password) < 8:
                st.warning("Password must be at least 8 characters")
            else:
                try:
                    ok, msg = create_user(signup_name, signup_email, signup_password)
                except ConnectionError as exc:
                    ok = False
                    msg = f"Account creation failed: {exc}"
                except Exception as exc:
                    ok = False
                    msg = f"Account creation failed: {exc}"

                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
else:
    user = st.session_state["auth_user"]
    st.sidebar.success(f"Logged in as {user['name']}")
    if st.sidebar.button("Logout"):
        st.session_state["auth_user"] = None
        st.rerun()


if st.session_state["auth_user"] is None:
    st.warning("Please log in to submit a report.")
    st.stop()

# TAB 1 – TRASH DETECTION


with tab1:
    st.markdown('<p class="section-title">Upload an Underwater Image for Detection</p>', unsafe_allow_html=True)
    st.markdown(
        "Upload a JPG, JPEG, PNG, BMP, TIFF, WebP, or TIF image of an underwater scene. "
        #"The system will enhance it using **Dark Channel Prior** and then run **RT-DETR** detection."
    )

    uploaded_file = st.file_uploader(
        label="Choose an underwater image",
        type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
        help="Supported formats: JPG, JPEG, PNG, BMP, TIFF, WebP"
    )

    if uploaded_file is not None:
        if model is None:
            st.error("⚠️ Model is not loaded. Please check that `best.pt` exists in the project root.")
        else:
            # Read uploaded image
            original_image = Image.open(uploaded_file).convert("RGB")

            with st.spinner("🔵 Enhancing image with Dark Channel Prior..."):
                enhanced_image = enhance_underwater_image(original_image)

            with st.spinner("🟡 Running RT-DETR detection..."):
                annotated_image, detections = run_detection(
                    model, enhanced_image, confidence_threshold
                )

            # Display results
            st.markdown('<p class="section-title">Detection Results</p>', unsafe_allow_html=True)

            col_orig, col_detect = st.columns(2)

            with col_orig:
                st.markdown("**Original Image**")
                st.image(original_image, use_container_width=True, caption="Uploaded Image")

            with col_detect:
                st.markdown("**Detected Objects**")
                st.image(annotated_image, use_container_width=True, caption="RT-DETR Detections")

            # Detection Summary Metrics
            st.markdown('<p class="section-title">Detection Summary</p>', unsafe_allow_html=True)

            if detections:
                num_detected = len(detections)

                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{num_detected}</h2>
                        <p>Total Objects Detected</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_m2:
                    unique_classes = len(set(d["label"] for d in detections))
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{unique_classes}</h2>
                        <p>Unique Classes Found</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_m3:
                    avg_conf = sum(d["confidence"] for d in detections) / num_detected
                    st.markdown(f"""
                    <div class="metric-card">
                        <h2>{avg_conf:.2f}</h2>
                        <p>Average Confidence</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("")

# Table of individual detections
                det_df = pd.DataFrame(detections)[["label", "confidence", "bbox"]]
                det_df.columns = ["Class Label", "Confidence", "Bounding Box [x1,y1,x2,y2]"]
                det_df.index += 1
                st.dataframe(det_df, use_container_width=True)

                # Store in session state for Analytics tab
                st.session_state["last_detections"] = detections
                
                # Save Detection Report Section
                st.markdown("---")
                st.markdown('<p class="section-title">💾 Save Detection Report</p>', unsafe_allow_html=True)
                st.markdown("Save these detection results to the database and map.")
                
                with st.form("detection_save_form", clear_on_submit=True):
                    col_loc1, col_loc2 = st.columns(2)
                    with col_loc1:
                        det_location_name = st.text_input("📍 Location Name", placeholder="e.g. Great Barrier Reef, Australia", key="det_location")
                    with col_loc2:
                        det_latitude = st.number_input("🌐 Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.0001, format="%.4f", key="det_lat")
                        det_longitude = st.number_input("🌐 Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.0001, format="%.4f", key="det_lon")
                    
                    save_detect_btn = st.form_submit_button("💾 Save Detection", use_container_width=True)
                
                if save_detect_btn:
                    # Filter out Unknown Debris for saving
                    valid_detections = [d for d in detections if d["label"] != "Unknown Debris"]
                    if not valid_detections:
                        st.warning("⚠️ No valid debris detected to save.")
                    elif not det_location_name.strip():
                        st.warning("⚠️ Please enter a location name.")
                    elif abs(det_latitude) < 1e-6 and abs(det_longitude) < 1e-6:
                        st.warning("⚠️ Please enter valid coordinates (0.0,0.0 is not accepted).")
                    else:
                        success = save_detection_report(
                            detections=valid_detections,
                            location_name=det_location_name,
                            latitude=det_latitude,
                            longitude=det_longitude,
                            user_email=st.session_state["auth_user"]["email"]
                        )
                        if success:
                            st.markdown(
                                '<div class="success-box">✅ Detection report saved successfully! '
                                'View it on the Global Pollution Map.</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("❌ Failed to save detection report.")

            else:
                st.info("✅ No debris detected in this image at the selected confidence threshold.")
                st.session_state["last_detections"] = []

    else:
        # Placeholder when no image is uploaded
        st.markdown("""
        <div style="text-align:center; padding: 3rem; background: #e0f7fa;
                    border-radius: 12px; color: #00838f;">
            <h3>📂 No Image Uploaded</h3>
            <p>Use the file uploader above to get started.</p>
        </div>
        """, unsafe_allow_html=True)


# TAB 2 – DETECTION ANALYTICS

with tab2:
    st.markdown('<p class="section-title">Detection Analytics</p>', unsafe_allow_html=True)
    st.markdown("Statistics from the most recent detection run.")

    detections = st.session_state.get("last_detections", [])

    if not detections:
        st.info("📭 No detections yet. Go to the **Trash Detection** tab and upload an image first.")
    else:
        total = len(detections)

        # Summary Metrics 
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{total}</h2>
                <p>Total Objects Detected</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            unique_cls = len(set(d["label"] for d in detections))
            st.markdown(f"""
            <div class="metric-card">
                <h2>{unique_cls}</h2>
                <p>Unique Debris Classes</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            avg_conf = sum(d["confidence"] for d in detections) / total
            st.markdown(f"""
            <div class="metric-card">
                <h2>{avg_conf:.2f}</h2>
                <p>Avg. Confidence Score</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Class Count Breakdown 
        st.markdown('<p class="section-title">Objects Detected per Class</p>', unsafe_allow_html=True)

        label_counts = {}
        for d in detections:
            lbl = d["label"]
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

        count_df = pd.DataFrame(
            list(label_counts.items()),
            columns=["Class", "Count"]
        ).sort_values("Count", ascending=False).reset_index(drop=True)
        count_df.index += 1

        col_table, col_chart = st.columns([1, 2])

        with col_table:
            st.markdown("**Count Table**")
            st.dataframe(count_df, use_container_width=True)

        with col_chart:
            st.markdown("**Bar Chart**")
            st.bar_chart(count_df.set_index("Class")["Count"])
# CONFIDENCE SCORE DISTRIBUTION
        st.markdown('<p class="section-title">Confidence Score Distribution</p>', unsafe_allow_html=True)

        conf_df = pd.DataFrame({
            "Detection #": list(range(1, total + 1)),
            "Confidence": [d["confidence"] for d in detections],
            "Label": [d["label"] for d in detections]
        })

        st.line_chart(conf_df.set_index("Detection #")["Confidence"])


# COMMUNITY REPORTS
with tab3:
    st.markdown('<p class="section-title">Submit a Marine Pollution Report</p>', unsafe_allow_html=True)
    st.markdown("Help us track ocean pollution. Fill out the form below to report a sighting.")

    with st.form("report_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            reporter_name = st.text_input("👤 Your Name", placeholder="e.g. Jane Doe")
            location_name = st.text_input("📍 Location Name", placeholder="e.g. Great Barrier Reef, Australia")

        with col_b:
            latitude = st.number_input("🌐 Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.0001, format="%.4f")
            longitude = st.number_input("🌐 Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.0001, format="%.4f")

        description = st.text_area(
            "📝 Description",
            placeholder="Describe what type of debris or pollution was observed...",
            height=120
        )

        image_upload = st.file_uploader(
            "📷 Optional: Upload an Image",
            type=["jpg", "jpeg", "png", "bmp","tiff","webp"],
            help="You can attach a photo of the pollution site."
        )

        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)

    if submitted:
        if not reporter_name.strip():
            st.warning("⚠️ Please enter your name before submitting.")
        elif not location_name.strip():
            st.warning("⚠️ Please enter a location name before submitting.")
        elif not description.strip():
            st.warning("⚠️ Please add a description before submitting.")
        elif abs(latitude) < 1e-6 and abs(longitude) < 1e-6:
            st.warning("⚠️ Please enter valid latitude and longitude values. 0.0,0.0 is not accepted.")
        else:
            success = save_report(
                name=reporter_name,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude,
                description=description,
                user_email=st.session_state["auth_user"]["email"]
            )
            if success:
                st.markdown(
                    '<div class="success-box">✅ Report submitted successfully! '
                    'Thank you for contributing to ocean health monitoring.</div>',
                    unsafe_allow_html=True
                )
            else:
                st.error("❌ Failed to save the report. Please try again.")

# Display all reports in a table
    st.markdown('<p class="section-title">All Submitted Reports</p>', unsafe_allow_html=True)

    all_reports = load_reports()

    if all_reports.empty:
        st.info("📭 No reports have been submitted yet. Be the first to report!")
    else:
        st.markdown(f"**{len(all_reports)}** report(s) submitted so far.")
        all_reports = all_reports.rename(columns={
            "name": "Name",
            "location_name": "Location",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "description": "Description",
            "timestamp": "Timestamp",
            "source": "Source",
            "user_email": "User Email"
        })
        display_cols = [c for c in ["Name", "Location", "Latitude", "Longitude", "Description", "Timestamp", "Source", "User Email"]
                        if c in all_reports.columns]
        st.dataframe(all_reports[display_cols], use_container_width=True)


# TAB 4 – GLOBAL POLLUTION MAP
with tab4:
    st.markdown('<p class="section-title">Global Marine Pollution Map</p>', unsafe_allow_html=True)
    st.markdown(
        "This map shows community-submitted pollution reports from around the world. "
        "Click on any marker to view report details."
    )

    map_reports = get_valid_map_reports()

    if map_reports.empty:
        st.info("🗺️ No geolocated reports yet. Submit one in the **Community Reports** tab!")
    else:
        st.markdown(f"📌 Showing **{len(map_reports)}** report(s) on the map.")

    # Build and render the Folium map
    pollution_map = build_pollution_map(map_reports)

    st_folium(
        pollution_map,
        width="100%",
        height=540,
        returned_objects=[]
    )


# TAB 5 – ABOUT PROJECT

with tab5:
    st.markdown('<p class="section-title">About ScrapSenseAI</p>', unsafe_allow_html=True)

    col_info, col_tech = st.columns([3, 2])

    with col_info:
        st.markdown("""
        ### 🌊 Project Overview

        **ScrapSenseAI** is an intelligent, deep-learning-powered system designed to
        automatically **detect and classify underwater debris** from images.

        Ocean pollution is one of the most pressing environmental challenges of our time —
        millions of tonnes of plastic and waste enter marine ecosystems every year.
        Traditional monitoring methods are slow, expensive, and labour-intensive.

        ScrapSenseAI tackles this challenge by leveraging state-of-the-art **real-time
        object detection** combined with **image enhancement techniques** tailored for
        murky underwater environments.

        ---

        ### 🎯 Project Goals

        - **Automated Detection:** Identify 15 types of underwater trash with high accuracy.
        - **Image Enhancement:** Use Dark Channel Prior (DCP) to improve visibility
          in turbid, low-light underwater images.
        - **Community Engagement:** Enable citizen scientists to submit geotagged
          pollution reports from anywhere in the world.
        - **Global Monitoring:** Visualize pollution hotspots on an interactive map.
        - **Scalable Architecture:** Modular, production-ready codebase built for extension.

        ---

        ### 🗑️ Detectable Debris Classes (15)

        The model can identify the following underwater waste categories:
        """)

        cols = st.columns(3)
        for i, cls in enumerate(DETECTION_CLASSES):
            cols[i % 3].markdown(f"✅ `{cls}`")

    with col_tech:
        st.markdown("### 🛠️ Technology Stack")

        tech_stack = {
            "🤖 Object Detection":  "RT-DETR (Ultralytics)",
            "🖼️ Image Enhancement": "Dark Channel Prior (OpenCV)",
            "🧠 Deep Learning":     "PyTorch",
            "🌐 Web Framework":     "Streamlit",
            "🗺️ Mapping":           "Folium + Streamlit-Folium",
            "📊 Data Analysis":     "Pandas + NumPy",
            "🐍 Language":          "Python 3.10+",
            "📦 Image Processing":  "Pillow + OpenCV",
        }

        for tech, value in tech_stack.items():
            st.markdown(f"""
            <div style="background:#e0f7fa; border-radius:8px; padding:0.5rem 0.8rem;
                        margin-bottom:0.5rem; border-left:4px solid #22a6b3;">
                <strong>{tech}</strong><br>
                <span style="color:#00838f;">{value}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    ### 🔬 How It Works

    1. **Upload** – User uploads an underwater image (JPG/PNG).
    2. **Enhance** – Dark Channel Prior removes haze and improves contrast in murky water.
    3. **Detect** – RT-DETR runs inference to locate and classify debris objects.
    4. **Annotate** – Bounding boxes are drawn with class labels and confidence scores.
    5. **Analyse** – Detection stats and charts are generated automatically.
    6. **Report** – Users can submit geotagged pollution reports to the community database.
    7. **Map** – All reports appear as interactive markers on the global pollution map.

    ---

    > *"Every piece of trash detected is a step toward cleaner oceans."*
    """)
