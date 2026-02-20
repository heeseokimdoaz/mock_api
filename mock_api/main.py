from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mock_api.routers import trend, doc, newspaper

app = FastAPI(title="TapaCross Mock API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trend.router)
app.include_router(doc.router)
app.include_router(newspaper.router)
