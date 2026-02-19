from typing import Optional

from pydantic import BaseModel


class TrendItem(BaseModel):
    create_date: str
    site_type: str
    doc_count: int


class TrendResponse(BaseModel):
    status: str = "success"
    data: list[TrendItem]


class DocItem(BaseModel):
    create_date: str
    site_type: str
    site_name: str
    title: Optional[str]
    content: str
    url: str
    polarity: str


class DocResponse(BaseModel):
    status: str = "success"
    data: list[DocItem]


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
