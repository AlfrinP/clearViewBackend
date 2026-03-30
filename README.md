# ClearView: Fake News Detection Backend

An agentic AI pipeline built using [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://python.langchain.com/) for fact-checking and verifying claims. This backend cross-checks claims against an internal document database using MongoDB Atlas Vector Search and dynamically falls back to querying the open web via Tavily Search when the internal evidence is insufficient or weak.

## 🚀 Key Features

- **Internal Knowledge Base Retrieval (RAG)**: Leverages HuggingFace embeddings (`sentence-transformers/all-mpnet-base-v2`) and MongoDB Atlas Vector Search to query your proprietary or local documents.
- **Agentic Routing**: Uses a stateful graph architecture (`StateGraph`) to intelligently assess evidence and dynamically decide if a claim requires external corroboration.
- **External Web Search Fallback**: Automatically searches the web (using Tavily Search API) if internal evidence is deemed weak, conflicting, or non-existent.
- **Structured LLM Output**: Uses Groq's high-speed inference models (default: `llama3-70b-8192`) and strictly enforces structured JSON output via Pydantic for deterministic and robust verifications.

## 🛠️ Project Architecture

1.  **Incoming Claim**: A claim is received via the FastAPI endpoint (`POST /api/v1/verify-news`).
2.  **Internal Retrieval**: Semantically queries MongoDB for relevant internal documents.
3.  **Evaluation Node**: A Groq-powered evaluation prompt determines if the claim is `[supported | refuted | insufficient]` based _only_ on the internal data.
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
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up Environment Variables**: Copy the provided example file and update it with your actual credentials:

    ```bash
    cp .env.example .env
    ```

## 🐋 Docker

The image installs **CPU PyTorch** and strips CUDA/NVIDIA-only pins from `requirements.txt` so the build stays portable.

```bash
docker build -t clearview-backend .

docker run --rm -p 8000:8000 --env-file .env clearview-backend
```

Then open `http://localhost:8000/docs`.

### Docker Compose

Starts the API and a **MongoDB 7** container for local development (default `MONGO_URI=mongodb://mongo:27017`).

```bash
docker compose up --build
```

If you use **MongoDB Atlas** (or any external MongoDB), start only the API and set `MONGO_URI` in `.env`:

```bash
docker compose up --build --no-deps api
```

Then open `http://localhost:8000/docs`.

## 🎮 Usage

Start the API server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Endpoint: `POST /api/v1/verify-news`

#### Request

```json
{
  "claim": "The speed of light is 299,792,458 meters per second."
}
```

#### Response (example)

```json
{
  "claim": "The speed of light is 299,792,458 meters per second.",
  "evaluation": {
    "verdict": "supported",
    "confidence": 1.0,
    "needs_external_search": false,
    "evidence_strength": "strong",
    "reason": "Internal evidence directly supports the claim."
  },
  "result": {
    "final_verdict": "True",
    "confidence": 1.0,
    "justification": "Both internal and external documents confirm the speed of light in a vacuum is exactly 299,792,458 m/s.",
    "sources_used": ["internal", "external"]
  }
}
```

#### cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/verify-news" \
  -H "Content-Type: application/json" \
  -d '{"claim":"The speed of light is 299,792,458 meters per second."}'
```

### File Endpoints

- `POST /api/v1/upload-file` (multipart: `file`, `file_title`)
- `GET /api/v1/files?page=1&limit=10`
- `DELETE /api/v1/files/{file_id}`
