from typing import Type

from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.config_setup import LLM


def build_chain(prompt_template: str, schema: Type[BaseModel]):
    """Build a LLM chain with the given prompt template and schema for structured output.

    Args:
        prompt_template (str): The prompt template to use.
        schema (Type[BaseModel]): The Pydantic schema to use for structured output.
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", prompt_template), ("user", "{query}")]
    )
    return prompt | LLM.with_structured_output(schema)
