from crewai import Task


def create_extract_information_task(agent, news_text: str) -> Task:
    return Task(
        agent=agent,
        description=(
            "Analyze the provided news article and extract core fact-checkable content.\n\n"
            f"News article:\n{news_text}\n\n"
            "Do not repeat the full article in your output.\n"
            "Return at most 3 claims and keep each claim concise (<=160 chars).\n"
            "Return JSON with keys:\n"
            "- claims: array of concise factual claims\n"
            "- entities: array of named entities (people, organizations, locations)\n"
            "- keywords: array of high-signal terms"
        ),
        expected_output=(
            "Strict JSON object with keys: claims, entities, keywords. "
            "Do not add markdown."
        ),
    )
