from .search import (
    tavily_search_tool,
    duckduckgo_search_tool,
    brave_search_tool,
    arxiv_search_tool,
)

from src.config import SELECTED_SEARCH_ENGINE, SearchEngine

# Map search engine names to their respective tools
search_tool_mappings = {
    SearchEngine.TAVILY.value: tavily_search_tool,
    SearchEngine.DUCKDUCKGO.value: duckduckgo_search_tool,
    SearchEngine.BRAVE_SEARCH.value: brave_search_tool,
    SearchEngine.ARXIV.value: arxiv_search_tool,
}

web_search_tool = search_tool_mappings.get(SELECTED_SEARCH_ENGINE, tavily_search_tool)

__all__ = [
    "crawl_tool",
    "web_search_tool",
    "python_repl_tool",
    "VolcengineTTS",
]
