from textwrap import dedent

from config import llm
from models import AspectResponse
from prompts import generate_answer_prompt


generate_chain = generate_answer_prompt | llm.with_structured_output(AspectResponse)


def build_context(aspect_verses: list[dict], aspect_chapters: list[dict]) -> str:
    context = ""
    for chapter in sorted(aspect_chapters, key=lambda c: c["book_name"]):
        verses_in_chapter = [
            v for v in aspect_verses
            if v["book_name"] == chapter["book_name"] and v["chapter"] == chapter["chapter_number"]
        ]
        verses_str = "".join(
            f"Numer wersetu: {v['verse']} | Treść wersetu: {v['verse_text']}\n"
            for v in verses_in_chapter
        )
        context += dedent(f"""
            Księga: {chapter['book_name']} | Numer rozdziału: {chapter['chapter_number']}
            Wersety:
            {verses_str}
            Treść całego rozdziału:
            {chapter['chapter_text']}
            =========================================
        """)
    return context


def generate_answer_node(state: dict) -> dict:
    debug = state.get("debug", False)
    user_query = state["user_query"]
    grouped_verses = state["grouped_verses"]
    retrieved_chapters = state["retrieved_chapters"]

    aspects = list(grouped_verses.keys())
    inputs = [
        {
            "user_query": user_query,
            "aspect": aspect,
            "context": build_context(
                aspect_verses=grouped_verses[aspect],
                aspect_chapters=retrieved_chapters[aspect],
            ),
        }
        for aspect in aspects
    ]

    responses = generate_chain.batch(inputs, config={"max_concurrency": 8})
    answers = [resp.model_dump() for resp in responses]

    if debug:
        print(f"[generate_answer] Generated answers for {len(answers)} aspect(s):")
        for ans in answers:
            print(f"  - {ans['aspect_name']} ({len(ans['paragraphs'])} paragraph(s))")

    return {"answers": answers}
