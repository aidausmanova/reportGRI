# ReportGRI: Automating GRI Alignment and Report Assessment 

Prepared for the DEMO paper submission for CIKM 2025 (https://cikm2025.org/calls/demo-papers)
---
Welcome to the ReportGRI project repository. This tool provides easy visual analytics for corporate sustainability reports (CSRs) based on Global Reporting Initiative (GRI) disclsoure requirements. The reports are checked for GRI disclosure completeness and materiality and receive GRI indexing suggestions. As part of this project we are primarily focusing on: **Standardising unstructured data from CSRs, Creating environemntal, social, governance (ESG) benchamrking and Generating LLM-based assessment of report coverage**.

Main features of ReportGRI include:
- **GRI disclosure-paragrph distribution** of reports
- **Report topical focus** with respect to GRI standard topics
- **Disclosure assessment** for completeness and materiality
- **Upload your report** to view the GRI distribution and do comparative analysis with industry peers, and receive LLM-based indexing suggestions

---

## Prerequisites

- Node.js (>=18) and npm
- Python 3.10+ with pip
- Docker + Docker Compose (optional for Docker setup)

Clone the repository
```bash
git clone https://github.com/aidausmanova/reportGRI.git
cd reportGRI
```
---

## Backend Setup (FastAPI)

### Step 1: Create Virtual Environment

#### Windows
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run FastAPI
```bash
uvicorn main:app --reload
```

> Server will start at: http://localhost:8000

### Note
To use gpt-3.5-turbo-1106, create .env file and add your api key as in the example below:
```bash
OPENAI_API_KEY=<Your OpenAI key>
BASE_URL='https://api.openai.com/v1'
```
---

## Frontend Setup (React 19 + TailwindCSS)

### Step 1: Install Frontend Packages
```bash
cd frontend
npm install
```

### Step 2: Run Vite Dev Server
```bash
npm run dev
```

> Frontend will start at: http://localhost:5173

---

## Optional: Docker Setup (Combined)

### Step 1: Build and Start All Containers
```bash
docker-compose up --build
```

> Backend on http://localhost:8000  
> Frontend on http://localhost:5173

---

## Acknowledgements
- Leuphana University
