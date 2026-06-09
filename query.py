import os
from dotenv import load_dotenv
from groq import Groq
from embed import build_index, retrieve

load_dotenv()

_groq_client = None


def _get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Make sure .env is set up.")
        _groq_client = Groq(api_key=api_key)
    return _groq_client


SYSTEM_PROMPT = """You are a helpful assistant that answers questions about UC Berkeley CS courses and professors.

Answer the question using ONLY the document excerpts provided below. Do not use any outside knowledge or information beyond what is in these excerpts.

For each claim in your answer, cite the source document in parentheses — for example: (source: rmp_john_denero_cs61a.txt).

If the provided excerpts do not contain enough information to answer the question, respond with exactly:
"I don't have enough information in the provided documents to answer that question."

Do not speculate or fill in gaps with general knowledge."""


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] Source: {chunk['source']}\n{chunk['text']}")
    return "\n\n".join(parts)


def ask(question: str, k: int = 5) -> dict:
    chunks = retrieve(question, k=k)
    context = _build_context(chunks)

    user_message = f"Document excerpts:\n\n{context}\n\nQuestion: {question}"

    response = _get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()
    # Collect unique sources from retrieved chunks (preserving order)
    seen = set()
    sources = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.add(chunk["source"])
            sources.append(chunk["source"])

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    build_index()

    test_questions = [
        "Is CS61A harder to take in the summer compared to the regular semester?",
        "What do students say about Dan Garcia's grading practices in CS61C?",
        # Out-of-scope test — system should decline, not hallucinate
        "What is the best off-campus apartment near Berkeley?",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        print("=" * 70)
        result = ask(q)
        print(result["answer"])
        print(f"\nSources: {', '.join(result['sources'])}")
        print()
