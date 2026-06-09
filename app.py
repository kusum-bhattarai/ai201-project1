import gradio as gr
from embed import build_index
from query import ask

# Build the index on startup if it hasn't been built yet
build_index()


def handle_query(question: str):
    if not question.strip():
        return "", ""
    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="The Unofficial Berkeley CS Guide") as demo:
    gr.Markdown("# The Unofficial Berkeley CS Guide")
    gr.Markdown(
        "Ask anything about UC Berkeley CS professors and courses — "
        "exam difficulty, grading, professor style, project workload. "
        "Answers are grounded in real student reviews and Reddit threads."
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. Is CS61A hard to take over the summer?",
                lines=2,
            )
        with gr.Column(scale=1):
            ask_btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)
    sources_box = gr.Textbox(label="Retrieved from", lines=4, interactive=False)

    ask_btn.click(handle_query, inputs=question_box, outputs=[answer_box, sources_box])
    question_box.submit(handle_query, inputs=question_box, outputs=[answer_box, sources_box])

    gr.Examples(
        examples=[
            "Is CS61A harder to take in the summer compared to the regular semester?",
            "What do students say about Dan Garcia's grading practices in CS61C?",
            "What strategies help students pass CS70 without a strong math background?",
            "What do students say about Josh Hug's CS61B lectures?",
            "How should I prepare for CS61A before the semester starts?",
        ],
        inputs=question_box,
    )

if __name__ == "__main__":
    demo.launch()
