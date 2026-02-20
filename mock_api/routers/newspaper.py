from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from mock_api.data_store import store

router = APIRouter()


@router.get("/v1/oracleye/newspaper")
async def get_newspaper(
    client_id: str = Query(...),
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    search_id: str = Query(...),
    region: str | None = Query(None),
    site_name: str | None = Query(None),
    offset: int = Query(0),
    size: int = Query(100),
):
    if len(from_date) != 14 or not from_date.isdigit():
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "잘못된 날짜 형식입니다. (yyyyMMddHHmmss)",
            },
        )
    if len(to_date) != 14 or not to_date.isdigit():
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "잘못된 날짜 형식입니다. (yyyyMMddHHmmss)",
            },
        )

    results = store.query_newspapers(
        from_date, to_date, region, site_name, offset, size
    )
    return {"status": "success", "data": results}
