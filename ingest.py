import re
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCUMENTS_DIR = Path("documents")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def load_documents(docs_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    docs = []
    for path in sorted(docs_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            docs.append({"text": text, "source": path.name})
    return docs


def clean_text(text: str) -> str:
    # Remove RMP "Tags:" lines — keyword labels, not review content
    text = re.sub(r"^Tags:.*$", "", text, flags=re.MULTILINE)
    # Collapse 3+ blank lines down to 2 (one paragraph break)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_documents(docs: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        splits = splitter.split_text(cleaned)
        for i, split in enumerate(splits):
            if len(split.strip()) >= 50:
                chunks.append({
                    "text": split.strip(),
                    "source": doc["source"],
                    "chunk_id": f"{doc['source']}::chunk_{i}",
                })
    return chunks


if __name__ == "__main__":
    print("Loading documents...")
    docs = load_documents()
    print(f"  Loaded {len(docs)} documents\n")

    print("Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"  Total chunks: {len(chunks)}\n")

    # Print 5 chunks spread evenly across the full collection
    print("=" * 60)
    print("SAMPLE CHUNKS (5 evenly spaced)")
    print("=" * 60)
    step = max(1, len(chunks) // 5)
    for i in range(5):
        idx = i * step
        if idx < len(chunks):
            c = chunks[idx]
            print(f"\n[Chunk {idx}]  source: {c['source']}")
            print("-" * 40)
            print(c["text"])
    print("\n" + "=" * 60)
    print(f"Total chunks: {len(chunks)} across {len(docs)} documents")
    print("=" * 60)
