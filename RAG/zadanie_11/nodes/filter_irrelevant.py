from config import llm
from models import VerseRelevance
from prompts import filter_prompt


filter_chain = filter_prompt | llm.with_structured_output(VerseRelevance).with_retry(
    stop_after_attempt=5, wait_exponential_jitter=True
)


def filter_irrelevant_node(state: dict) -> dict:
    debug = state.get("debug", False)
    user_query = state["user_query"]
    verses = state["expanded_verses"]

    inputs = [
        {"user_query": user_query, "bible_quote": v["context_text"]}
        for v in verses
    ]

    responses = filter_chain.batch(inputs, config={"max_concurrency": 24})

    relevant_verses, irrelevant_verses = [], []
    for verse, resp in zip(verses, responses):
        if resp.is_relevant:
            relevant_verses.append({**verse, "why_relevant": resp.reasoning})
        else:
            irrelevant_verses.append({**verse, "why_irrelevant": resp.reasoning})

    if debug:
        print(f"[filter_irrelevant] Relevant: {len(relevant_verses)} | Filtered out: {len(irrelevant_verses)}")

    return {"relevant_verses": relevant_verses}
