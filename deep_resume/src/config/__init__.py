from .tools import SEARCH_MAX_RESULTS, SELECTED_SEARCH_ENGINE, SearchEngine
from .loader import load_yaml_config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

__all__ = [
    # Other configurations
    "SEARCH_MAX_RESULTS",
    "SELECTED_SEARCH_ENGINE",
    "SearchEngine",
]