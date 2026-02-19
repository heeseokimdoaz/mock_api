import httpx

from backend.config import API_BASE_URL, CLIENT_ID, SEARCH_ID


class TapaCrossClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.client_id = CLIENT_ID
        self.search_id = SEARCH_ID

    async def get_trend(
        self,
        from_date: str,
        to_date: str,
        site_type: str | None = None,
    ) -> dict:
        params = {
            "client_id": self.client_id,
            "from": from_date,
            "to": to_date,
            "search_id": self.search_id,
        }
        if site_type:
            params["site_type"] = site_type
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v1/oracleye/trend", params=params
            )
            return resp.json()

    async def get_documents(
        self,
        from_date: str,
        to_date: str,
        site_type: str | None = None,
        offset: int = 0,
        size: int = 100,
    ) -> dict:
        params = {
            "client_id": self.client_id,
            "from": from_date,
            "to": to_date,
            "search_id": self.search_id,
            "offset": offset,
            "size": size,
        }
        if site_type:
            params["site_type"] = site_type
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v1/oracleye/doc", params=params
            )
            return resp.json()
