from crewai import Task


def create_verify_facts_task(agent, evidence_task: Task) -> Task:
    return Task(
        agent=agent,
        context=[evidence_task],
        description=(
            "Evaluate whether internal RAG evidence is sufficient for final classification.\n"
            "Use max_similarity_score as the primary routing metric and justify certainty."
        ),
        expected_output=(
            "Strict JSON object with keys:\n"
            "- rag_sufficient: boolean\n"
            "- similarity_score: number in [0,1]\n"
            "- decision_reasoning: short explanation"
        ),
    )
