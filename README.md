# LifeLong Memory Engine for LLMs (Local Context Orchestrator)

A lightweight, zero-cost, privacy-first persistent memory orchestrator designed to solve context drift, conversational hallucination, and token memory limits across long-running LLM chat sessions (such as `gemini.google.com`).

---

## 1. Problem Statement & Motivation

Large Language Models (LLMs) operate under strict finite context windows. Over extended interactions:
1. **Context Eviction:** Critical instructions, architectural decisions, and project constraints get flushed out as token limits are approached.
2. **Hallucination & Topic Drift:** When context is lost, models guess previous states rather than referencing actual decisions.
3. **API Cost vs. Web UI Trade-off:** While paid APIs offer programmatic embeddings, long-term multi-million-token pipelines become expensive. Web interfaces are free but stateless across new chat threads.

**Solution:** An external, local, deterministic memory engine that stores, deduplicates, prunes, and injects context on demand directly into web-based AI interfaces without external API bills or cloud privacy exposure.

---

## 2. Architecture & Design Principles

```
                  +-----------------------------------+
                  |         Web Chat UI               |
                  |     (gemini.google.com)           |
                  +-----------------+-----------------+
                                    ^
       Ctrl + V (Inject Context)    |   Ctrl + C (Copy Raw Logs)
                                    v
                  +-----------------+-----------------+
                  |       clipboard_bridge.py         |
                  +--------+-----------------+--------+
                           |                 |
                copy mode  |                 | save mode
                           v                 v
            +--------------+----+     +------+----------------+
            | memory_manager.py |     |   chat_cleaner.py     |
            +--------------+----+     +------+----------------+
                           ^                 |
                           | Reads/Writes    | Cleans & Deduplicates
                           v                 v
                  +--------+-----------------+--------+
                  |            memory.json            |
                  |   (Structured Flat-File Store)    |
                  +-----------------+-----------------+
                                    ^
                                    | Monitors & Archives
                                    v
                  +-----------------+-----------------+
                  |            pruner.py              |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |       memory_archive.json         |
                  +-----------------------------------+
```

### Core Tenets:
- **Privacy-First (Local by Default):** Data resides on your own filesystem (`memory.json`).
- **Zero Compute Overhead:** Employs regex filters, sequence matching, and metadata scoring rather than heavy local language models.
- **Deduplication at Ingestion:** Repeated facts increase engagement scores rather than wasting disk and token space.
- **Smart Pruning:** Prevents unbounded memory growth through size monitoring and interactive archiving.

---

## 3. Project Structure

```
ai_memory_engine/
│
├── memory_manager.py     # Base store initialization, read/write, prompt generator
├── chat_cleaner.py       # Boilerplate noise stripper, fuzzy deduplication
├── clipboard_bridge.py   # CLI bridge between system clipboard and browser UI
├── pruner.py             # Storage threshold monitor & interactive archive engine
├── memory.json           # Active structured memory store (auto-generated)
└── memory_archive.json   # Cold storage for pruned items (auto-generated)
```

---

## 4. Setup & Installation

### Prerequisites
- Python 3.8+
- Operating System: Windows, macOS, or Linux

### Dependencies
Install the required clipboard library:

```bash
pip install pyperclip
```

---

## 5. Module Reference

### 5.1. `memory_manager.py`
The data foundation of the engine.
- **`init_memory()`**: Verifies or creates the initial schema structure in `memory.json`.
- **`load_memory()` / `save_memory(data)`**: Safe JSON I/O utilities.
- **`add_fact(category, content, importance=3)`**: Stores facts with a unique incremental ID, timestamp, and metadata.
- **`generate_context_prompt()`**: Extracts active projects and sorts stored facts by importance, outputting a consolidated prompt block ready for chat injection.

### 5.2. `chat_cleaner.py`
The cleaning and deduplication pipeline.
- **`clean_raw_text(raw_text)`**: Uses compiled regular expressions to strip LLM boilerplate ("As an AI language model...", "Sure, I can help...", "Let me know if you need anything else...").
- **`is_duplicate(new_text, existing_facts, similarity_threshold=0.75)`**: Computes `SequenceMatcher` similarity against existing records.
- **`ingest_raw_conversation(raw_text, category, default_importance)`**: Evaluates cleaned lines, increments access counters for duplicates, and commits novel facts.

### 5.3. `clipboard_bridge.py`
The operator interface.
- **`copy` Command**: Formats the latest high-priority context and places it on your system clipboard.
- **`save` Command**: Reads copied text from your clipboard, strips noise via `chat_cleaner.py`, and ingests it into `memory.json`.

### 5.4. `pruner.py`
The garbage collector and storage monitor.
- **`get_file_size_mb(filepath)`**: Computes file footprint.
- **`check_storage_status()`**: Evaluates current file size against `max_size_mb`. Triggers warnings if usage exceeds 80%.
- **`prune_low_value_facts(max_importance_threshold=2)`**: Identifies low-priority or outdated knowledge and allows interactive migration to `memory_archive.json`.

---

## 6. Daily Usage Workflow

### Step 1: Starting a New Chat Session
Before beginning a conversation on `gemini.google.com` or any LLM interface:

```bash
python clipboard_bridge.py copy
```
1. Open the LLM input box.
2. Press `Ctrl + V` (or `Cmd + V`).
3. Append your prompt or task right after the injected block and send.

### Step 2: Saving Important Chat Outcomes
When the assistant generates architectural decisions, summaries, or preferences you want to persist:
1. Highlight and copy the text in your browser (`Ctrl + C`).
2. Run in terminal:

```bash
python clipboard_bridge.py save
```
*(Optional: supply a custom category)*
```bash
python clipboard_bridge.py save technical_decisions
```

### Step 3: Routine Maintenance & Optimization
Periodically check memory health and archive obsolete facts:

```bash
python pruner.py
```
If low-importance candidates are found, confirm (`y`) to move them from `memory.json` to `memory_archive.json`.

---

## 7. Storage Schema Reference

### Active Store (`memory.json`)
```json
{
  "system_config": {
    "max_size_mb": 10.0,
    "user_name": "User"
  },
  "facts": [
    {
      "id": 1,
      "category": "technical_preference",
      "content": "Prefers Python for data engineering and backend tasks.",
      "importance": 5,
      "timestamp": "2026-10-11 21:30:00",
      "access_count": 3
    }
  ],
  "active_projects": [
    {
      "project_name": "LifeLong Memory Engine",
      "current_goal": "Local context orchestrator integration",
      "last_updated": "2026-10-11 21:30:00"
    }
  ]
}
```

---

## 8. Scaling & Future Roadmap

1. **Cloud Sync:** Integrate Google Drive API to synchronize `memory.json` across multiple workstations.
2. **Browser Extension:** Transition from Python CLI clipboard bridge to a native browser extension with automatic background injection.
3. **Local Vector Search:** Upgrade from regex/exact heuristics to an embedded vector store (e.g., ChromaDB or SQLite-VSS) for semantic retrieval at larger scales (>50 MB).