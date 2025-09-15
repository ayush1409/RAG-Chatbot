
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocIn(BaseModel):
    id: str = Field(..., description="Unique ID for the document (used for provenance)")
    title: Optional[str] = None
    text: str = Field(..., min_length=1)

class IngestRequest(BaseModel):
    docs: List[DocIn]

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(4, description="How many context chunks to retrieve")

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]