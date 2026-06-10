# Zadanie 11 — Bible RAG Pipeline (LangGraph)

A LangGraph pipeline that answers questions about the Bible by chaining retrieval,
context expansion, LLM filtering, thematic grouping, and structured answer generation.

## Requirements

- Running Qdrant instance at `http://localhost:6333` with the `biblia` collection
  (populated via Zadanie 1 in the notebook)
- `.env` file in the project root (`../`) with `OPENAI_API_KEY` set

## Running

```bash
cd zadanie_11
python main.py "Twoje pytanie o Biblii"
```

### Options

| Argument | Values | Default | Description |
|---|---|---|---|
| `query` | any string | — | Question to ask (required) |
| `--level` | `basic` `medium` `deep` | `medium` | Analysis depth; controls how many verses are retrieved per request |
| `--debug` | flag | off | Print progress info after each pipeline step |

### Examples

```bash
# Basic query
python main.py "Co Biblia mówi o miłości bliźniego?"

# Deep analysis with debug output
python main.py "Czego Biblia uczy o pieniądzach i bogactwie?" --level deep --debug

# Quick lookup
python main.py "Ile dni trwał biblijny potop?" --level basic
```

## Pipeline steps

```
START
  └─► generate_requests    LLM generates 1–3 semantic search queries with optional Qdrant filters
  └─► execute_retrieval    Hybrid retrieval from Qdrant, results deduplicated across queries
  └─► expand_neighbors     Each verse is expanded with the previous and next verse (same chapter)
  └─► filter_irrelevant    LLM batch-judges each expanded verse for relevance (parallel calls)
  └─► group_results        LLM groups relevant verses into thematic categories
  └─► retrieve_chapters    Full chapter texts fetched for each category (cached within a run)
  └─► generate_answer      LLM generates a structured answer per aspect (parallel calls)
END
```

## File structure

```
zadanie_11/
├── main.py               # CLI entry point
├── pipeline.py           # graph builder + run_query()
├── state.py              # PipelineState TypedDict
├── config.py             # Qdrant client, embeddings, LLM, metadata
├── models.py             # Pydantic models for structured outputs
├── prompts.py            # prompt templates
└── nodes/
    ├── generate_requests.py
    ├── execute_retrieval.py
    ├── expand_neighbors.py
    ├── filter_irrelevant.py
    ├── group_results.py
    ├── retrieve_chapters.py
    └── generate_answer.py
```
