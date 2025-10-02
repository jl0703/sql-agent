import re
from typing import Literal

from langgraph.graph import END, START, StateGraph
from psycopg import AsyncConnection, ProgrammingError

from app.agent.schemas.model import Generator, SQLTranslator
from app.agent.schemas.state import (
    InputState,
    OutputState,
    OverallState,
    SQLExecutorState,
    SQLTranslatorState,
)
from app.agent.templates import generator_template, sql_translator_template
from app.agent.utils import build_chain


class AgentOrchestrator:
    """
    Orchestrates the AI workflow that translates user queries into parameterized SQL query,
    executes the SQL against a PostgreSQL database and generates a response.
    """

    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def sql_translator(self, state: InputState) -> SQLTranslatorState:
        """Translate the user query into a parameterized SQL query.

        Args:
            state (InputState): The input state containing the user id and user query.

        Returns:
            SQLTranslatorState: The SQL translator state containing the translated query and parameters.
        """
        try:
            formatted_prompt = build_chain(sql_translator_template(), SQLTranslator)
            response = await formatted_prompt.ainvoke(
                {
                    "client_id": state["client_id"],
                    "query": state["query"],
                    "error_message": "",
                }
            )

            return {
                "query": state["query"],
                "sql_query": response.sql_query if response.sql_query else None,
                "params": (
                    [
                        {"name": param.name, "value": param.value}
                        for param in response.params
                    ]
                    if response.params
                    else None
                ),
                "error_message": (
                    response.error_message if response.error_message else None
                ),
            }
        except Exception as e:
            raise Exception(f"Error in sql_translator: {str(e)}")

    async def sql_executor(self, state: SQLTranslatorState) -> SQLExecutorState:
        """Execute the parameterized SQL query and return the results.

        Args:
            state (SQLTranslatorState): The SQL translator state containing the translated query and parameters.

        Returns:
            SQLExecutorState: The SQL executor state containing the query results.
        """
        try:
            if state["sql_query"] is None:
                return {
                    "query": state["query"],
                    "result": None,
                    "error_message": state["error_message"] or "No SQL query to execute.",
                }

            sql_query = state["sql_query"].replace("?", "%s")
            sql_query = re.sub(r":\w+", "%s", sql_query)
            
            values = (
                [param["value"] for param in state["params"]]
                if state.get("params")
                else []
            )

            try:
                async with self.conn.cursor() as cur:
                    await cur.execute(sql_query, values)
                    rows = await cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    result = [dict(zip(columns, row)) for row in rows]

                return {
                    "query": state["query"],
                    "result": result,
                    "error_message": None,
                }
            except ProgrammingError as e:
                return {
                    "query": state["query"],
                    "result": None,
                    "error_message": (
                        f"SQL Execution Error: {state['sql_query']} "
                        f"Params: {state.get('params')} "
                        f"Error: {str(e)}"
                    ),
                    "fallback_count": state.get("fallback_count", 0) + 1,
                }
                
        except Exception as e:
            raise Exception(f"Error in sql_executor: {str(e)}")

    async def generator(self, state: SQLExecutorState) -> OutputState:
        """Generate human-readable response based on the SQL query results.

        Args:
            state (SQLExecutorState): The SQL executor state containing the query results.

        Returns:
            OutputState: The output state containing the response.
        """
        try:
            if state["error_message"] is not None:
                return {
                    "response": state["error_message"],
                }

            formatted_prompt = build_chain(generator_template(), Generator)
            res = await formatted_prompt.ainvoke(
                {
                    "context": state["result"] or "No data found.",
                    "query": state["query"],
                }
            )

            return {"response": res.response}
        except Exception as e:
            raise Exception(f"Error in generator: {str(e)}")

    def route_after_sql_translator(
        self, 
        state: SQLTranslatorState
    ) -> Literal["sql_executor", "generator"]:
        """Determine the next step after SQL translation.

        Args:
            state (SQLTranslatorState): The current state after SQL translation.

        Returns:
            Literal["sql_executor", "generator"]: The next step to take.
        """
        if state.get("result") is not None:
            return "generator"
        
        if state.get("fallback_count", 0) <= 3:
            return "sql_executor"
        
        return "generator"

    def route_after_sql_executor(
        self, 
        state: SQLExecutorState
    ) -> Literal["sql_translator", "generator"]:
        """Determine the next step after SQL execution.
        
        Args:
            state (SQLExecutorState): The current state after SQL execution.
        
        Returns:
            Literal["sql_translator", "generator"]: The next step to take. 
        """
        err = state.get("error_message") or ""
        
        if "SQL Execution Error:" in err and state.get("fallback_count", 0) < 3:
            return "sql_translator"
        
        return "generator"

    def build_graph(self) -> StateGraph:
        """Build the graph representing the agent workflow.

        Returns:
            StateGraph: The compiled state graph representing the agent workflow.
        """
        graph = StateGraph(
            OverallState, input_schema=InputState, output_schema=OutputState
        )
        graph.add_node("sql_translator", self.sql_translator)
        graph.add_node("sql_executor", self.sql_executor)
        graph.add_node("generator", self.generator)

        graph.add_edge(START, "sql_translator")
        graph.add_conditional_edges("sql_translator", self.route_after_sql_translator)
        graph.add_conditional_edges("sql_executor", self.route_after_sql_executor)
        graph.add_edge("generator", END)

        return graph.compile()
