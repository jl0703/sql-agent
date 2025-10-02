from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Schema for a query request."""

    client_id: str
    query: str
    
class QueryResponse(BaseModel):
    """Schema for a query response."""

    response: str
