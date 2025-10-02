from typing import List, Optional, TypedDict


class InputState(TypedDict):
    """Represents the initial input state for processing a query."""

    client_id: int
    query: str


class ParamState(TypedDict):
    """Represents a parameter for a parameterized SQL query."""

    name: str
    value: str


class SQLTranslatorState(TypedDict):
    """Represents the state after translating a query into SQL."""

    query: str
    sql_query: Optional[str]
    params: Optional[List[ParamState]]
    error_message: Optional[str]
    fallback_count: Optional[int]


class SQLExecutorState(TypedDict):
    """Represents the state after executing a SQL query."""

    query: str
    result: Optional[List[dict]]
    error_message: Optional[str]
    fallback_count: Optional[int]


class OutputState(TypedDict):
    """Represents the final output state after processing the query."""

    response: str


class OverallState(InputState, SQLTranslatorState, SQLExecutorState, OutputState):
    """Represents the complete state throughout the query processing lifecycle."""

    pass
