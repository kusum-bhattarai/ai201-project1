import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level singletons so model and collection are loaded once per process
_model = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model ({MODEL_NAME})...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def build_index(force: bool = False) -> None:
    collection = _get_collection()

    if collection.count() > 0 and not force:
        print(f"Index already built ({collection.count()} chunks). Pass force=True to rebuild.")
        return

    if collection.count() > 0:
        # Delete all existing entries before rebuilding
        existing_ids = collection.get()["ids"]
        collection.delete(ids=existing_ids)

    print("Loading and chunking documents...")
    chunks = chunk_documents(load_documents())
    print(f"  {len(chunks)} chunks ready\n")

    model = _get_model()
    print("Embedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    print("\nStoring in ChromaDB...")
    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    print(f"Done — {collection.count()} chunks stored in '{CHROMA_PATH}'\n")


def retrieve(query: str, k: int = 5) -> list[dict]:
    collection = _get_collection()
    model = _get_model()
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "text": doc,
            "source": meta["source"],
            "distance": round(dist, 4),
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    build_index()

    test_queries = [
        "Is CS61A harder to take in the summer compared to the regular semester?",
        "What do students say about Dan Garcia's grading practices in CS61C?",
        "What strategies do students recommend for passing CS70 without a strong math background?",
    ]

    for query in test_queries:
        print(f"Query: {query}")
        print("=" * 70)
        for i, r in enumerate(retrieve(query), 1):
            print(f"  [{i}] distance={r['distance']}  source={r['source']}")
            print(f"      {r['text'][:200].replace(chr(10), ' ')}")
        print()
