# AI Text Classification Web App

A full-stack web application for classifying text into 22 categories using machine learning. Built with **FastAPI** + **React**, using a TF-IDF + Logistic Regression pipeline trained on IMDB and 20 Newsgroups datasets.

> **The ML model is pre-trained and included in the repository** — no training step required.

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
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       ├── database/
│       │   ├── app.db                   # SQLite database (auto-created)
│       │   └── database.py              # SQLAlchemy engine & session
│       ├── ml/
│       │   ├── artifacts/
│       │   │   ├── combined_dataset.csv # Merged training data
│       │   │   ├── eda_distribution.png # Distribution plots
│       │   │   └── label_mapping.csv    # Label encoder output
│       │   ├── data/
│       │   │   └── IMDB Dataset.csv     # Raw IMDB data
│       │   ├── models/
│       │   │   ├── text_classifier.joblib   # ✅ Pre-trained model
│       │   │   ├── label_mapping.json       # ✅ Class label mapping
│       │   │   └── training_metrics.json    # Accuracy & CV scores
│       │   └── src/
│       │       ├── preprocess.py        # Data loading & cleaning
│       │       ├── train.py             # Model training pipeline
│       │       └── predict.py           # Inference service (singleton)
│       ├── models/
│       │   └── user_model.py            # SQLAlchemy ORM models
│       ├── routes/
│       │   ├── auth_routes.py           # /auth endpoints
│       │   └── predict_routes.py        # /predict endpoints
│       ├── schemas/
│       │   └── user_schema.py           # Pydantic request/response schemas
│       ├── services/
│       │   ├── auth_service.py          # Register, login, user lookup
│       │   └── predict_service.py       # Prediction + history CRUD
│       ├── utils/
│       │   └── security.py              # JWT creation & verification
│       ├── config.py                    # Pydantic settings (reads .env)
│       └── main.py                      # FastAPI app entry point
├── frontend/
│   └── src/
│       ├── components/                  # Layout, ProtectedRoute, UI primitives
│       ├── pages/
│       │   ├── Home.jsx
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   ├── Dashboard.jsx
│       │   ├── History.jsx
│       │   └── Profile.jsx
│       ├── services/
│       │   └── api.js                   # Axios instance + API methods
│       ├── store/
│       │   └── authStore.js             # Zustand auth state
│       ├── App.jsx
│       └── main.jsx
├── .env                                 # Local environment variables (never commit)
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Clone the repository

```bash
git clone https://github.com/Rafeh-18/AI-Text-Classification-Web-App.git
cd AI-Text-Classification-Web-App
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `bcrypt==4.0.1` is pinned in requirements.txt due to a compatibility issue between passlib and bcrypt 4.x+.

### 4. Create `.env` file

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./backend/app/database/app.db
MODEL_PATH=backend/app/ml/models/text_classifier.joblib
LABEL_MAPPING_PATH=backend/app/ml/models/label_mapping.json
```

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/api/v1/docs`

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: `http://localhost:5173`

---

## API Reference

All protected endpoints require an `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | ❌ | Create a new account |
| `POST` | `/api/v1/auth/login` | ❌ | Login and receive JWT |
| `GET` | `/api/v1/auth/me` | ✅ | Get current user info |

### Predictions

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/predict/` | ✅ | Classify text |
| `GET` | `/api/v1/predict/history` | ✅ | Get prediction history |
| `DELETE` | `/api/v1/predict/history/{id}` | ✅ | Delete a prediction |

#### Example — classify text

```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Scientists discover new clean energy source from seawater."}'
```

**Response:**
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

The pre-trained model is included at `backend/app/ml/models/text_classifier.joblib` and loads automatically on server start.

| Property | Value |
|---|---|
| Algorithm | TF-IDF + Logistic Regression |
| Training data | IMDB (50k reviews) + 20 Newsgroups (11k articles) |
| Total classes | 22 (2 sentiment + 20 news categories) |
| Validation accuracy | ~89% |
| Vocabulary size | 10,000 features |
| n-gram range | (1, 2) — unigrams + bigrams |

### Class Labels

Labels follow the format `source_classname`:

| Source | Labels |
|---|---|
| IMDB | `imdb_positive`, `imdb_negative` |
| 20 Newsgroups | `newsgroups_rec.sport.hockey`, `newsgroups_sci.space`, `newsgroups_talk.politics.misc`, and 17 more |

### Retraining (optional)

If you want to retrain the model from scratch:

```bash
# Step 1 — preprocess (requires IMDB Dataset.csv in backend/app/ml/data/)
python -m backend.app.ml.src.preprocess

# Step 2 — train
python -m backend.app.ml.src.train
```

---

## Running Tests

```bash
python -m pytest backend/tests/ -v
```

Tests run against an isolated SQLite database — production `app.db` is never touched.

**24 tests across 2 files:**

| File | What's tested |
|---|---|
| `test_auth.py` | Register (success, duplicate email/username, invalid inputs), Login (success, wrong credentials), `/me` (valid, no token, invalid token) |
| `test_predict.py` | Classify (success, unauthenticated, text too short/long/empty), History (empty, after prediction, pagination, user isolation), Delete (success, not found, another user's record, unauthenticated) |

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | JWT signing key (min 32 chars) | ✅ |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes | `1440` |
| `DATABASE_URL` | SQLAlchemy DB connection string | SQLite default |
| `MODEL_PATH` | Path to `.joblib` model file | see config.py |
| `LABEL_MAPPING_PATH` | Path to `label_mapping.json` | see config.py |

---

## Known Limitations

- **SQLite** is used for simplicity — replace `DATABASE_URL` with a PostgreSQL URI for production
- **bcrypt 4.0.1** is pinned — newer versions break passlib's version detection
- **Model hot-swap** is not supported — a server restart is required to load a newly trained model
- **CORS** is configured for `localhost` only — update `allow_origins` in `main.py` before deploying

---

## License

MIT
