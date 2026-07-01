# SHL Product Recommendation Agent

A production-grade, stateful, and deterministic runtime recommendation pipeline built for selecting assessments from the official SHL product catalog. 

This agent uses a **hybrid architecture** designed for high reliability: **Gemini 2.5** is utilized solely for natural language understanding and linguistic generation, while a **deterministic Finite State Machine (FSM)** handles business logic, workflow transitions, and required parameter tracking. Authoritative metadata matching is performed programmatically from local FAISS indices, preventing vector catalog hallucinations.

---

## 🏛 Architecture Overview

```
User Query / History
       │
       ▼
 FastAPI (/chat)
       │
       ▼
Extractor (Gemini) ──► Parses user intent, roles, level, constraints into ConversationState
       │
       ▼
Decision FSM ───────► Deterministically computes missing fields and routes state (CLARIFY, RETRIEVE, etc.)
       │
       ▼
Retriever ──────────► Formulates queries, searches FAISS, filters on languages, levels, duration, remote
       │
       ▼
Prompt Generator ───► Standardizes instructions based on FSM state (battery, compare tables, refuse legal)
       │
       ▼
Linguistic Gemini ──► Generates reasoning descriptions matching catalog items
       │
       ▼
Metadata Merger ────► Re-inserts authoritative catalog names/links programmatically into AgentResponse
```

---

## 📁 Project Structure

* `main.py` - FastAPI entry point and server controller.
* `agent/`
  * `extractor.py` - Structured context and entity extractor using `gemini-2.5-flash`.
  * `fsm.py` - Deterministic python FSM mapping states and checking missing fields.
  * `generator.py` - Prompt builder and response generator with exponential rate backoff.
  * `schemas.py` - Pydantic models for structured output constraints.
  * `demo_fallback.py` - High-fidelity mock simulator used to bypass API quota blocks (429 rate limit exceptions).
* `retriever/`
  * `retriever.py` - FAISS similarity search and multi-constraint metadata filter (languages, levels mapping, durations).
  * `models.py` - Dataclasses for `SHLDocument` and `ConversationState`.
* `scripts/`
  * `build_documents.py` - Cleans raw catalog JSON files and builds schema docs.
  * `build_embeddings.py` - Generates vector embedding matrix via `gemini-embedding-2` with pacing.
  * `build_faiss.py` - Builds flat inner-product FAISS index for Cosine Similarity search.
  * `evaluate_traces.py` - Simulation runner executing all 10 official conversations.
* `tests/` - Comprehensive test suites (document builder, embeddings, FSM, retriever, generator, FastAPI routes).

---

## 🚀 Getting Started

### 1. Installation
Set up python environment and install requirements:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Server
Launch the local API server:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```
Interactive API docs will be available at: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

> [!NOTE]
> **API Quota Protection (Demo Mode)**: 
> If uvicorn encounters a `429 RESOURCE_EXHAUSTED` warning (daily limit exhausted on free-tier keys), it **automatically falls back to a high-fidelity demo mode**, serving mock responses for key developer, leadership, plant operator, and admin assistant queries instead of crashing with a 500 error.
>
> You can also force demo mode on uvicorn startup by setting the environment variable:
> `DEMO_MODE=true uvicorn main:app`

---

## 🧪 Testing & Evaluation

### Run Unit Tests
Execute the full unit test suite (all 24 tests):
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### Run Evaluation Suite
Execute the turn-by-turn simulation through all 10 official markdown conversations:
```bash
python3 scripts/evaluate_traces.py
```
This produces an alignment metrics analysis saved to `data/processed/evaluation_report.md`.
