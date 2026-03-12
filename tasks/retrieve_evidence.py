from crewai import Task


def create_retrieve_evidence_task(agent, news_text: str, extraction_task: Task) -> Task:
    return Task(
        agent=agent,
        context=[extraction_task],
        description=(
            "Use the extracted claims to retrieve supporting or contradicting passages from the "
            "internal vector database tool.\n"
            "Do retrieval only; do not classify the claim.\n"
            "Use only the extracted claims/keywords from context (do not repeat full article).\n"
            "For each claim, include top evidence and assign a similarity score in [0,1].\n"
            "Limit to top 2 evidence items. Keep each passage <=300 chars."
        ),
        expected_output=(
            "Strict JSON object with keys:\n"
            "- rag_evidence: array of {claim, passage, source, similarity_score}\n"
            "- max_similarity_score: number in [0,1]\n"
            "- retrieval_summary: short text (<=40 words)"
        ),
    )
