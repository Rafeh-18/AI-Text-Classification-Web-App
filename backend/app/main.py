from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database.database import engine, Base
from backend.app.routes import auth_routes, predict_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Fixed: allow_origins can't be ["*"] when allow_credentials=True — browsers will block it
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        # Add your production frontend URL here, e.g. "https://your-frontend.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix=settings.API_V1_STR)
app.include_router(predict_routes.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "AI Text Classification API", "docs": f"{settings.API_V1_STR}/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}