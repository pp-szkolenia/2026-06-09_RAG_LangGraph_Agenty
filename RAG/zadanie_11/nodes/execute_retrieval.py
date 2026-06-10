from langchain_core.runnables import RunnableConfig


def execute_retrieval_node(state: dict, config: RunnableConfig) -> dict:
    debug = state.get("debug", False)

    retriever = config["configurable"]["retriever"]

    all_docs = []
    for req in state["retrieval_requests"]:
        search_kwargs = {"k": req["top_k"]}
        if req["query_filters"] is not None:
            search_kwargs["filter"] = req["query_filters"]

        docs = retriever.invoke(
            req["query_text"],
            config={"configurable": {"search_kwargs": search_kwargs}},
        )
        all_docs.extend(docs)

    seen: set[tuple] = set()
    unique_verses: list[dict] = []
    for doc in all_docs:
        key = (doc.metadata.get("book_name"), doc.metadata.get("chapter"), doc.metadata.get("verse"))
        if key not in seen:
            seen.add(key)
            unique_verses.append({"verse_text": doc.page_content} | doc.metadata)

    if debug:
        print(f"[execute_retrieval] {len(unique_verses)} unique verses (from {len(all_docs)} total hits)")

    return {"retrieved_verses": unique_verses}
