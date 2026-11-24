# 🌾 KRISHI Intelligence

**AI-Powered Farm Digital Twin & Precision Agriculture Decision-Support System**

🔗 **[Live App](https://krishi-intelligence.vercel.app)** | **[API Docs](https://krishi-intelligence-api.onrender.com/docs)** | `FastAPI 0.115` · `Next.js 14` · `XGBoost 2.1` · `SQLAlchemy 2.0` · `116 Pytest Passed`

---

## Overview

**KRISHI Intelligence** bridges the gap between raw agronomic data and actionable field decisions for smallholder farmers. By combining a real-time **Farm Digital Twin** with machine learning yield and risk models and localized market intelligence, the platform helps farmers optimize irrigation, input allocation, and mandi selling windows.

## Key Features

* **Farm Digital Twin:** Models crop phenology stages, soil moisture and nutrient profiles, and localized weather impacts across the crop lifecycle.
* **AI What-If Decision Engine:** Uses trained **XGBoost** and **scikit-learn** models to simulate yield outcomes, input costs, and climate risk across multiple intervention scenarios.
* **Mandi Intelligence & Net Profit Optimizer:** Compares nearby mandi commodity prices against transport and logistics costs to recommend the most profitable selling venue and timing.
* **RESTful API & Interactive Frontend:** High-performance FastAPI backend paired with a responsive Next.js 14 and TypeScript dashboard.

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS (Deployed on **Vercel**) |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy 2.0 (Deployed on **Render**) |
| **Machine Learning** | XGBoost 2.1, scikit-learn, pandas, NumPy |
| **Testing & Quality** | Pytest (116 automated unit & integration tests) |

## Architecture

- **Frontend (Vercel CDN):** Next.js 14 application routing `/api/*` requests seamlessly to the cloud backend.
- **Backend (Render Cloud):** FastAPI server handling REST endpoints, Pydantic validation, SQLAlchemy 2.0 persistence, and XGBoost ML inference.

## Local Setup & Installation

### 1. Clone the Repository
    git clone https://github.com/AryanCodes352/krishi-intelligence.git
    cd krishi-intelligence

### 2. Backend Setup (FastAPI)
    cd backend
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

API Swagger documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup (Next.js)
    cd frontend
    npm install
    npm run dev

Frontend application will run at `http://localhost:3000`.

### 4. Run Automated Tests
    cd backend
    pytest

## Author

Built and deployed end-to-end by **Aryan** ([GitHub](https://github.com/AryanCodes352)).
