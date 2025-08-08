from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    departure_date: str  # YYYY-MM-DD
    program: str | None = None
    cabin: str | None = None  # economy, business
