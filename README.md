# The Unofficial Guide — Project 1

---

## Domain

Student reviews and community knowledge about CS professors and courses at UC Berkeley. Official course descriptions list topics and prerequisites but reveal nothing about how a professor actually teaches, how hard exams are, which projects take 40 hours, or how the grading curve actually works. Students share this knowledge through Rate My Professors and Reddit (r/berkeley) — but it's scattered across platforms and impossible to search with a single question. This system makes it queryable: a user asks a plain-language question and gets a grounded, cited answer drawn from real student reviews and Reddit threads.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors — John DeNero, CS61A | RMP reviews | `documents/rmp_john_denero_cs61a.txt` |
| 2 | Rate My Professors — Josh Hug, CS61B | RMP reviews | `documents/rmp_josh_hug_cs61b.txt` |
| 3 | Rate My Professors — Dan Garcia, CS61C | RMP reviews | `documents/rmp_dan_garcia_cs61c.txt` |
| 4 | Rate My Professors — Satish Rao, CS70 | RMP reviews | `documents/rmp_satish_rao_cs70.txt` |
| 5 | Reddit r/berkeley — "How can I prepare for CS61A?" | Reddit thread | `documents/CS61A_reddit_thread.txt` |
| 6 | Reddit r/berkeley — "CS61A, how difficult is it?" | Reddit thread | `documents/CS61A_difficulty_reddit_thread.txt` |
| 7 | Reddit r/berkeley — "How to prep for CS61B?" | Reddit thread | `documents/CS61B_prep_reddit_thread.txt` |
| 8 | Reddit r/berkeley — "CS61C" (exam reaction thread) | Reddit thread | `documents/CS61C_reddit_thread.txt` |
| 9 | Reddit r/berkeley — "How hard is CS70 if you're not cracked?" | Reddit thread | `documents/CS70_reddit_thread.txt` |
| 10 | Reddit r/berkeley — "Study tips for math and CS?" | Reddit thread | `documents/CS_tips_reddit_thread.txt` |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** The documents consist entirely of short-form opinion text — individual RMP reviews (50–150 words each) and Reddit comments (20–100 words each), all separated by blank lines. At 500 characters, a single chunk captures roughly one complete review or 2–3 related comments. This keeps the natural unit of meaning (one person's opinion) together in one chunk, which is what the embedding model needs to produce a useful vector. Smaller chunks (e.g., 200 characters) would split a review mid-sentence, producing fragments like "exams are quite" with no subject or context. Larger chunks (1000+ characters) would merge multiple unrelated reviews, diluting the semantic signal.

The `RecursiveCharacterTextSplitter` tries paragraph breaks (`\n\n`) first before falling back to line breaks and then spaces. This means most reviews and comments stay intact as single chunks unless they exceed 500 characters. The 50-character overlap preserves sentences that straddle a boundary.

During implementation, a cleaning step was added to strip `Tags:` lines from RMP files (e.g., "Tags: Tough grader, Amazing lectures") and to drop any chunk under 50 characters. These were metadata labels, not review content, and would have polluted the vector store with near-empty embeddings.

**Final chunk count:** 57 chunks across 10 documents.

---

## Sample Chunks

Five representative chunks with their source document names:

**Chunk 1** — `CS61A_difficulty_reddit_thread.txt`
> u/Silent-Shallot-7351: I took CS61A in Summer '24. The class is unbelievably fast-paced. You essentially learn a new fundamental CS concept every day for the duration of the course. I had decent programming experience going in (Data 8/ high school APCSA level) but it still moved very quickly.

**Chunk 2** — `CS61B_prep_reddit_thread.txt`
> u/Broad-Author-712: Just learn some basic Java syntax (declaring variables, control, loops, and classes) so you can focus on the actual data structures from the start. That should be enough. That's what I did and I found it perfect because I could focus on the actual content immediately at the start of the class (which is the most fast paced part, as they'll tell you).

**Chunk 3** — `CS70_reddit_thread.txt`
> before the deadline you're going to have to work very hard AND very smart if you want to do well it's not impossible but it's not easy or even medium level difficult prior experience is the single biggest factor in determining where your grade is going to be along the distribution curve So with that in mind I'm not going to say "just work hard and you'll get your grade" because that's not how this class or real life really works

**Chunk 4** — `CS_tips_reddit_thread.txt`
> u/iced_matcha29: Have taken both of these but not over the summer. For 61A I'd recommend learning introductory python before you go into the class so you don't feel left behind (harvards online cs50 is a great resource for that). For 54 just look over matrices a bit and make sure you remember basic matrix operations. Overall advice is just to get a tiny head start so you're not overwhelmed

**Chunk 5** — `rmp_satish_rao_cs70.txt`
> Quality: 1.0 / Difficulty: 1.0 / Course: CS70 / Apr 1st, 2026
> Comment: Not recommended. Professor Rao's teaching style was difficult to follow, and he did not feel supportive when students needed help progressing in the course. Students should be cautious and clearly understand all course policies, as academic integrity concerns are taken very seriously.

Each chunk is readable and self-contained — each represents one student's complete opinion or one exchange of advice without requiring surrounding context to understand.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. Runs locally with no API key and no rate limits. Each chunk is embedded into a 384-dimensional vector and stored in a local ChromaDB collection with cosine similarity as the distance metric.

**Production tradeoff reflection:** For a real deployment, I would consider several tradeoffs. **Context length:** `all-MiniLM-L6-v2` has a 256-token limit per chunk, which is tight for longer reviews that may carry multiple distinct claims. `all-mpnet-base-v2` supports 384 tokens and generally scores higher on benchmarks, at the cost of slower inference. **Domain specificity:** Student slang ("cooked," "cracked," "goat") and Berkeley-specific shorthand ("61A," "70") are informal and domain-specific; a general-purpose model encodes these imprecisely, which weakens retrieval for informal queries. A fine-tuned model on student-generated text would retrieve more accurately but requires labeled training data. **Latency vs. cost:** An API-hosted model (e.g., OpenAI `text-embedding-3-small`) offloads compute but adds per-request cost and network latency. For a low-traffic internal tool, a local model like MiniLM keeps operating cost at zero. **Multilingual support:** Not relevant for this English-only corpus, but a consideration for any system covering international student communities.

---

## Retrieval Test Results

**Query 1:** "Is CS61A harder to take in the summer compared to the regular semester?"

| Rank | Distance | Source | Why relevant |
|------|----------|--------|-------------|
| 1 | 0.3441 | CS61A_difficulty_reddit_thread.txt | Direct account of a student who took CS61A in Summer '24, describes it as "unbelievably fast-paced" |
| 2 | 0.4158 | CS61A_difficulty_reddit_thread.txt | Follow-up from the same student comparing summer CS61A to fall CS61B |
| 3 | 0.4635 | CS70_reddit_thread.txt | Off-topic — a general "how hard is this class" comment about CS70, not CS61A summer |

Results 1 and 2 are directly relevant: both come from the same summer CS61A thread and contain the key information. Result 3 drifts to CS70 — the phrase "it's hard, depends on how much you grind" is semantically similar to the query without being topically relevant. This is expected in a small corpus where general difficulty language appears across multiple documents.

---

**Query 2:** "What do students say about Dan Garcia's grading practices in CS61C?"

| Rank | Distance | Source | Why relevant |
|------|----------|--------|-------------|
| 1 | 0.2826 | rmp_dan_garcia_cs61c.txt | A Garcia CS61C review — but the praise review ("absolute gem"), not the grading criticism ones |
| 2 | 0.4113 | rmp_satish_rao_cs70.txt | Off-topic — a CS70 review about Rao's teaching |
| 3 | 0.4162 | rmp_john_denero_cs61a.txt | Off-topic — a CS61A review about DeNero |

Only 1 of 5 retrieved chunks was from the correct document. This query is the documented **failure case** — see Failure Case Analysis below.

---

**Query 3:** "What strategies do students recommend for passing CS70 without a strong math background?"

| Rank | Distance | Source | Why relevant |
|------|----------|--------|-------------|
| 1 | 0.3561 | CS70_reddit_thread.txt | A student with a "relatively weak math background" describing how they studied — reading notes thoroughly, grinding |
| 2 | 0.3976 | CS70_reddit_thread.txt | The original question in the thread — "How hard is CS70 if you're not cracked?" — contextualizes the answers |
| 3 | 0.4709 | CS70_reddit_thread.txt | A long honest answer describing the course structure as the difficulty, not the content itself |

Results 1, 2, and 5 (all from CS70_reddit_thread.txt) are directly relevant: together they give a student's first-person account with weak math background plus strategic advice. Result 3 (CS61A difficulty thread) drifts in because the phrase "fast-paced... hard... prioritize the class" appears in both CS61A and CS70 difficulty discussions.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant that answers questions about UC Berkeley CS courses and professors.

Answer the question using ONLY the document excerpts provided below. Do not use any outside
knowledge or information beyond what is in these excerpts.

For each claim in your answer, cite the source document in parentheses — for example:
(source: rmp_john_denero_cs61a.txt).

If the provided excerpts do not contain enough information to answer the question, respond with
exactly: "I don't have enough information in the provided documents to answer that question."

Do not speculate or fill in gaps with general knowledge.
```

**How source attribution is surfaced in the response:** The LLM is instructed to cite sources inline (e.g., `source: CS70_reddit_thread.txt`) for each claim. In addition, the response object from `query.py` programmatically returns a `sources` list — the unique filenames of all retrieved chunks — which is displayed separately in the Gradio UI under "Retrieved from." Attribution is therefore double-enforced: instructed in the prompt and guaranteed structurally.

---

## Example Responses

**Example 1 — in-scope query with source citations:**

> **Q:** How do students recommend preparing for CS61A before the semester starts?
>
> **A:** According to the provided excerpts, students recommend preparing for CS61A by watching topical videos recorded by DeNero and getting familiar with the content on cs61a.org (source: CS61A_reddit_thread.txt). Additionally, it's suggested to play around with environment diagrams on tutor.cs61a.org to get a better understanding of the material, especially since it can be confusing at the beginning of the course (source: CS61A_reddit_thread.txt).
>
> **Retrieved from:** CS61A_difficulty_reddit_thread.txt • CS61A_reddit_thread.txt • CS61B_prep_reddit_thread.txt • rmp_josh_hug_cs61b.txt

**Example 2 — in-scope query with multiple sources:**

> **Q:** What do students say about Josh Hug's lectures in CS61B?
>
> **A:** According to the provided documents, students have varying opinions about Josh Hug's lectures in CS61B. One student comments that they would go to the lectures "for the experience and not for the attendance points" (source: rmp_josh_hug_cs61b.txt), implying that the lectures are enjoyable but not essential for understanding the material. Another student praises Hug as an "amazing professor who has a sense of humor, teaches really well, and looks out to his students" (source: rmp_josh_hug_cs61b.txt). Additionally, a student mentions that "his videos are cool" (source: rmp_josh_hug_cs61b.txt).
>
> **Retrieved from:** rmp_josh_hug_cs61b.txt • rmp_satish_rao_cs70.txt • rmp_john_denero_cs61a.txt

**Example 3 — out-of-scope query showing refusal:**

> **Q:** What is the best off-campus apartment near Berkeley?
>
> **A:** I don't have enough information in the provided documents to answer that question.
>
> **Retrieved from:** rmp_josh_hug_cs61b.txt • CS61A_reddit_thread.txt • CS_tips_reddit_thread.txt

The system correctly declined rather than generating a plausible-sounding answer from general knowledge. The retrieved chunks were unrelated to off-campus housing (they happened to be the closest vectors by cosine similarity), but the LLM correctly identified that none of them contained relevant information.

---

## Query Interface

**Interface type:** Gradio web app (`app.py`), served at `http://localhost:7860`.

**To run:**
```bash
source .venv/bin/activate
python app.py
```

**Input fields:**
- **Your question** — a free-text box where users type any question about UC Berkeley CS professors or courses. Pressing Enter or clicking "Ask" submits the query.

**Output fields:**
- **Answer** — the LLM-generated response, grounded in the retrieved chunks, with inline source citations in the format `(source: filename.txt)`.
- **Retrieved from** — a bulleted list of the unique source filenames that were retrieved for the query.

**Pre-loaded example queries** (clickable in the UI):
- "Is CS61A harder to take in the summer compared to the regular semester?"
- "What do students say about Dan Garcia's grading practices in CS61C?"
- "What strategies help students pass CS70 without a strong math background?"
- "What do students say about Josh Hug's CS61B lectures?"
- "How should I prepare for CS61A before the semester starts?"

**Sample interaction transcript:**

```
User: What strategies do students recommend for passing CS70 without a strong math background?

Answer: According to the provided excerpts, students recommend the following strategies for
passing CS70 without a strong math background:
- Prioritizing the class and spending a lot of time on it (source: CS70_reddit_thread.txt)
- Reading every note thoroughly, possibly multiple times (source: CS70_reddit_thread.txt)
- Being willing to "grind" in order to achieve a higher grade (source: CS70_reddit_thread.txt)
It's also mentioned that the structure of the course, with its fast pace, can be a significant
challenge, rather than the content itself (source: CS70_reddit_thread.txt).

Retrieved from:
• CS70_reddit_thread.txt
• CS61A_difficulty_reddit_thread.txt
• CS_tips_reddit_thread.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is CS61A harder to take in the summer compared to the regular semester? | Yes — "unbelievably fast-paced," twice the speed of fall/spring, exam averages ~30–40% | States summer is "unbelievably fast-paced" but declines to make a direct comparison to fall/spring | Relevant | Partially accurate |
| 2 | What do students say about Dan Garcia's grading practices in CS61C? | Mixed — "A's for All" policy described as a scam, grade dropped A→B+ after exam, averages below 65% target | "I don't have enough information in the provided documents to answer that question." | Off-target | Inaccurate |
| 3 | What strategies do students recommend for passing CS70 without a strong math background? | Read notes until you can recreate proofs; grind practice exams a month before each test; attend discussions | Prioritize the class; read every note thoroughly; be willing to grind | Relevant | Partially accurate |
| 4 | What do students say about Josh Hug's lectures in CS61B? | Highly praised — "amazing," "hilarious," "inspirational," curriculum is "perfection" | Amazing professor with a sense of humor who teaches well; lectures are enjoyable; videos are cool | Relevant | Accurate |
| 5 | How do students recommend preparing for CS61A before the semester starts? | Watch DeNero's videos on cs61a.org; practice environment diagrams on tutor.cs61a.org; learn intro Python | Watch videos on cs61a.org; practice environment diagrams on tutor.cs61a.org | Relevant | Partially accurate |

---

## Failure Case Analysis

**Question that failed:** "What do students say about Dan Garcia's grading practices in CS61C?"

**What the system returned:** "I don't have enough information in the provided documents to answer that question."

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure. The document `rmp_dan_garcia_cs61c.txt` contains exactly the information needed: one review calls the "A's for All" policy "a scam," another describes a grade dropping from A to B+ after the final, and a third specifically mentions "shady grading practices (delaying grade distribution releases, lying about said distributions)." However, only 1 of the 5 retrieved chunks came from `rmp_dan_garcia_cs61c.txt` — and it was the positive review calling Garcia an "absolute gem," not any of the grading-critical ones.

The underlying cause is that the query "Dan Garcia's grading practices in CS61C" shares the generic semantic structure of any professor RMP review. The embedding model produces similar vectors for "Dan Garcia grading CS61C" and "Professor X grading course Y" because the structural pattern is the same. With only 5 Garcia-specific chunks in a 57-chunk collection, 4 of the 5 top results were pulled from other professors' reviews (CS70 and CS61A), none of which were relevant. The one Garcia chunk that was retrieved happened to be the furthest semantically from the grading-criticism reviews.

**What you would change to fix it:** Two approaches. First, increase k from 5 to 8–10 to give more Garcia chunks a chance to enter the retrieved set. Second, add a metadata filter on source filename for queries that name a specific professor or course (e.g., if the query mentions "Garcia" or "CS61C," restrict retrieval to `rmp_dan_garcia_cs61c.txt` chunks first). ChromaDB supports `where` filters that would enable this.

---

## Spec Reflection

**One way the spec helped during implementation:** The Chunking Strategy section in `planning.md` — specifying 500 characters, 50-character overlap, and the reasoning that each review should stay in one chunk — was directly usable as an implementation spec. Rather than experimenting with chunk sizes after building the pipeline, the decision was already made and justified. When `ingest.py` was written, the parameters were simply plugged in. This saved significant debugging time and made the code reviewable against a stated rationale.

**One way implementation diverged from the spec, and why:** The spec did not anticipate the need to clean `Tags:` lines from RMP documents. The planning.md described cleaning as "remove navigation text, ads, boilerplate," and `Tags:` labels didn't register as a problem until the first batch of chunks was printed and the output included chunks like `"Tags: Tough grader, Amazing lectures"` — 36 characters of keyword metadata that would pollute the vector store with useless embeddings. A `re.sub` cleaning step was added to remove these lines. The spec was updated accordingly. This is a good example of why the checkpoint instruction to "print 5 representative chunks and inspect them" exists.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline**

- *What I gave the AI:* The Documents section and Chunking Strategy section from `planning.md`, specifying 10 `.txt` files, 500-character chunk size, 50-character overlap, and `RecursiveCharacterTextSplitter`.
- *What it produced:* A working `ingest.py` that loads all `.txt` files, cleans them, and splits using `RecursiveCharacterTextSplitter` with the specified parameters. Each chunk was stored as a dict with `text`, `source`, and `chunk_id` fields.
- *What I changed or overrode:* After running the script and inspecting the output, I found 8 junk chunks: 4 were `Tags:` lines from RMP files (e.g., "Tags: Tough grader, Amazing lectures"), and others were short noise like "u/Traditional_Yam_154: Thanks!" The AI-generated code only filtered empty strings. I added a `re.sub` to strip `Tags:` lines during cleaning and changed the filter from `if split.strip()` to `if len(split.strip()) >= 50`.

**Instance 2 — Embedding, retrieval, and generation pipeline**

- *What I gave the AI:* The Retrieval Approach section and Architecture diagram from `planning.md`, plus the requirement that responses must be grounded and include source citations.
- *What it produced:* Working `embed.py` (ChromaDB index build + `retrieve()` function using `all-MiniLM-L6-v2`) and `query.py` (Groq integration with a grounding system prompt).
- *What I changed or overrode:* The initial system prompt said "try to use the provided documents" — too weak to enforce grounding. I rewrote it to be explicit: "Answer the question using ONLY the document excerpts provided below. Do not use any outside knowledge." I verified grounding by testing an out-of-scope question ("best off-campus apartment near Berkeley") and confirmed the system returned a clean refusal rather than hallucinating an answer. I also changed `temperature` from the default (1.0) to 0.2 to make responses more consistent and less prone to paraphrasing away from the source text.
