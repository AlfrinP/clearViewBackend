# ClearView: Fake News Detection Backend

An agentic AI pipeline built using [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://python.langchain.com/) for fact-checking and verifying claims. This backend cross-checks claims against an internal document database using MongoDB Atlas Vector Search and dynamically falls back to querying the open web via Tavily Search when the internal evidence is insufficient or weak.

## 🚀 Key Features

*   **Internal Knowledge Base Retrieval (RAG)**: Leverages HuggingFace embeddings (`sentence-transformers/all-mpnet-base-v2`) and MongoDB Atlas Vector Search to query your proprietary or local documents.
*   **Agentic Routing**: Uses a stateful graph architecture (`StateGraph`) to intelligently assess evidence and dynamically decide if a claim requires external corroboration.
*   **External Web Search Fallback**: Automatically searches the web (using Tavily Search API) if internal evidence is deemed weak, conflicting, or non-existent.
*   **Structured LLM Output**: Uses Groq's high-speed inference models (default: `llama3-70b-8192`) and strictly enforces structured JSON output via Pydantic for deterministic and robust verifications.

## 🛠️ Project Architecture

1.  **Incoming Claim**: A string claim is inputted to the graph via `main.py`.
2.  **Internal Retrieval**: Semantically queries MongoDB for relevant internal documents.
3.  **Evaluation Node**: A Groq-powered evaluation prompt determines if the claim is `[supported | refuted | insufficient]` based *only* on the internal data.
4.  **Conditional Edge (`decide`)**: If the evidence is weak, conflicting, or missing, the graph routes the query to the web. Otherwise, it proceeds to make a final decision.
5.  **External Search**: Queries the open web for up-to-date facts using Tavily.
6.  **Final Verdict Node**: Synthesizes all gathered evidence and outputs a final JSON structure containing the classification (`True | False | Misleading | Not enough information`), a confidence score, and clear justifications.

## ⚙️ Installation & Setup

1.  **Clone the Repository** and open it in your terminal.
2.  **Activate your virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  **Install Dependencies** (Ensure you have `langchain`, `langgraph`, `pymongo`, `langchain-groq`, `langchain-mongodb`, `langchain-huggingface`, `langchain-tavily`, and `sentence-transformers` installed).
4.  **Set up Environment Variables**: Create a `.env` file in the root directory and add the following keys securely (Do NOT commit this to Git!):

    ```env
    # API Keys
    HUGGINGFACEHUB_API_TOKEN="hf_..."
    GROQ_API_KEY="gsk_..."
    TAVILY_API_KEY="tvly-..."

    # MongoDB Atlas Config
    MONGO_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net"
    MONGO_DB_NAME="fake_news_db"
    MONGODB_COLLECTION="documents"
    ATLAS_VECTOR_SEARCH_INDEX_NAME="vector_index"
    
    # Optional LLM Configs
    LLM_MODEL="llama3-70b-8192"
    MODEL_TEMPERATURE="0.7"
    ```

## 🎮 Usage

You can launch the interactive Command Line Interface locally to test claims against your pipeline:

```bash
python main.py
```

### Example Interaction:
```text
Welcome to the Fake News Detector CLI!
Type 'exit' or 'quit' to exit.

Enter a claim to verify: The speed of light is 299,792,458 meters per second.

Processing claim: 'The speed of light is 299,792,458 meters per second.'...

==================================================
VERDICT: True
CONFIDENCE: 1.0
JUSTIFICATION: Both internal and external documents confirm the speed of light in a vacuum is exactly 299,792,458 m/s.
SOURCES USED: internal, external
==================================================
```
