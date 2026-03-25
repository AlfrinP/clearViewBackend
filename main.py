from langgraph.graph import StateGraph, END
from nodes import internal_retrieval, evaluate, external_retrieval, final_answer
from nodes import should_search_more, GraphState

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

app = graph.compile()

if __name__ == "__main__":
    print("Welcome to the Fake News Detector CLI!")
    print("Type 'exit' or 'quit' to exit.")
    
    while True:
        try:
            claim = input("\nEnter a claim to verify: ").strip()
            if claim.lower() in ['exit', 'quit']:
                break
            if not claim:
                continue
                
            print(f"\nProcessing claim: '{claim}'...\n")
            
            # Start the graph execution
            # Pass the initial state
            initial_state = {
                "claim": claim, 
                "internal_docs": "", 
                "external_docs": "", 
                "evaluation": {}, 
                "result": {}
            }
            final_state = app.invoke(initial_state)
            
            result = final_state.get("result", {})
            print("="*50)
            print(f"VERDICT: {result.get('final_verdict', 'N/A')}")
            print(f"CONFIDENCE: {result.get('confidence', 'N/A')}")
            print(f"JUSTIFICATION: {result.get('justification', 'N/A')}")
            print(f"SOURCES USED: {', '.join(result.get('sources_used', []))}")
            print("="*50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
