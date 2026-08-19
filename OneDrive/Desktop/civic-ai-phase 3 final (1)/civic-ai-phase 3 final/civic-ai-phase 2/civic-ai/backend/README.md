# Civic AI - FastAPI Backend

Production-ready backend API service for **Civic AI – Intelligent Community Emergency & Civic Problem Reporting System**.

## Technology Stack
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM / Database**: SQLAlchemy 2.0 / PostgreSQL (SQLite fallback for unit tests)
- **Validation & Serialization**: Pydantic v2
- **Authentication**: JWT (JSON Web Tokens) + Bcrypt password hashing
- **Testing**: Pytest + HTTPX

## Phase 1 Capabilities
- ✅ `GET /health`: Health verification endpoint
- ✅ `POST /auth/register`: Citizen registration with hashed passwords
- ✅ `POST /auth/login`: JWT token generation
- ✅ `GET /users/me`: Authenticated profile retrieval (excludes password hashes)
- ✅ `POST /incidents`: Incident creation with GPS coordinates
- ✅ `GET /incidents`: Incident listing with pagination
- ✅ `GET /incidents/{id}`: Single incident retrieval
- ✅ `PATCH /incidents/{id}`: Status and severity updates
- ✅ Centralized AI Taxonomy definitions & Incident Status Enums
- ✅ Automatic OpenAPI / Swagger docs at `/docs` and ReDoc at `/redoc`

## Local Development Setup

### 1. Virtual Environment Setup
```bash
cd backend
python -m venv .venv

# On Linux/macOS
source .venv/bin/activate

# On Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Dev Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run Pytest Test Suite
```bash
pytest -v
```
