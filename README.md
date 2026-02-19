<p align="center">
  <img src="https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F00?style=for-the-badge" />
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" />
</p>

<h1 align="center">🏢 TalentGrid</h1>

<p align="center">
  <strong>AI-Powered Smart Talent Sourcing Platform</strong><br/>
  <em>From raw CVs to ranked candidates — powered by RAG, Hybrid Search & Cross-Encoder Re-Ranking</em>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-ai-architecture">AI Architecture</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-getting-started">Getting Started</a> •
  <a href="#-project-structure">Project Structure</a> •
  <a href="#-team">Team</a>
</p>

---

## About

**TalentGrid** is a full-stack, AI-powered talent sourcing platform built as a capstone project for the **AI Innovator Pathway** program. It solves a real-world recruitment challenge: matching talent to roles relies heavily on manual review and subjective judgment, making the process slow, inconsistent, and difficult to scale.

TalentGrid automates the entire pipeline — from uploading a raw CV (PDF/DOCX) to enabling recruiters to search candidates using natural language queries like:

> _"Find me a senior React developer with 5+ years who speaks Arabic"_

The system parses CVs using AI-powered OCR, structures them with LLMs, embeds them into a vector database, and retrieves the best matches using a hybrid semantic + keyword search with cross-encoder re-ranking.

---

## Features

- ** AI-Powered CV Parsing** — Mistral OCR extracts text from any PDF (even scanned), then Groq/Gemini structures it into a consistent schema
- ** Hybrid Search** — Combines semantic vector search with BM25 keyword matching using dynamic weights based on query type
- ** Cross-Encoder Re-Ranking** — Cohere's cross-encoder re-scores results for precision
- ** Dashboard & Analytics** — Real-time stats on your talent pipeline
- ** Multi-Source Import** — Upload CVs via drag & drop or import from Gmail
- ** Rich Candidate Profiles** — Detailed view with skills, experience, education, and AI match scores
- ** Authentication** — JWT-based auth with registration and login
- ** Real-Time Processing** — Live status updates as CVs are parsed and indexed
- ** Advanced Filters** — Filter by experience range, languages, and location

---

## 📸 Screenshots

### Login Page

<p align="center">
  <img src="screenshots/login.jpg" alt="Login Page" width="750" />
</p>

### Registration Page

<p align="center">
  <img src="screenshots/register.jpg" alt="Registration Page" width="750" />
</p>

### Dashboard

<p align="center">
  <img src="screenshots/dashboard.jpg" alt="Dashboard" width="750" />
</p>

### CV Import & AI Ingestion

<p align="center">
  <img src="screenshots/import.jpg" alt="Multi-Source CV Ingestion" width="750" />
</p>

### Talent Search & Results

<p align="center">
  <img src="screenshots/search.jpg" alt="Search Results with AI Matching" width="750" />
</p>

### Candidate Profile

<p align="center">
  <img src="screenshots/candidate_profile.jpg" alt="Candidate Profile with AI Insights" width="750" />
</p>

---

## AI Architecture

TalentGrid implements a **production-grade RAG (Retrieval-Augmented Generation)** pipeline with three major stages:

```
┌──────────────┐   ┌────────────────┐   ┌───────────────┐   ┌────────────────┐
│  CV Upload   │──▶│  Mistral OCR   │──▶│  CVChunker    │──▶│   Embedder     │
│  (PDF/DOCX)  │   │  + Groq/Gemini │   │ (field-based) │   │ all-mpnet-v2   │
└──────────────┘   └────────────────┘   └───────────────┘   └───────┬────────┘
                                                                     │
                                                            ┌────────▼────────┐
                                                            │    ChromaDB     │
                                                            │  (persistent)   │
                                                            └────────┬────────┘
                                                                     │
┌──────────────┐   ┌────────────────┐   ┌───────────────┐   ┌────────▼────────┐
│ Ranked       │◀──│ Cross-Encoder  │◀──│ Hybrid Search │◀──│  Query Parser   │
│ Candidates   │   │ Cohere Rerank  │   │ Vector + BM25 │   │  + Filters      │
└──────────────┘   └────────────────┘   └───────────────┘   └─────────────────┘
```

### Stage 1: CV Ingestion Pipeline

| Step  | Component                                  | What It Does                                                          |
| ----- | ------------------------------------------ | --------------------------------------------------------------------- |
| Load  | **Mistral OCR**                            | Extracts text from PDFs (even scanned/designed CVs)                   |
| Parse | **Groq (Llama 3.3 70B)** → Gemini fallback | Structures raw text into JSON (name, skills, experience, etc.)        |
| Chunk | **Custom CVChunker**                       | Splits CV by semantic fields (profile, skills, experience, education) |
| Embed | **all-mpnet-base-v2**                      | Converts each chunk into a 768-dimensional vector                     |
| Store | **ChromaDB**                               | Persistent vector storage with metadata filtering                     |

### Stage 2: Hybrid Retrieval

- **Semantic search** (vector similarity) for understanding meaning
- **BM25 keyword search** with synonym expansion, stop-word filtering, and tech-skill boosting
- **Dynamic weights**: skill queries → 80% keyword / 20% semantic; job descriptions → 60% semantic / 40% keyword

### Stage 3: Cross-Encoder Re-Ranking

- **Cohere Rerank API** re-scores the top ~20 results using a cross-encoder model
- Cross-encoders analyze query + document _together_ for much higher precision
- Graceful fallback to retrieval scores if Cohere is unavailable

---

## 🛠️ Tech Stack

### Frontend

| Technology      | Purpose                 |
| --------------- | ----------------------- |
| React 18        | UI framework            |
| Vite            | Build tool & dev server |
| TailwindCSS     | Utility-first styling   |
| React Router v6 | Client-side routing     |
| React Query     | Server state management |
| Recharts        | Analytics charts        |
| Lucide React    | Icon library            |
| Axios           | HTTP client             |

### Backend

| Technology  | Purpose              |
| ----------- | -------------------- |
| FastAPI     | Python web framework |
| SQLAlchemy  | ORM for PostgreSQL   |
| Pydantic    | Data validation      |
| JWT (PyJWT) | Authentication       |
| Uvicorn     | ASGI server          |

### AI / ML

| Technology                               | Purpose                    |
| ---------------------------------------- | -------------------------- |
| Mistral OCR                              | PDF text extraction        |
| Groq (Llama 3.3 70B)                     | Primary LLM for CV parsing |
| Google Gemini 2.0 Flash                  | Fallback LLM               |
| SentenceTransformers (all-mpnet-base-v2) | Text embeddings (768d)     |
| ChromaDB                                 | Persistent vector store    |
| Cohere Rerank                            | Cross-encoder re-ranking   |

### Infrastructure

| Technology   | Purpose                      |
| ------------ | ---------------------------- |
| PostgreSQL   | Relational database          |
| ChromaDB     | Vector database (persistent) |
| Gmail OAuth2 | CV import from email         |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL

### 1. Clone the repository

```bash
git clone https://github.com/your-username/talentgrid.git
cd talentgrid
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/talentgrid

# JWT
SECRET_KEY=your-secret-key

# AI API Keys
MISTRAL_API_KEY=your-mistral-key
GROQ_API_KEY=your-groq-key
GOOGLE_API_KEY=your-google-key
COHERE_API_KEY=your-cohere-key

# Optional
HF_TOKEN=your-huggingface-token
LANGSMITH_API_KEY=your-langsmith-key
```

```bash
# Run the backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Index Existing Candidates (Optional)

If you have candidates in the database that need to be indexed into ChromaDB:

```bash
cd backend
python reindex_candidates.py
```

---

## 📁 Project Structure

```
talentgrid/
├── backend/
│   ├── app/
│   │   ├── ai/                          #  AI Module
│   │   │   ├── ingestion/
│   │   │   │   ├── parser.py            # Mistral OCR + Groq/Gemini parsing
│   │   │   │   ├── chunker.py           # Semantic field-based CV chunking
│   │   │   │   ├── embedder.py          # all-mpnet-base-v2 embeddings
│   │   │   │   └── pipeline.py          # Orchestrates chunk → embed → store
│   │   │   ├── retrieval/
│   │   │   │   ├── query_parser.py      # Filter translation (UI → ChromaDB)
│   │   │   │   ├── retriever.py         # Orchestrates search pipeline
│   │   │   │   └── hybrid_search.py     # Vector + BM25 with dynamic weights
│   │   │   ├── ranking/
│   │   │   │   └── cross_encoder.py     # Cohere re-ranking
│   │   │   ├── storage/
│   │   │   │   └── vector_store.py      # ChromaDB persistent storage
│   │   │   └── service.py               # Unified AI service facade
│   │   ├── models/                      # SQLAlchemy models
│   │   ├── routes/                      # API endpoints
│   │   │   ├── auth.py                  # Authentication
│   │   │   ├── candidates.py            # CRUD operations
│   │   │   ├── search.py               # RAG-powered search
│   │   │   ├── import_cv.py            # CV upload & parsing
│   │   │   ├── gmail.py                # Gmail CV import
│   │   │   ├── analytics.py            # Dashboard stats
│   │   │   └── admin.py                # Reindexing tools
│   │   ├── services/                    # Business logic
│   │   ├── schemas/                     # Pydantic schemas
│   │   ├── config.py                    # Settings & env vars
│   │   ├── database.py                  # DB connection
│   │   └── main.py                      # FastAPI app entry
│   ├── chroma_db/                       # Persistent vector store
│   ├── requirements.txt
│   └── reindex_candidates.py            # Bulk re-indexing script
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/                  # Navbar, Sidebar
│   │   │   ├── common/                  # Button, Card, Input, etc.
│   │   │   ├── features/               # CandidateCard, etc.
│   │   │   └── auth/                   # PrivateRoute
│   │   ├── pages/
│   │   │   ├── Auth/                   # Login, Register
│   │   │   ├── Onboarding/            # Welcome flow
│   │   │   ├── Dashboard/             # Main dashboard
│   │   │   ├── Search/                # AI-powered search
│   │   │   ├── Import/                # CV upload
│   │   │   ├── CandidateProfile/      # Detailed view
│   │   │   └── Analytics/             # Charts & stats
│   │   ├── contexts/                   # Auth context
│   │   ├── services/                   # API client
│   │   └── App.jsx                     # Router setup
│   ├── package.json
│   └── tailwind.config.js
│
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint                   | Description                             |
| ------ | -------------------------- | --------------------------------------- |
| `POST` | `/api/auth/register`       | Create new account                      |
| `POST` | `/api/auth/login`          | Login & get JWT token                   |
| `GET`  | `/api/candidates/`         | List all candidates                     |
| `GET`  | `/api/candidates/:id`      | Get candidate details                   |
| `POST` | `/api/import/upload`       | Upload & parse a CV                     |
| `POST` | `/api/search/`             | AI-powered semantic search              |
| `GET`  | `/api/analytics/dashboard` | Dashboard statistics                    |
| `POST` | `/api/admin/reindex`       | Re-index all candidates                 |
| `GET`  | `/docs`                    | Interactive API documentation (Swagger) |

---

## ⚙️ Environment Variables

| Variable            | Required | Description                        |
| ------------------- | -------- | ---------------------------------- |
| `DATABASE_URL`      | ✅       | PostgreSQL connection string       |
| `SECRET_KEY`        | ✅       | JWT signing key                    |
| `MISTRAL_API_KEY`   | ✅       | For CV OCR processing              |
| `GROQ_API_KEY`      | ✅       | Primary LLM (free: 14,400 req/day) |
| `GOOGLE_API_KEY`    | ⚡       | Fallback LLM (Gemini)              |
| `COHERE_API_KEY`    | ⚡       | Cross-encoder re-ranking           |
| `HF_TOKEN`          | ❌       | HuggingFace (for private models)   |
| `LANGSMITH_API_KEY` | ❌       | Tracing & debugging                |

> ✅ = Required &nbsp; ⚡ = Recommended &nbsp; ❌ = Optional

---

## 👥 Team

**Team A — AI Innovator Pathway**

| Name              | Role |
| ----------------- | ---- |
| Amina AlHaffar    |      |
| Salma Abou Shkair |      |
| Bayan Abo Razmeh  |      |
| Balsam Fater Deeb |      |
| Mohammad Mansour  |      |

---

## 📄 License

This project was built as a capstone project for the AI Innovator Pathway program under subul impact outsourcing

---

<p align="center">
  <strong>Built with ❤️ and a lot of ☕ by Team A</strong><br/>
  <em>AI Innovator Pathway — 2026</em>
</p>
