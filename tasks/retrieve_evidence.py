from crewai import Task


def create_retrieve_evidence_task(agent, news_text: str, extraction_task: Task) -> Task:
    return Task(
        agent=agent,
        context=[extraction_task],
        description=(
            "Use the extracted claims to retrieve supporting or contradicting passages from the "
            "internal vector database tool.\n\n"
            f"Original news article:\n{news_text}\n\n"
            "For each claim, include the top evidence and assign a similarity score between 0 and 1."
        ),
        expected_output=(
            "Strict JSON object with keys:\n"
            "- rag_evidence: array of {claim, passage, source, similarity_score}\n"
            "- max_similarity_score: number in [0,1]\n"
            "- retrieval_summary: short text"
        ),
    )
