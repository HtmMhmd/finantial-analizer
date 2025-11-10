# DocAnalizer — System Presentation

A concise, visual walkthrough of the DocAnalizer system: components, data flow, runtime sequence, and deployment.

## 1) What it does (1 slide)
- Ingest financial PDFs
- Extract structured data with provenance
- Analyze metrics, risks, and scenarios
- Generate a stakeholder-ready Markdown report

Inputs: One or more PDF files
Outputs: Two Markdown files in `output/`:
- `<analysis_type>_analyze.md` (structured analysis dump)
- `<analysis_type>_report.md` (final report)

## 2) Architecture overview (diagram)
```mermaid
graph TD
  U((User)) -->|PDF(s)| D[/documents/]
  D --> EX[Extraction Agent]
  EX -->|JSON+Provenance| AN[Financial Analyst Agent]
  AN -->|Metrics+Scenarios| RG[Report Generator Agent]
  RG -->|Markdown Report| O[(output/)]

  EX -.calls.-> ADE[(LandingAI ADE API)]
  AN -.prompts.-> LLM[(LLM Provider)]
  AN -.computes.-> CALC[(Calculator Tool)]
  RG -.optional.-> PUSH[(Pushover)]

  classDef ext fill:#F6F8FF,stroke:#6B8EFF;
  classDef api fill:#FFF7E6,stroke:#FFB020;
  class EX,AN,RG ext;
  class ADE,LLM,CALC,PUSH api;
```

## 3) End-to-end system flow (flowchart)
```mermaid
flowchart LR
  A([Start]) --> B[Parse CLI args / env]
  B --> C{All documents exist?}
  C -- No --> E[[Exit with error]]
  C -- Yes --> D[Create output directory]
  D --> F[Run CrewAI pipeline]
  F --> X[Extraction]
  X --> Y[Analysis]
  Y --> Z[Report generation]
  Z --> G[Write outputs to /app/output]
  G --> H([Done])
```

## 4) Runtime sequence (agents, tools, providers)
```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant CLI as run_agent.py
  participant Crew as CrewAI Orchestrator
  participant Ext as document_extractor
  participant Ana as financial_analyst
  participant Rep as report_generator
  participant ADE as LandingAI ADE
  participant LLM as LLM Provider
  participant Calc as Calculator Tool

  U->>CLI: Provide --doc paths, --analysis type
  CLI->>Crew: kickoff(inputs)
  Crew->>Ext: extract_documents(file_paths)
  Ext->>ADE: OCR/structure extract
  ADE-->>Ext: JSON with tables/kv/narrative+provenance
  Ext-->>Crew: extracted JSON

  Crew->>Ana: analyze_financial_data(extracted JSON)
  Ana->>LLM: Generate metrics/risks/scenarios
  Ana->>Calc: Compute ratios (CAGR, margins, etc.)
  LLM-->>Ana: Structured analysis JSON
  Calc-->>Ana: Numeric results
  Ana-->>Crew: analysis JSON

  Crew->>Rep: generate_report(analysis JSON)
  Rep->>LLM: Draft Markdown sections
  LLM-->>Rep: Markdown content
  Rep-->>CLI: Write <type>_report.md and <type>_analyze.md
  CLI-->>U: Print output directory path
```

## 5) Deployment view (Docker + volumes)
```mermaid
graph LR
  subgraph Host
    docs[/./documents/]:::vol
    out[/./output/]:::vol
    env> .env ]:::env
  end

  subgraph Container[doc-analyzer]
    data[/app/data/]:::bind
    outc[/app/output/]:::bind
    run[python run_agent.py]:::proc
  end

  docs -- bind:ro --> data
  out -- bind:rw --> outc
  env -. env-file .-> Container

  classDef vol fill:#F0FFF4,stroke:#38A169;
  classDef bind fill:#EBF8FF,stroke:#3182CE;
  classDef proc fill:#FFF5F5,stroke:#E53E3E;
  classDef env fill:#FAF5FF,stroke:#805AD5;
```

## 6) Key components (cheat sheet)
- Crew: `DocAnalizer` in `src/doc_analizer/crew.py`
- Agents: `document_extractor`, `financial_analyst`, `report_generator`
- Tools: `LandingAIDocumentExtractor`, `CalculatorTool`, `PushoverNotifier (optional)`
- Config: `src/doc_analizer/config/agents.yaml`, `src/doc_analizer/config/tasks.yaml`
- CLI: `run_agent.py` (accepts `--doc` multiple times, `--analysis`, `--output-dir`)

## 7) Run options
- Local: `python run_agent.py --doc path/to.pdf --analysis "financial report"`
- Docker Compose:
  - Place PDFs in `./documents`
  - Outputs appear in `./output`
  - Example:
    - `docker-compose run --rm doc-analyzer --doc /app/data/your.pdf --analysis "financial report"`

## 8) Notes and assumptions
- Requires valid API keys for LandingAI and an LLM provider (OpenAI, Groq, etc.)
- Large PDFs and image-heavy scans will increase extraction time
- Outputs are deterministic only to the extent of fixed prompts/model settings

---
This presentation is auto-generated to reflect the current repository structure and runtime flow. Adjust diagrams as you customize agents, tools, or deployment.
