from qdrant_client import models as qdrant_models

from config import client, COLLECTION_NAME


def retrieve_chapters_node(state: dict) -> dict:
    debug = state.get("debug", False)
    grouped_verses = state["grouped_verses"]

    chapter_cache: dict[str, str] = {}
    retrieved_chapters: dict[str, list] = {}

    for category, verses in grouped_verses.items():
        unique_chapters = list({(v["book_name"], v["chapter"]) for v in verses})
        category_chapters = []

        for book_name, chapter_no in unique_chapters:
            cache_key = f"{book_name} {chapter_no}"

            if cache_key not in chapter_cache:
                points, _ = client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=qdrant_models.Filter(
                        must=[
                            qdrant_models.FieldCondition(
                                key="metadata.book_name",
                                match=qdrant_models.MatchValue(value=book_name),
                            ),
                            qdrant_models.FieldCondition(
                                key="metadata.chapter",
                                match=qdrant_models.MatchValue(value=chapter_no),
                            ),
                        ]
                    ),
                    with_payload=True,
                    with_vectors=False,
                    limit=1000,
                )
                chapter_text = "\n".join(
                    f"{p.payload['metadata']['verse']}: {p.payload['page_content']}"
                    for p in sorted(points, key=lambda p: p.payload["metadata"]["verse"])
                )
                chapter_cache[cache_key] = chapter_text

            category_chapters.append({
                "chapter_id": cache_key,
                "book_name": book_name,
                "chapter_number": chapter_no,
                "chapter_text": chapter_cache[cache_key],
            })

        retrieved_chapters[category] = category_chapters

    if debug:
        print(f"[retrieve_chapters] Fetched {len(chapter_cache)} unique chapter(s) across {len(retrieved_chapters)} categories")

    return {"retrieved_chapters": retrieved_chapters}
