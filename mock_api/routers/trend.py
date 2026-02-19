from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from mock_api.data_store import store

router = APIRouter()


@router.get("/v1/oracleye/trend")
async def get_trend(
    client_id: str = Query(...),
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    site_type: str | None = Query(None),
    search_id: str = Query(...),
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

    results = store.query_trend(from_date, to_date, site_type)
    return {"status": "success", "data": results}
