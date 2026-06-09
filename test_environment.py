"""Health check for RAG + LangGraph environment."""
import sys

OK, FAIL = "OK  ", "FAIL"
results = {}


def check(label):
    def decorator(fn):
        try:
            fn()
            results[label] = OK
            print(f"[{OK}] {label}")
        except Exception as e:
            results[label] = f"{FAIL}: {e}"
            print(f"[{FAIL}] {label}: {e}")
    return decorator


# ── 1. Core imports ────────────────────────────────────────────────────────────

@check("import: langchain-core")
def _():
    from langchain_core.prompts import PromptTemplate
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

@check("import: langchain-community")
def _():
    import langchain_community

@check("import: langgraph")
def _():
    from langgraph.graph import StateGraph, START, END

@check("import: qdrant-client")
def _():
    from qdrant_client import QdrantClient, models

@check("import: langchain-qdrant")
def _():
    from langchain_qdrant import QdrantVectorStore

@check("import: langchain-huggingface")
def _():
    from langchain_huggingface import HuggingFaceEmbeddings

@check("import: langchain-openai")
def _():
    from langchain_openai import ChatOpenAI

@check("import: sentence-transformers")
def _():
    import sentence_transformers

@check("import: fastembed")
def _():
    import fastembed


# ── 2. Text splitter ───────────────────────────────────────────────────────────

@check("text splitter")
def _():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=5)
    chunks = splitter.split_text("Hello world. This is a test sentence for splitting.")
    assert len(chunks) >= 1


# ── 3. HuggingFace embeddings ──────────────────────────────────────────────────

@check("HuggingFace embeddings (all-MiniLM-L6-v2)")
def _():
    from langchain_huggingface import HuggingFaceEmbeddings
    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vec = emb.embed_query("test")
    assert len(vec) == 384


# ── 4. Qdrant in-memory ────────────────────────────────────────────────────────

@check("Qdrant in-memory: create / upsert / search / delete")
def _():
    from qdrant_client import QdrantClient, models
    client = QdrantClient(":memory:")
    col = "_health_check_"
    client.create_collection(col, vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE))
    client.upsert(col, points=[models.PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4], payload={"x": 1})])
    hits = client.query_points(col, query=[0.1, 0.2, 0.3, 0.4], limit=1).points
    assert len(hits) == 1
    client.delete_collection(col)


# ── 5. Qdrant localhost ────────────────────────────────────────────────────────

@check("Qdrant localhost:6333: create / upsert / search / delete")
def _():
    from qdrant_client import QdrantClient, models
    client = QdrantClient(url="http://localhost:6333", timeout=5)
    col = "_health_check_tmp_"
    if client.collection_exists(col):
        client.delete_collection(col)
    client.create_collection(col, vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE))
    client.upsert(col, points=[models.PointStruct(id=1, vector=[0.1, 0.2, 0.3, 0.4])])
    hits = client.query_points(col, query=[0.1, 0.2, 0.3, 0.4], limit=1).points
    assert len(hits) == 1
    client.delete_collection(col)


# ── 6. LangChain + Qdrant in-memory vector store ──────────────────────────────

@check("LangChain QdrantVectorStore (in-memory)")
def _():
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_qdrant import QdrantVectorStore
    from langchain_core.documents import Document
    from qdrant_client import QdrantClient

    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    client = QdrantClient(":memory:")
    vs = QdrantVectorStore.from_documents(
        documents=[Document(page_content="hello world")],
        embedding=emb,
        location=":memory:",
        collection_name="_lc_check_",
    )
    results_vs = vs.similarity_search("hello", k=1)
    assert len(results_vs) == 1


# ── 7. LangGraph graph build & invoke ─────────────────────────────────────────

@check("LangGraph: build and invoke a simple graph")
def _():
    from typing import TypedDict
    from langgraph.graph import StateGraph, START, END

    class S(TypedDict):
        value: int

    def double(state: S):
        return {"value": state["value"] * 2}

    g = StateGraph(S)
    g.add_node("double", double)
    g.add_edge(START, "double")
    g.add_edge("double", END)
    app = g.compile()
    out = app.invoke({"value": 3})
    assert out["value"] == 6


# ── 8. LangChain prompt template ──────────────────────────────────────────────

@check("LangChain PromptTemplate")
def _():
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([("human", "Say {word}")])
    msgs = prompt.format_messages(word="hi")
    assert msgs[0].content == "Say hi"


# ── Summary ────────────────────────────────────────────────────────────────────

passed = sum(1 for v in results.values() if v == OK)
total = len(results)
failed = [(k, v) for k, v in results.items() if v != OK]

print(f"\n{'='*55}")
print(f"SUMMARY: {passed}/{total} checks passed")
if failed:
    print("\nFailed checks:")
    for k, v in failed:
        print(f"  - {k}: {v}")
else:
    print("All checks passed.")
print('='*55)
sys.exit(0 if not failed else 1)
