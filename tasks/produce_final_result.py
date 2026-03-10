from crewai import Task


def create_produce_final_result_task(agent, task_context: list[Task]) -> Task:
    return Task(
        agent=agent,
        context=task_context,
        description=(
            "Produce the final fake-news verdict using available evidence.\n"
            "Classifications allowed: Real, Fake, Uncertain.\n"
            "Confidence must be between 0 and 1 and reflect evidence quality."
        ),
        expected_output=(
            "Strict JSON object with keys:\n"
            "- classification: one of Real|Fake|Uncertain\n"
            "- confidence: number in [0,1]\n"
            "- reasoning: concise explanation\n"
            "- rag_evidence: array\n"
            "- web_sources: array"
        ),
    )
