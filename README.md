# 🌿 Athena: AI-Powered Utility Vegetation Management (UVM) Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white&style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black&style=flat-square)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?logo=pytorch&logoColor=white&style=flat-square)

> **"Protecting the grid, preserving the wild."**  
> Athena is an AI-powered Utility Vegetation Management (UVM) platform designed to autonomously identify, assess, and mitigate wildfire risks caused by vegetation encroachment on power lines.

---

## Mission

Wildfires caused by power line failures are a catastrophic and recurring problem. Athena bridges the gap between **Macro-Scale Analysis** (Satellite/OSM) and **Micro-Scale precision** (Drone/Computer Vision) to provide utility operators with a unified, real-time risk assessment dashboard.

## Key Features

### Macro Scanner
*Identify risks from the sky.*
- **Geospatial Intelligence**: Ingests power line data from **OpenStreetMap (OSM)** and satellite imagery.
- **Risk Heatmaps**: Automatically calculates risk scores for thousands of assets based on location and historical data.
- **Interactive Map**: A high-performance **React Leaflet** map visualizing critical hotspots across California.

### Micro Inspector
*Validate threats with precision.*
- **Drone Simulation**: Simulates a live drone inspection feed for high-risk zones.
- **Computer Vision**: Deployed a custom **U-Net Semantic Segmentation** model (trained on the TTPLA dataset) to distinguish between:
    - 🔴 **Vegetation** (Trees/Shrubs)
    - 🔵 **Power Lines** (Cables)
    - 🟡 **Towers**
- **Real-Time Inference**: Detects intersections between vegetation and cables to flag **"Critical Encroachment"** instantly.

---

## Tech Stack

| Component | Technologies |
|-----------|--------------|
| **Frontend** | React, Vite, Tailwind CSS, React Leaflet, Lucide Icons |
| **Backend** | Python, Flask, GeoPandas, OSMnx, Shapely |
| **AI / ML** | PyTorch, Segmentation Models, OpenCV, NumPy |
| **Data** | OpenStreetMap, TTPLA Dataset (Aerial Power Lines) |

---

## Dashboard Preview

### 1. The Command Center
*A dark-mode, futuristic map interface for monitoring grid health.*
*![Dashboard Placeholder](https://via.placeholder.com/800x400?text=Athena+Command+Center)*

### 2. AI Inference
*Micro-Inspector detecting a tree branch touching a high-voltage line.*
*![Inference Placeholder](https://via.placeholder.com/800x400?text=U-Net+Segmentation+Output)*

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
- Open `http://localhost:5173` in your browser.
- Click on any **Red (Critical)** hotspot on the map.
- Click **"Launch Drone"** to see the simulated view.
- Click **"Run Inference"** to let the AI analyze the image!

---

## 🧠 Model Training

The core AI model is a **U-Net** architecture with a **ResNet-18** backbone, trained on the **TTPLA** dataset.

```python
# Sample Inference Code
model = smp.Unet(encoder_name="resnet18", classes=4)
mask = model(image_tensor)
risk = check_intersection(mask['vegetation'], mask['cable'])
```

---

## 🔮 Future Roadmap

- [ ] **LiDAR Integration**: 3D depth analysis for precise clearance measurement.
- [ ] **Predictive Growth**: Use historical weather data to predict vegetation growth rates.
- [ ] **Work Order Automation**: Automatically dispatch tree-trimming crews to critical zones.

---

Made with by **Edwin Kim**
