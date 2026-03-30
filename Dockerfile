# ClearView Backend — FastAPI + LangGraph
# CPU image: requirements.txt pins CUDA/nvidia wheels; those are skipped and PyTorch CPU is installed first.

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

# Minimal build deps for some scientific wheels; ssl for pymongo/appwrite
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install CPU PyTorch first (avoids pulling NVIDIA CUDA stack from requirements.txt)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
        "torch==2.11.0" \
        --index-url https://download.pytorch.org/whl/cpu

# Drop GPU-only / duplicate torch lines from the lockfile, then install the rest
RUN sed -e '/^nvidia-/d' \
        -e '/^triton==/d' \
        -e '/^cuda-/d' \
        -e '/^torch==/d' \
        requirements.txt > requirements.docker.txt \
    && pip install --no-cache-dir -r requirements.docker.txt

COPY app ./app
COPY main.py ./main.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -sf http://127.0.0.1:8000/docs > /dev/null || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
