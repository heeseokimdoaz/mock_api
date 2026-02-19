from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from mock_api.data_store import store

router = APIRouter()


@router.get("/v1/oracleye/doc")
async def get_doc(
    client_id: str = Query(...),
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    site_type: str | None = Query(None),
    search_id: str = Query(...),
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

    results = store.query_docs(from_date, to_date, site_type, offset, size)
    return {"status": "success", "data": results}
