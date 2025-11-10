# DocAnalizer Crew

DocAnalizer is a multi-agent financial document analysis system built on top of [CrewAI](https://crewai.com). It ingests unstructured or semi-structured financial PDFs, extracts structured data (tables, key/value pairs, narratives), computes metrics and scenarios, and synthesizes a stakeholder-ready Markdown report with strict formatting. The design emphasizes reproducibility, provenance, and modular extensibility (LLM providers, tools, output contracts).

## Why This Project?
Financial teams spend significant time manually:
- Extracting data from diverse filings and reports
- Normalizing metrics, calculating ratios, stress-testing scenarios
- Producing decision-grade summaries quickly for stakeholders

DocAnalizer automates this end-to-end pipeline using specialized agents:
1. Extraction (lossless structured JSON with provenance)
2. Analysis (metrics, risks, scenarios, recommendations)
3. Report Generation (structured Markdown with traceable formulas)

This reduces manual effort, improves consistency, and creates a foundation for auditability and downstream integrations.

## Core Features
- Multi-agent architecture (Extractor, Analyst, Report Writer)
- Strict output contracts (JSON schemas & Markdown section ordering)
- Provenance tracking (page + locator for every sourced metric)
- Scenario analysis (base / downside / upside numeric deltas)
- Extensible tools (LandingAI ADE integration, calculator, optional Pushover notifier)
- Pluggable LLM backends (OpenRouter, Groq, OpenAI, Gemini experimentation)
- Safe computation via a sandboxed calculator tool (formulas & financial math)
- Configuration-driven prompts (`agents.yaml`, `tasks.yaml`)

## Tech Stack
- Python 3.10+
- CrewAI (agent/task orchestration)
- LiteLLM (provider abstraction)
- OpenRouter / Groq (LLM endpoints) – configurable per agent
- LandingAI ADE (document extraction)
- Pydantic (tool input validation)
- Requests (HTTP integrations)
- UV (dependency + environment management)

Optional integrations (currently disabled by default in report stage):
- Pushover push notifications

## High-Level Architecture
```
PDFs -> Extraction Agent (LandingAI tool) -> Structured JSON -> Analyst Agent -> Metrics/Risks/Scenarios JSON -> Report Generator -> Markdown Report
```

### Agents
- `document_extractor`: Parses documents into structured JSON with provenance.
- `financial_analyst`: Transforms extracted data into metrics, scenarios, recommendations; produces `pushover_summary` (still available if you re-enable notifications).
- `report_generator`: Generates a 10-section stakeholder-ready Markdown report (Pushover integration removed from config by default).

### Tools
- `landing_ai_document_extractor`: LandingAI ADE wrapper for robust OCR + structure.
- `calculator`: Sandboxed evaluation for formulas (ratios, CAGR, NPV, WACC, etc.).
- `pushover_notifier` (optional): Can be re-added to `report_generator` if push alerts are desired.

### Configuration Files
- `src/doc_analizer/config/agents.yaml`: Agent definitions (roles, goals, prompts, tools, LLM provider).
- `src/doc_analizer/config/tasks.yaml`: Task descriptions, expected outputs, and agent mapping.
- `src/doc_analizer/crew.py`: Crew assembly, tool exposure helpers.

### Output Contracts
- Extraction: JSON with metadata, tables, key-value pairs, narratives, attachments, issues.
- Analysis: JSON with executive_summary, metrics[], risk_assessment[], scenario_analysis{}, recommendations[], data_gaps[], pushover_summary.
- Report: Markdown ONLY with 10 ordered sections (Executive Summary → Appendix). Every metric shows formula & provenance reference.

## Installation

Ensure you have Python >=3.10 <3.14. This project uses [UV](https://docs.astral.sh/uv/) for dependency and environment management.

Install `uv` if not present:
```bash
pip install uv
```

Install project dependencies (inside repo root):
```bash
uv sync
```

Alternatively (CrewAI helper):
```bash
crewai install
```

## Environment Variables
Create a `.env` file (see `.env.example` for template) for active providers:

**LLM Provider (choose one or more):**
- `OPENAI_API_KEY` and optionally `OPENAI_MODEL_NAME` (default: gpt-4)
- `GROQ_API_KEY` and optionally `GROQ_MODEL_NAME` (default: llama3-70b-8192)
- `OPENROUTER_API_KEY` (and optionally `OPENROUTER_BASE_URL`, `OPENROUTER_MODEL`, `OPENROUTER_HTTP_REFERER`, `OPENROUTER_APP_TITLE`)
- `GOOGLE_API_KEY` (for Gemini models)

**Required for Document Extraction:**
- `LANDINGAI_API_KEY` - Required for the LandingAI ADE document extraction tool

**Optional Integrations:**
- `PUSHOVER_USER_KEY` and `PUSHOVER_API_TOKEN` – Only if you re-enable push notifications

If you remove or disable an integration, ensure the corresponding agent `tools` and prompt references are updated.

### Setting up .env file
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

## Running the Project

### Option 1: Direct Python Execution
From repository root:
```bash
crewai run
```
This executes the configured crew: extraction → analysis → report.

### Option 2: Using the CLI Runner Script
For more control over document paths and analysis type:
```bash
python run_agent.py --doc /path/to/document.pdf --analysis "annual financial report"
```

Additional options:
```bash
# Analyze multiple documents
python run_agent.py --doc doc1.pdf --doc doc2.pdf --analysis "quarterly report"

# Specify custom output directory
python run_agent.py --doc report.pdf --analysis "Q4 2024" --output-dir custom_output

# Enable verbose mode
python run_agent.py --doc report.pdf --analysis "financial analysis" --verbose
```

### Option 3: Docker Container (Recommended for Production)

#### Prerequisites
- Docker and Docker Compose installed
- API keys configured in `.env` file

#### Setup
1. Copy the example environment file and configure your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

2. Create a `documents` directory and place your PDFs:
```bash
mkdir -p documents
cp your-financial-report.pdf documents/
```

#### Build the Docker Image
```bash
docker-compose build
```

#### Run Analysis with Docker Compose

**Method 1: Using docker-compose run (Recommended)**
```bash
# Basic usage
docker-compose run --rm doc-analyzer --doc /app/data/report.pdf --analysis "financial report"

# Analyze sample PDF
docker-compose run --rm doc-analyzer \
  --doc /app/sample_pdfs/NASDAQ_TSLA_2024.pdf \
  --analysis "tesla annual financial report"

# Multiple documents
docker-compose run --rm doc-analyzer \
  --doc /app/data/q1.pdf \
  --doc /app/data/q2.pdf \
  --analysis "quarterly comparison"
```

**Method 2: Using the analyze-document service**
Edit the `command` section in `docker-compose.yml` under `analyze-document` service, then:
```bash
docker-compose --profile manual up analyze-document
```

#### Direct Docker Commands
```bash
# Build image
docker build -t doc-analyzer:latest .

# Run with mounted volumes
docker run --rm \
  --env-file .env \
  -v $(pwd)/documents:/app/data:ro \
  -v $(pwd)/output:/app/output \
  doc-analyzer:latest \
  --doc /app/data/report.pdf \
  --analysis "financial report"
```

#### Volume Mappings
- `./documents` → `/app/data` (read-only): Place your input PDFs here
- `./output` → `/app/output`: Generated reports will appear here
- `./tests/sample_pdfs` → `/app/sample_pdfs` (read-only): Sample PDFs for testing

Generated artifacts:
- `output/{analysis_type}_analyze.md` (JSON-like analysis output)
- `output/{analysis_type}_report.md` (final Markdown report)

## Testing
Calculator tool tests:
```bash
uv run python tests/test_calculator.py
```
Extend tests by adding scenarios to `tests/` for new financial formulas or edge cases (e.g., division by zero handling, negative cash flows).

## Customization Workflow
1. Adjust agent LLMs in `agents.yaml` (e.g., switch `report_generator` model).
2. Modify prompt sections (`report_format`, `analysis_framework`) to tighten or relax constraints.
3. Add new tools in `src/doc_analizer/tools/` and register them in `__init__.py`.
4. Wire tools to agents by editing their `tools:` lists.
5. Update tasks in `tasks.yaml` to reflect new expected outputs.

## Troubleshooting
- Provider 404 errors: Check base URL env vars; ensure no conflicting `OPENAI_API_BASE` overrides when using Groq.
- Rate limit errors (TPM): Switch to larger context model or chunk requests.
- JSON repair artifacts: Strengthen output_contract or reduce temperature.
- Missing provenance: Ensure extraction agent includes page + locator for every datapoint.

---
DocAnalizer focuses on traceable, decision-grade financial insight generation. Contributions and issue reports are welcome.
