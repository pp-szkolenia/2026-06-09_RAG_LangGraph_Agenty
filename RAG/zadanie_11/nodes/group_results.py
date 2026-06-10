import json

from config import llm
from models import GroupedVerses
from prompts import group_verses_prompt


group_chain = group_verses_prompt | llm.with_structured_output(GroupedVerses)


def group_results_node(state: dict) -> dict:
    debug = state.get("debug", False)
    user_query = state["user_query"]
    relevant_verses = state["relevant_verses"]

    grouping_input = [
        {"id": v["_id"], "text": v["context_text"]}
        for v in relevant_verses
    ]

    result = group_chain.invoke({
        "user_query": user_query,
        "verses_json": json.dumps(grouping_input, ensure_ascii=False),
    })

    verse_lookup = {v["_id"]: v for v in relevant_verses}
    grouped_verses = {
        entry.category_name: [
            verse_lookup[vid] for vid in entry.verse_ids if vid in verse_lookup
        ]
        for entry in result.categories
    }

    if debug:
        print(f"[group_results] {len(relevant_verses)} verses → {len(grouped_verses)} categories:")
        for name, verses in grouped_verses.items():
            print(f"  - {name} ({len(verses)} verses)")

    return {"grouped_verses": grouped_verses}
