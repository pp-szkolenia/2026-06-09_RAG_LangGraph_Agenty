from typing import Any
from typing_extensions import TypedDict


class PipelineState(TypedDict, total=False):
    user_query: str
    analysis_level: str
    debug: bool
    retrieval_requests: list[dict[str, Any]]
    retrieved_verses: list[dict]
    expanded_verses: list[dict]
    relevant_verses: list[dict]
    grouped_verses: dict[str, list]
    retrieved_chapters: dict[str, list]
    answers: list[dict]
