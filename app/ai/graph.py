from langgraph.graph import END, StateGraph

from app.ai.nodes import (
    GraphState,
    evaluate,
    external_retrieval,
    final_answer,
    internal_retrieval,
    should_search_more,
)

graph = StateGraph(GraphState)

graph.add_node("internal", internal_retrieval)
graph.add_node("evaluate", evaluate)
graph.add_node("external", external_retrieval)
graph.add_node("final", final_answer)

graph.set_entry_point("internal")
graph.add_edge("internal", "evaluate")
graph.add_conditional_edges(
    "evaluate", should_search_more, {"external": "external", "final": "final"}
)
graph.add_edge("external", "final")
graph.add_edge("final", END)

verification_graph = graph.compile()

