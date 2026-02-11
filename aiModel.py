from langchain.tools import tool
from langchain.agents import create_agent
from models import llm
from rag.vectorDb import vector_store


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve verified government rules and regulations related to vehicle modifications in Kerala."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [retrieve_context]
# If desired, specify custom instructions
prompt = (
    "You are a fake news detection assistant focused on vehicle modification laws in Kerala, India. "
    "Use the retrieval tool to verify claims using official government rules, MVD notifications, "
    "and legal documents. Clearly state whether a claim is true, false, or misleading, "
    "and explain why using retrieved evidence."
)

agent = create_agent(llm, tools, system_prompt=prompt)


# query = (
#     "A viral message claims that aftermarket LED headlights, underbody neon lights, "
#     "and modified exhausts are now fully legal in Kerala without any approval from MVD.\n\n"
#     "Verify whether this claim is true or fake using official vehicle modification rules. "
#     "Provide a clear verdict and justification."
# )


# for event in agent.stream(
#     {"messages": [{"role": "user", "content": query}]},
#     stream_mode="values",
# ):
#     event["messages"][-1].pretty_print()
