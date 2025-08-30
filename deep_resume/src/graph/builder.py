from langgraph.graph import StateGraph, START, END
from .types import State
from .nodes import reviewer_node, background_investigator_node, analyst_node, researcher_node, coordinator_node

def _build_base_graph():
    """Build and return the base state graph with all nodes and edges."""
    builder = StateGraph(State)
    builder.add_edge(START, "reviewer")
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("background_investigator", background_investigator_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("researcher", researcher_node)
    builder.add_edge("coordinator", END)
    return builder

def build_graph():
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_base_graph()
    return builder.compile()

graph = build_graph()