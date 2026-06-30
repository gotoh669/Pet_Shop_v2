from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.bootstrap import init_database
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.response import success
from app.routers import api_router


app = FastAPI(title=settings.app_name)

allow_origins = (
    ["*"]
    if settings.cors_allow_origins == "*"
    else [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        init_database()


@app.get("/health")
def health() -> dict:
    return success({"status": "ok", "project": "Pet_Shop_v2"})
