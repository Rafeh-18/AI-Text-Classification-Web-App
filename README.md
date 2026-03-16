# AI Text Classification Web App

A full-stack web application for classifying text into 22 categories using machine learning. Built with **FastAPI** + **React**, using a TF-IDF + Logistic Regression pipeline trained on IMDB and 20 Newsgroups datasets.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite, python-jose, passlib[bcrypt] |
| ML | scikit-learn, TF-IDF + Logistic Regression, joblib |
| Frontend | React, Vite, Tailwind CSS, Axios, Zustand, react-hot-toast |
| Auth | JWT (Bearer tokens) |
| Testing | pytest, httpx |

---

## Project Structure

```
AI-Text-Classification-Web-App/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── database.py          # SQLAlchemy engine & session
│   │   ├── ml/
│   │   │   ├── data/                # Raw datasets (IMDB CSV)
│   │   │   ├── models/              # Trained model + label mapping
│   │   │   │   ├── text_classifier.joblib
│   │   │   │   └── label_mapping.json
│   │   │   ├── artifacts/           # Intermediate training outputs
│   │   │   └── src/
│   │   │       ├── preprocess.py    # Data loading & cleaning
│   │   │       ├── train.py         # Model training pipeline
│   │   │       └── predict.py       # Inference service (singleton)
│   │   ├── models/
│   │   │   └── user_model.py        # SQLAlchemy ORM models
│   │   ├── routes/
│   │   │   ├── auth_routes.py       # /auth endpoints
│   │   │   └── predict_routes.py    # /predict endpoints
│   │   ├── schemas/
│   │   │   └── user_schema.py       # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── auth_service.py      # Register, login, user lookup
│   │   │   └── predict_service.py   # Prediction + history CRUD
│   │   ├── utils/
│   │   │   └── security.py          # JWT creation & verification
│   │   ├── config.py                # Pydantic settings (reads .env)
│   │   └── main.py                  # FastAPI app entry point
│   └── tests/
│       ├── conftest.py              # Fixtures & test DB setup
│       ├── test_auth.py             # Auth endpoint tests
│       └── test_predict.py          # Prediction endpoint tests
├── frontend/
│   ├── src/
│   │   ├── components/              # Layout, ProtectedRoute, UI primitives
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── History.jsx
│   │   │   └── Profile.jsx
│   │   ├── services/
│   │   │   └── api.js               # Axios instance + auth/predict API
│   │   ├── store/
│   │   │   └── authStore.js         # Zustand auth state
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── .env                             # Environment variables (never commit)
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Clone & create virtual environment

```bash
git clone https://github.com/your-username/AI-Text-Classification-Web-App.git
cd AI-Text-Classification-Web-App
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

```bash
cp .env.example .env
```

Edit `.env` and set a real secret key:

```env
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./backend/app/database/app.db
MODEL_PATH=backend/app/ml/models/text_classifier.joblib
LABEL_MAPPING_PATH=backend/app/ml/models/label_mapping.json
```

Generate a secure key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Train the ML model (first-time setup)

```bash
# Place IMDB Dataset.csv in backend/app/ml/data/
python -m backend.app.ml.src.preprocess
python -m backend.app.ml.src.train
```

This produces `text_classifier.joblib` and `label_mapping.json` in `backend/app/ml/models/`.

### 5. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

API runs at `http://127.0.0.1:8000`  
Swagger docs at `http://127.0.0.1:8000/api/v1/docs`

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Create a new account |
| `POST` | `/api/v1/auth/login` | Login and receive JWT |
| `GET` | `/api/v1/auth/me` | Get current user (auth required) |

### Predictions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/predict/` | Classify text (auth required) |
| `GET` | `/api/v1/predict/history` | Get prediction history (auth required) |
| `DELETE` | `/api/v1/predict/history/{id}` | Delete a prediction (auth required) |

#### Example — classify text

```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Scientists discover new clean energy source from seawater."}'
```

```json
{
  "prediction": "newsgroups_sci.med",
  "confidence": 0.847,
  "top_3": [
    { "label": "newsgroups_sci.med", "confidence": 0.847 },
    { "label": "newsgroups_sci.space", "confidence": 0.091 },
    { "label": "newsgroups_sci.crypt", "confidence": 0.031 }
  ],
  "saved": true
}
```

---

## ML Model

| Property | Value |
|---|---|
| Algorithm | TF-IDF + Logistic Regression |
| Training data | IMDB (50k) + 20 Newsgroups (11k) |
| Classes | 22 (2 sentiment + 20 news categories) |
| Validation accuracy | ~89% |
| Vocabulary size | 10,000 features |
| n-gram range | (1, 2) unigrams + bigrams |

Labels follow the format `source_classname` (e.g. `imdb_positive`, `newsgroups_rec.sport.hockey`).

---

## Running Tests

```bash
python -m pytest backend/tests/ -v
```

The test suite uses an isolated in-memory SQLite database — your production `app.db` is never touched.

**Coverage — 24 tests:**

- **Auth:** register (success, duplicate email/username, invalid inputs), login (success, wrong credentials), `/me` (valid token, no token, invalid token)
- **Predict:** classify (success, unauthenticated, text too short/long/empty), history (empty, after prediction, pagination, user isolation), delete (success, not found, another user's record, unauthenticated)

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing key (min 32 chars) | **required** |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` (24h) |
| `DATABASE_URL` | SQLAlchemy connection string | SQLite path |
| `MODEL_PATH` | Path to `.joblib` model file | see config |
| `LABEL_MAPPING_PATH` | Path to `label_mapping.json` | see config |

---

## Known Limitations

- SQLite is used for simplicity — swap `DATABASE_URL` for PostgreSQL in production
- `bcrypt==4.0.1` is required due to a passlib compatibility issue with bcrypt 4.x+
- The ML model loads once at startup (singleton) — a server restart is needed to hot-swap the model

---

## License

MIT
