# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        poppler-utils \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md
COPY knowledge ./knowledge
COPY src ./src
COPY run_agent.py ./run_agent.py
COPY tests/sample_pdfs ./tests/sample_pdfs

RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data /app/output

# ENTRYPOINT ["python", "run_agent.py", "--doc", "tests/sample_pdfs/NASDAQ_TSLA_2024.pdf", ]
# ENTRYPOINT ["python", "run_agent.py", "--doc", "tests/sample_pdfs/Small-Foundation-Annual-Report-2019.pdf", ]

