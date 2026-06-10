from config import client, COLLECTION_NAME


def expand_verse_context(verse: dict) -> dict:
    verse_id = verse["_id"]
    chapter = verse["chapter"]
    book_name = verse["book_name"]

    candidate_ids = [id_ for id_ in [verse_id - 1, verse_id, verse_id + 1] if id_ >= 0]

    points = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=candidate_ids,
        with_payload=True,
        with_vectors=False,
    )

    same_chapter = sorted(
        [
            p for p in points
            if p.payload["metadata"]["chapter"] == chapter
            and p.payload["metadata"]["book_name"] == book_name
        ],
        key=lambda p: p.payload["metadata"]["verse"],
    )

    verse_numbers = [p.payload["metadata"]["verse"] for p in same_chapter]
    combined_text = " ".join(p.payload["page_content"] for p in same_chapter)

    return {
        **verse,
        "context_text": combined_text,
        "context_verse_start": min(verse_numbers),
        "context_verse_stop": max(verse_numbers),
    }


def expand_neighbors_node(state: dict) -> dict:
    debug = state.get("debug", False)

    expanded = [expand_verse_context(v) for v in state["retrieved_verses"]]

    if debug:
        print(f"[expand_neighbors] Expanded context for {len(expanded)} verses")

    return {"expanded_verses": expanded}
