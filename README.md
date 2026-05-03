# 🌊 ScrapSenseAI
RemoteSigned)
Underwater Automated Trash Detection and Classification System using RT-DETR.


ScrapSenseAI uses a trained **RT-DETR** model to detect and classify 15 types of underwater debris in uploaded images. It also features community pollution reporting and a global interactive pollution map.

---

## ✨ Features

- 🔍 **Trash Detection** - Upload underwater images for automatic debris detection
- 📊 **Detection Analytics** - View statistics and charts from detection results
- 📋 **Community Reports** - Submit geotagged pollution reports
- 🗺️ **Global Pollution Map** - Interactive map of all submitted reports
- 🖼️ **Image Enhancement** - Dark Channel Prior for improving underwater image clarity

---

## 📁 Project Structure

```
ScrapSenseAI/
├── app.py                      # Main Streamlit application
├── best.pt                    # RT-DETR model weights (add this!)
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables
├── README.md                # This file
├── DATA/
│   ├── reports.csv          # Community pollution reports
│   └── results.csv          # Detection results
├── modules/
│   ├── __init__.py
│   ├── auth.py              # User authentication
│   ├── db.py               # MongoDB connection
│   ├── detection.py        # RT-DETR inference
│   ├── image_processing.py # Dark Channel Prior enhancement
│   ├── map_view.py        # Folium pollution map
│   ├── model_loader.py     # Model loading utilities
│   ├── mongo_setup.py    # MongoDB index setup
│   └── report_manager.py # Report CRUD operations
└── venv/                   # Virtual environment
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MongoDB (local or Atlas)

### Installation

1. **Clone the repository**
   ```bash
   cd ScrapSenseAI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add model weights**
   
   Place your trained `best.pt` file in the project root.

5. **Configure environment**
   
   Update `.env` with your MongoDB connection string:
   ```
   MONGODB_URI=mongodb://localhost:27017
   ```

6. **Setup MongoDB indexes**
   ```bash
   python -m modules.mongo_setup
   ```

7. **Run the application**
   ```bash
   streamlit run app.py
   ```

The app will open at `http://localhost:8501`

---

## 🎯 Detectable Classes (15)

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

---

## 🛠️ Tech Stack

- **RT-DETR** (Ultralytics) – Object Detection
- **OpenCV** – Image Enhancement
- **PyTorch** – Deep Learning
- **Streamlit** – Web Framework
- **MongoDB** – Database
- **Folium** – Interactive Maps

---

