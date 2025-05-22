# Sustainability Reports Analyzer

Prepared for the DEMO paper submission for CIKM 2025 (https://cikm2025.org/calls/demo-papers)
---

## 🚀 Features

- **GRI Distribution** of few already published reports
- **Upload your report** to view the GRI distribution and do comparative analysis with industry peers
- 
-

---

## 🧠 Prerequisites

- Node.js (>=18) and npm
- Python 3.9+ with pip
- git

### Optional (for Docker setup):
- Docker + Docker Compose

---

## 🛠️ Setup Instructions

### ✅ Clone the Repository
```bash
git clone https://github.com/abdullah-rana/sustainability-reports-analyzer.git
cd sustainability-reports-analyzer
```

---

## ⚙️ Backend Setup (FastAPI)

### 📦 Step 1: Create Virtual Environment

#### 🪟 Windows
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### 🐧 Linux / macOS
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 📦 Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### ▶️ Step 3: Run FastAPI
```bash
uvicorn main:app --reload
```

> Server will start at: http://localhost:8000

---

## 🎨 Frontend Setup (React 19 + TailwindCSS)

### 📦 Step 1: Install Frontend Packages
```bash
cd frontend
npm install
```

### ▶️ Step 2: Run Vite Dev Server
```bash
npm run dev
```

> Frontend will start at: http://localhost:5173

---

## 🧪 Optional: Docker Setup (Combined)

### Step 1: Build and Start All Containers
```bash
docker-compose up --build
```

> Backend on http://localhost:8000  
> Frontend on http://localhost:5173

---

## 👋 Acknowledgements
- Leuphana University
-
-