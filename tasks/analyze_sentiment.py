from crewai import Task


def create_web_search_task(agent, news_text: str, verification_task: Task) -> Task:
    return Task(
        agent=agent,
        context=[verification_task],
        description=(
            "Only if rag_sufficient is false, perform web search to gather external evidence.\n"
            "Prioritize trusted sources (WHO, CDC, Reuters, AP, government or academic domains).\n\n"
            f"News article:\n{news_text}"
        ),
        expected_output=(
            "Strict JSON object with keys:\n"
            "- web_sources: array of {title, url, snippet, credibility_note}\n"
            "- web_search_summary: short text\n"
            "- skipped: boolean (true if rag_sufficient was true)"
        ),
    )
