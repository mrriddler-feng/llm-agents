from langgraph.graph import MessagesState
from src.prompts.resume_model import Resume
from src.prompts.topic_model import Topic

class State(MessagesState):

    # Runtime Variables
    locale: str = "zh-CN"
    resume_file_path: str
    resume: Resume | str = None
    topic_list: list[Topic] = []
    topic_idx: int = -1
