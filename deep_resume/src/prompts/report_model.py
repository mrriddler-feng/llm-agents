from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionType(str, Enum):
    YESORNO = "yesorno"
    NUMERIC = "numeric"
    DEFAULT = "default"

class Answer(BaseModel):
    question_type: QuestionType = Field(..., description="Question classification")
    answer: Optional[str] = Field(
        default=None, description="The answer result"
    )

class Step(BaseModel):
    need_web_search: bool = Field(default=False, description="Indicates if need to search")
    title: str = Field(..., description="")
    description: str = Field(..., description="Specify exactly what data to collect")

class Report(BaseModel):
    locale: str = Field(..., description="e.g. 'en-US' or 'zh-CN', based on the user's language")
    has_enough_context: bool = Field(default=False, description="Indicates if there is enough context for the report")
    thought: str = Field(..., description="")
    title: str = Field(..., description="")
    steps: List[Step] = Field(default_factory=list)
    answer: Answer = Field(default_factory=Answer)