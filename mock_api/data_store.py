import json
from pathlib import Path


class DataStore:
    def __init__(self, docs_path: str, trend_path: str):
        with open(docs_path, encoding="utf-8") as f:
            self.documents: list[dict] = json.load(f)
        with open(trend_path, encoding="utf-8") as f:
            self.trend_data: list[dict] = json.load(f)

    def query_trend(
        self,
        from_date: str,
        to_date: str,
        site_type: str | None = None,
    ) -> list[dict]:
        from_day = from_date[:8]
        to_day = to_date[:8]
        results = []
        for item in self.trend_data:
            if from_day <= item["create_date"] <= to_day:
                if site_type is None or item["site_type"] == site_type:
                    results.append(item)
        return results

    def query_docs(
        self,
        from_date: str,
        to_date: str,
        site_type: str | None = None,
        offset: int = 0,
        size: int = 100,
    ) -> list[dict]:
        results = []
        for doc in self.documents:
            if from_date <= doc["create_date"] <= to_date:
                if site_type is None or doc["site_type"] == site_type:
                    results.append(doc)
        results.sort(key=lambda x: x["create_date"], reverse=True)
        return results[offset : offset + size]


_data_dir = Path(__file__).resolve().parent.parent / "data" / "converted"
store = DataStore(
    str(_data_dir / "all_documents.json"),
    str(_data_dir / "trend_data.json"),
)
