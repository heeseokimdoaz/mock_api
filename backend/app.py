from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.api_client import TapaCrossClient

app = FastAPI(title="TapaCross Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = TapaCrossClient()


@app.get("/api/trend")
async def trend(
    from_date: str = Query("20260208000000"),
    to_date: str = Query("20260212235959"),
    site_type: str | None = Query(None),
):
    return await client.get_trend(from_date, to_date, site_type)


@app.get("/api/documents")
async def documents(
    from_date: str = Query("20260208000000"),
    to_date: str = Query("20260212235959"),
    site_type: str | None = Query(None),
    offset: int = Query(0),
    size: int = Query(20),
):
    return await client.get_documents(from_date, to_date, site_type, offset, size)


@app.get("/api/newspapers")
async def newspapers(
    from_date: str = Query("20260208000000"),
    to_date: str = Query("20260212235959"),
    region: str | None = Query(None),
    site_name: str | None = Query(None),
    offset: int = Query(0),
    size: int = Query(20),
):
    return await client.get_newspapers(
        from_date, to_date, region, site_name, offset, size
    )


frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
