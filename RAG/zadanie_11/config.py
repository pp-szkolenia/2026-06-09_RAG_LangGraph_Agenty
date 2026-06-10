import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_core.runnables import ConfigurableField
from qdrant_client import QdrantClient

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
COLLECTION_NAME = "biblia"

client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))

embeddings = HuggingFaceEmbeddings(model_name="sdadas/mmlw-retrieval-roberta-large-v2")

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.HYBRID,
)

retriever = vector_store.as_retriever().configurable_fields(
    search_kwargs=ConfigurableField(id="search_kwargs")
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

with open(DATA_DIR / "unique_metadata_values.json") as f:
    METADATA_JSON = json.dumps(json.load(f), ensure_ascii=False)
