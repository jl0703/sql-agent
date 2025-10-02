from typing import List, Optional

from pydantic import BaseModel, Field


class Param(BaseModel):
    """Param schema for binding in parameterized SQL query."""

    name: str = Field(description="Parameter name to bind in SQL query")
    value: str = Field(description="Parameter value as string")


class SQLTranslator(BaseModel):
    """Response schema for translating user query into parameterized SQL query."""

    sql_query: Optional[str] = Field(
        description="Parameterized SQL query with placeholders."
    )
    params: Optional[List[Param]] = Field(
        description="List of parameters to bind to the query.",
        default_factory=list,
    )
    error_message: Optional[str] = Field(
        None, description="Message to the user if the query cannot be answered."
    )


class Generator(BaseModel):
    """Response schema for generating output based on context and user query."""

    response: str = Field(
        description="Generated response based on the context and user query."
    )
