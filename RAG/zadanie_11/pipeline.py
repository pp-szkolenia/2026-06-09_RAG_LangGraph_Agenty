from langgraph.graph import END, START, StateGraph

from config import retriever
from nodes import (
    expand_neighbors_node,
    execute_retrieval_node,
    filter_irrelevant_node,
    generate_answer_node,
    generate_requests_node,
    group_results_node,
    retrieve_chapters_node,
)
from state import PipelineState


def build_graph():
    builder = StateGraph(PipelineState)

    builder.add_node("generate_requests", generate_requests_node)
    builder.add_node("execute_retrieval", execute_retrieval_node)
    builder.add_node("expand_neighbors", expand_neighbors_node)
    builder.add_node("filter_irrelevant", filter_irrelevant_node)
    builder.add_node("group_results", group_results_node)
    builder.add_node("retrieve_chapters", retrieve_chapters_node)
    builder.add_node("generate_answer", generate_answer_node)

    builder.add_edge(START, "generate_requests")
    builder.add_edge("generate_requests", "execute_retrieval")
    builder.add_edge("execute_retrieval", "expand_neighbors")
    builder.add_edge("expand_neighbors", "filter_irrelevant")
    builder.add_edge("filter_irrelevant", "group_results")
    builder.add_edge("group_results", "retrieve_chapters")
    builder.add_edge("retrieve_chapters", "generate_answer")
    builder.add_edge("generate_answer", END)

    return builder.compile()


def run_query(
    user_query: str,
    analysis_level: str = "medium",
    debug: bool = False,
) -> list[dict]:
    graph = build_graph()
    final_state = graph.invoke(
        {
            "user_query": user_query,
            "analysis_level": analysis_level,
            "debug": debug,
        },
        config={"configurable": {"retriever": retriever}},
    )
    return final_state["answers"]
