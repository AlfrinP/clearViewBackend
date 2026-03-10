from crewai import Task


def create_extract_information_task(agent, news_text: str) -> Task:
    return Task(
        agent=agent,
        description=(
            "Analyze the provided news article and extract core fact-checkable content.\n\n"
            f"News article:\n{news_text}\n\n"
            "Return JSON with keys:\n"
            "- claims: array of concise factual claims\n"
            "- entities: array of named entities (people, organizations, locations)\n"
            "- keywords: array of high-signal terms\n"
            "- cleaned_text: normalized version of article"
        ),
        expected_output=(
            "Strict JSON object with keys: claims, entities, keywords, cleaned_text. "
            "Do not add markdown."
        ),
    )
