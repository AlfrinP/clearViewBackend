import json
from models import llm
import prompt
from tools import retrieve_context, web_search


def should_search_more(result):
    if result["verdict"] == "insufficient":
        return True

    if result["confidence"] < 0.65:
        return True

    if result["evidence_strength"] == "weak":
        return True

    return False


def internal_retrieval(state):
    docs = retrieve_context(state["claim"])
    return {"internal_docs": docs}


def evaluate(state):
    response = llm.invoke(
        prompt.evaluation_prompt.format(
            claim=state["claim"], documents=state["internal_docs"]
        )
    )
    parsed_json = json.loads(response.content)
    return {"evaluation": parsed_json}


def decide(state):
    if should_search_more(state["evaluation"]):
        return "external_search"
    return "final"


def external_retrieval(state):
    docs = web_search(state["claim"])
    return {"external_docs": docs}


def final_answer(state):
    response = llm.invoke(
        prompt.final_verdict_prompt.format(
            claim=state["claim"],
            internal_docs=state["internal_docs"],
            external_docs=state["external_docs"],
        )
    )
    return {"result": response}
