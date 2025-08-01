from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

# Import services
from app.core.query import query_documentation

# Create router
router = APIRouter()

# Define request and response models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

# Query endpoint
@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    """
    Query the API documentation with a natural language question.
    
    Returns an answer generated from the most relevant documentation chunks.
    """
    try:
        result = query_documentation(request.query, request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))