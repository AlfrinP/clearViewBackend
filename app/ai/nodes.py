from typing import TypedDict

from pydantic import BaseModel, Field

from app.ai import prompts
from app.ai.model_client import llm
from app.ai.tools import retrieve_context, web_search


class GraphState(TypedDict):
    claim: str
    internal_docs: str
    external_docs: str
    evaluation: dict
    result: dict


class Evaluation(BaseModel):
    verdict: str = Field(description="supported | refuted | insufficient")
    confidence: float = Field(description="0 to 1")
    needs_external_search: bool
    evidence_strength: str = Field(description="weak | moderate | strong")
    reason: str = Field(description="short explanation")


class FinalVerdict(BaseModel):
    final_verdict: str = Field(
        description="True | False | Misleading | Not enough information"
    )
    confidence: float = Field(description="0 to 1")
    justification: str = Field(description="clear reasoning")
    sources_used: list[str] = Field(
        description="sources used, e.g. ['internal', 'external']"
    )


def should_search_more(state: GraphState) -> str:
    result = state.get("evaluation", {})
    if result.get("verdict") == "insufficient":
        return "external"
    if result.get("confidence", 1.0) < 0.65:
        return "external"
    if result.get("evidence_strength") == "weak":
        return "external"
    return "final"


def internal_retrieval(state: GraphState) -> dict:
    docs = retrieve_context.invoke({"query": state["claim"]})
    if isinstance(docs, tuple):
        docs = docs[0]
    return {"internal_docs": docs}


def evaluate(state: GraphState) -> dict:
    structured_llm = llm.with_structured_output(Evaluation)
    response = structured_llm.invoke(
        prompts.evaluation_prompt.format(
            claim=state["claim"], documents=state.get("internal_docs", "")
        )
    )
    return {"evaluation": response.model_dump()}


def external_retrieval(state: GraphState) -> dict:
    docs = web_search.invoke({"query": state["claim"]})
    return {"external_docs": docs}


def final_answer(state: GraphState) -> dict:
    structured_llm = llm.with_structured_output(FinalVerdict)
    response = structured_llm.invoke(
        prompts.final_verdict_prompt.format(
            claim=state["claim"],
            internal_docs=state.get("internal_docs", ""),
            external_docs=state.get("external_docs", ""),
        )
    )
    return {"result": response.model_dump()}

