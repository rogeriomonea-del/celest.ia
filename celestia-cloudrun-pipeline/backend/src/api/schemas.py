from pydantic import BaseModel

class SearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str  # YYYY-MM-DD
    program: str | None = None  # e.g., LATAM, Azul, Smiles
