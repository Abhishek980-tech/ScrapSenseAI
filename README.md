# 🌊 ScrapSenseAI
### Underwater Automated Trash Detection and Classification System

ScrapSenseAI uses a trained **RT-DETR** model to detect and classify 15 types of
underwater debris in uploaded images. It also features community pollution reporting
and a global interactive pollution map.

---

## 📁 Project Structure

```
ScrapSenseAI/
├── app.py                        ← Main Streamlit application
├── best.pt                       ← RT-DETR model weights (add this!)
├── requirements.txt
├── data/
│   └── reports.csv               ← Community pollution reports
└── modules/
    ├── __init__.py
    ├── model_loader.py           ← Load RT-DETR model
    ├── image_processing.py       ← Dark Channel Prior enhancement
    ├── detection.py              ← Run inference & draw bounding boxes
    ├── report_manager.py         ← Save/load community reports
    └── map_view.py               ← Generate Folium pollution map
```

---

## ⚙️ Setup Instructions

### 1. Clone / download the project
```bash
cd ScrapSenseAI
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your model weights
Place your trained `best.pt` file in the **project root** (same level as `app.py`):
```
ScrapSenseAI/
├── app.py
├── best.pt   ← here
```

### 5. Run the application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## 🗑️ Detectable Classes (15)

| # | Class | # | Class |
|---|-------|---|-------|
| 1 | Mask | 9 | net |
| 2 | can | 10 | pbag |
| 3 | cellphone | 11 | pbottle |
| 4 | electronics | 12 | plastic |
| 5 | gbottle | 13 | rod |
| 6 | glove | 14 | sunglasses |
| 7 | metal | 15 | tire |
| 8 | misc | | |

Objects detected below the confidence threshold are labeled **Unknown Debris**.

---

## 🛠️ Tech Stack

- **RT-DETR** (Ultralytics) – Real-Time Detection Transformer
- **OpenCV** – Dark Channel Prior image enhancement
- **PyTorch** – Deep learning backend
- **Streamlit** – Web application framework
- **Folium** – Interactive maps
- **Pandas / NumPy** – Data analytics

---

## 📊 Application Tabs

| Tab | Description |
|-----|-------------|
| 🔍 Trash Detection | Upload image → enhance → detect → annotate |
| 📊 Detection Analytics | Charts and stats from latest detection |
| 📋 Community Reports | Submit geotagged pollution reports |
| 🗺️ Global Pollution Map | Interactive map of all submitted reports |
| ℹ️ About Project | Project details and tech stack |
