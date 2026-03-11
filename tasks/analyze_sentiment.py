from crewai import Task


def create_web_search_task(agent, news_text: str, verification_task: Task) -> Task:
    return Task(
        agent=agent,
        context=[verification_task],
        description=(
            "When rag_sufficient is false, use Tavily web search to gather "
            "external evidence.\n"
            "Use extracted claims or keywords from prior tasks to form "
            "precise search queries.\n"
            "Prioritize trusted sources (WHO, CDC, Reuters, AP, government "
            "or academic domains).\n"
            "Limit output size: maximum 3 sources and each source content "
            "must be at most 400 characters.\n\n"
            f"News article:\n{news_text}\n\n"
            "Use the tavily_web_search_tool and return only structured JSON."
        ),
        expected_output=(
            "Strict JSON object with keys:\n"
            "- web_sources: array of {title, content, url}\n"
            "- evidence_summaries: array of short summaries showing support "
            "or contradiction\n"
            "- skipped: boolean"
        ),
    )
