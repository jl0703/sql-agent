from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.agent.orchestrator import AgentOrchestrator
from app.dependencies import get_db
from app.schemas.model import QueryRequest, QueryResponse

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post("/query", status_code=status.HTTP_200_OK)
async def query_agent(request: QueryRequest, conn=Depends(get_db)) -> QueryResponse:
    """Query the agent about transactions.

    Args:
        request (QueryRequest): The query request object.
        orchestrator (AgentOrchestrator, optional): The agent orchestrator instance. Defaults to Depends(get_orchestrator).

    Returns:
        QueryResponse: The query response object.
    """
    try:
        orchestrator = AgentOrchestrator(conn)
        graph = orchestrator.build_graph()
        res = await graph.ainvoke(
            {"client_id": request.client_id, "query": request.query}
        )

        return QueryResponse(response=res["response"])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
