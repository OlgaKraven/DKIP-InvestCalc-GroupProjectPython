from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.routes_example import router as example_router

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app = FastAPI(title="API Skeleton")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(example_router, prefix="/api/v1", tags=["example"])


@app.get("/")
def root():
    return {
        "message": "API Skeleton работает. Откройте /docs для Swagger UI.",
        "docs_url": "/docs",
        "health_url": "/health",
        "items_url": "/api/v1/items",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
