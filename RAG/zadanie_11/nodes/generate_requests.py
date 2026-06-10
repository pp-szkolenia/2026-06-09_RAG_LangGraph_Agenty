from qdrant_client import models as qdrant_models

from config import llm, METADATA_JSON
from models import QdrantCondition, QdrantFilter, build_retrieval_request_model
from prompts import retrieval_assistant_prompt


def get_top_k_range(analysis_level: str) -> tuple[int, int, int]:
    """Returns (popular_topic, standard_topic, specific_topic) top_k values."""
    ranges = {
        "basic": (5, 3, 2),
        "medium": (15, 10, 5),
        "deep": (30, 20, 10),
    }
    if analysis_level not in ranges:
        raise ValueError(f"Unknown analysis_level: {analysis_level!r}")
    return ranges[analysis_level]


def to_qdrant_filter(qf: QdrantFilter) -> qdrant_models.Filter | None:
    if not (qf.must or qf.should or qf.must_not):
        return None

    def to_cond(c: QdrantCondition) -> qdrant_models.FieldCondition:
        return qdrant_models.FieldCondition(key=c.key, match=qdrant_models.MatchValue(value=c.value))

    return qdrant_models.Filter(
        must=[to_cond(c) for c in qf.must] or None,
        should=[to_cond(c) for c in qf.should] or None,
        must_not=[to_cond(c) for c in qf.must_not] or None,
    )


def generate_requests_node(state: dict) -> dict:
    analysis_level = state.get("analysis_level", "medium")
    debug = state.get("debug", False)

    top_k_popular, top_k_standard, top_k_specific = get_top_k_range(analysis_level)
    model_cls = build_retrieval_request_model(top_k_popular, top_k_standard, top_k_specific, METADATA_JSON)

    chain = retrieval_assistant_prompt | llm.with_structured_output(model_cls)
    result = chain.invoke({"question": state["user_query"]})

    requests = [
        {
            "query_text": req.query_text,
            "query_filters": to_qdrant_filter(req.query_filters),
            "top_k": req.top_k,
        }
        for req in result.requests
    ]

    if debug:
        print(f"[generate_requests] Generated {len(requests)} retrieval request(s):")
        for i, req in enumerate(requests, 1):
            print(f"  {i}. top_k={req['top_k']} | {req['query_text']}")
            if req["query_filters"]:
                print(f"     filters: {req['query_filters']}")

    return {"retrieval_requests": requests}
