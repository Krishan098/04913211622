from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime
import re

SHORTCODE_REGEX = re.compile(r"^[a-zA-Z0-9]{4,32}$")

class ShortenRequest(BaseModel):
    url: HttpUrl
    validity: Optional[int] = 30  # minutes
    shortcode: Optional[str] = None

    @field_validator('validity')
    @classmethod
    def validity_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Validity must be a positive integer (minutes)")
        return v

    @field_validator('shortcode')
    @classmethod
    def shortcode_valid(cls, v):
        if v and not SHORTCODE_REGEX.match(v):
            raise ValueError("Shortcode must be alphanumeric and 4-32 chars")
        return v

class ShortenResponse(BaseModel):
    shortlink: str
    expiry: datetime

class ClickInfo(BaseModel):
    timestamp: str
    source: str
    geo: str

class StatsResponse(BaseModel):
    original_url: str
    created_at: datetime
    expiry: datetime
    click_count: int
    clicks: List[ClickInfo]