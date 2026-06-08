# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews and community knowledge about CS professors and courses at UC Berkeley. This knowledge is valuable because official course descriptions list topics and prerequisites but reveal nothing about how a professor actually teaches, how hard exams are, which projects take 40 hours, or how the curve works in practice. Students share this knowledge with each other through Rate My Professors and Reddit (r/berkeley) — but it's scattered across platforms and impossible to search with a single question. This system makes it queryable.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors — John DeNero, CS61A | RMP reviews: teaching style, exam format, grading | `documents/rmp_john_denero_cs61a.txt` |
| 2 | Rate My Professors — Josh Hug, CS61B | RMP reviews: lectures, projects, workload | `documents/rmp_josh_hug_cs61b.txt` |
| 3 | Rate My Professors — Dan Garcia, CS61C | RMP reviews: grading practices, exam difficulty, "A's for All" controversy | `documents/rmp_dan_garcia_cs61c.txt` |
| 4 | Rate My Professors — Satish Rao, CS70 | RMP reviews: proof difficulty, teaching style, exam grading | `documents/rmp_satish_rao_cs70.txt` |
| 5 | Reddit r/berkeley — CS61A prep thread | How to prepare for CS61A; advice on environment diagrams and exam pacing | `documents/CS61A_reddit_thread.txt` |
| 6 | Reddit r/berkeley — CS61A difficulty thread | Is CS61A hard over the summer? Student experiences and exam averages | `documents/CS61A_difficulty_reddit_thread.txt` |
| 7 | Reddit r/berkeley — CS61B prep thread | How to prepare for CS61B; Java basics and early project advice | `documents/CS61B_prep_reddit_thread.txt` |
| 8 | Reddit r/berkeley — CS61C exam thread | Student reactions to a CS61C midterm; virtual addresses and little endian | `documents/CS61C_reddit_thread.txt` |
| 9 | Reddit r/berkeley — CS70 difficulty thread | How hard is CS70 without a math background; strategies that worked | `documents/CS70_reddit_thread.txt` |
| 10 | Reddit r/berkeley — CS study tips thread | Study tips for CS61A and Math 54 taken together over summer | `documents/CS_tips_reddit_thread.txt` |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Reasoning:** The documents consist almost entirely of short-form opinion text — individual RMP reviews (50–150 words each) and Reddit comments (20–100 words each). At 500 characters, a single chunk captures roughly one complete review or 2–3 short comments, which is the right unit of meaning: one person's full opinion stays together. Smaller chunks (e.g., 200 characters) would split a single review mid-sentence, so a chunk might contain only "exams are quite difficult" with no subject, making it nearly unretievable for a query about grading. Larger chunks (e.g., 1000+ characters) would merge multiple unrelated reviews, diluting the specific signal the embedding needs to match a targeted query.

The 50-character overlap ensures that a sentence straddling a chunk boundary (e.g., a key claim in the last line of one chunk and its qualifier at the start of the next) is captured by at least one chunk fully. Given the total corpus size (~17,500 characters across 10 documents), this strategy produces an estimated **40–50 chunks** — at the lower bound of the target range, but appropriate for a short-form corpus where individual opinions are the retrieval unit.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`. Runs locally — no API key, no rate limits, fast inference on CPU.

**Top-k:** 5 chunks per query. This gives the LLM enough context to synthesize an answer from multiple perspectives (e.g., two students agreeing and one dissenting) without flooding the prompt with loosely related material. For a small corpus like this, k=5 covers a meaningful fraction of the most relevant content without dilution.

**Production tradeoff reflection:** For a real deployment, I would weigh:
- **Context length:** `all-MiniLM-L6-v2` has a 256-token limit per chunk, which is tight for longer reviews. `all-mpnet-base-v2` supports 384 tokens and generally scores higher on benchmarks at the cost of slower inference.
- **Domain specificity:** Student slang ("cooked," "cracked," "goat") and course codes (CS61A, CS70) are informal and domain-specific. A general-purpose model may not encode these well. A fine-tuned model on student-generated text would retrieve more accurately but requires training data and infrastructure.
- **Latency vs. accuracy:** For a production web app with many concurrent users, an API-hosted model (e.g., OpenAI `text-embedding-3-small`) offloads compute but adds cost and latency per request. Local models like MiniLM are free per query but require a machine with enough memory to keep the model loaded.
- **Multilingual support:** Not needed for this English-only corpus, but relevant if the system ever covers international student communities.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Is CS61A harder to take in the summer compared to the regular semester? | Yes — students describe it as "unbelievably fast-paced," going at twice the normal speed. Raw exam averages were around 30–40% in one summer session. One student called it "nightmare mode." |
| 2 | What do students say about Dan Garcia's grading practices in CS61C? | Mixed. Garcia is praised as an amazing lecturer but criticized for grading: the "A's for All" policy is described as hard to achieve in practice; multiple students saw their grade drop from A to B+ after the final, and exam averages fell below the stated 65% target with small curves. |
| 3 | What strategies do students recommend for passing CS70 without a strong math background? | Read the course notes until you can recreate proofs yourself; grind practice exams starting a month before each test; attend discussions; use office hours. Students who procrastinated still managed a B due to the steep curve. |
| 4 | What do students say about Josh Hug's lectures in CS61B? | Highly positive. Reviews describe them as "amazing," "hilarious," and "inspirational." His CS61B curriculum is called "perfection." Students recommend attending lectures even when attendance is not tracked. |
| 5 | How do students recommend preparing for CS61A before the semester starts? | Watch DeNero's videos on cs61a.org to get familiar with content; practice environment diagrams on tutor.cs61a.org; optionally learn introductory Python first (CS50 is mentioned); begin studying for the first midterm after the first week or two of class. |

---

## Anticipated Challenges

1. **Short documents producing very few chunks and sparse retrieval.** Several documents are under 200 words. With 500-character chunks, the thinnest files (CS61A_reddit_thread.txt, CS61B_prep_reddit_thread.txt) will each produce only 2–3 chunks. If a query needs information from one of these files, there may simply not be enough content for a strong embedding match. Mitigation: if retrieval quality is poor for CS61B questions, reduce chunk size to 300 characters to increase chunk count, or collect additional CS61B documents.

2. **Course codes and informal language reducing embedding match quality.** Student text uses shorthand ("61A," "70," "cracked," "cooked") that a general-purpose embedding model may not represent well. A query phrased formally ("How difficult is CS61A?") may not match a chunk that says "61A is insane if you're not cracked." Mitigation: test retrieval with both formal and informal query phrasings and compare distance scores; if informal queries retrieve poorly, consider query expansion or rephrasing.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INDEXING PIPELINE                        │
│  (run once to build the vector store)                           │
└─────────────────────────────────────────────────────────────────┘

  documents/*.txt
       │
       ▼
┌─────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  Ingestion  │────▶│    Chunking      │────▶│ Embedding + Storage  │
│             │     │                  │     │                      │
│  Python     │     │  LangChain       │     │  sentence-           │
│  open()     │     │  RecursiveChar   │     │  transformers        │
│  read text  │     │  TextSplitter    │     │  all-MiniLM-L6-v2    │
│  + source   │     │  size=500        │     │                      │
│  metadata   │     │  overlap=50      │     │  ChromaDB            │
└─────────────┘     └──────────────────┘     │  (local, persisted)  │
                                             └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         QUERY PIPELINE                          │
│  (run on each user question)                                    │
└─────────────────────────────────────────────────────────────────┘

  user question
       │
       ▼
┌─────────────┐     ┌──────────────────────┐     ┌──────────────┐
│  Retrieval  │────▶│     Generation       │────▶│  Interface   │
│             │     │                      │     │              │
│  Embed      │     │  Groq API            │     │  Gradio      │
│  query →    │     │  llama-3.3-70b       │     │  web UI      │
│  ChromaDB   │     │  -versatile          │     │              │
│  top-k=5    │     │                      │     │  shows:      │
│  similarity │     │  system prompt       │     │  answer +    │
│  search     │     │  enforces grounding  │     │  sources     │
│             │     │  + source citation   │     │              │
└─────────────┘     └──────────────────────┘     └──────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude this planning.md (Documents section + Chunking Strategy section) and ask it to implement `ingest.py`: a script that loads every `.txt` file from `documents/`, attaches the filename as source metadata to each chunk, splits using `RecursiveCharacterTextSplitter` with `chunk_size=500` and `chunk_overlap=50`, prints 5 sample chunks with their source labels, and prints the total chunk count. I will verify the output by reading 5 printed chunks and confirming each one is a coherent, self-contained thought from the real document content — not a fragment, not HTML, not empty.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the Retrieval Approach section and the Architecture diagram and ask it to implement `embed.py` (embed all chunks from `ingest.py` into a persisted ChromaDB collection using `all-MiniLM-L6-v2`, storing source filename as metadata) and a `retrieve(query, k=5)` function that returns top-k chunks with distance scores and source names. I will verify by running the 5 evaluation questions through `retrieve()` and checking that returned chunks visibly relate to each question and that distance scores are below 0.5.

**Milestone 5 — Generation and interface:**
I will give Claude the Evaluation Plan section (so it knows the query types) and the Architecture diagram and ask it to implement `query.py` (wraps retrieval + Groq generation with a grounding system prompt) and `app.py` (Gradio UI with a question input, answer output, and sources output). I will verify grounding by asking a question that is NOT in the documents and confirming the system says it lacks information rather than generating a plausible-sounding answer from general knowledge.
