from typing import List, Optional
from pydantic import BaseModel, Field
from .report_model import Report
from .resume_model import Experience

class Question(BaseModel):
    description: str = Field(..., description="")
    answered: bool = Field(default=False, description="")
    observations: List[str] = Field(default_factory=list)
    iterations: int = Field(default=0, description="The number of iterations for the analyst to answer the question")
    report: Optional[Report] = Field(default=None, description="The report to the question")

class BackgroundInvestigation(BaseModel):
    background_search_description: str = Field(..., description="")
    searched: bool = Field(default=False, description="")
    background_investigation_context: List[str] = Field(default_factory=list, description="Background investigation context for answering questions")

class Topic(BaseModel):
    background_investigation: BackgroundInvestigation = Field(default_factory=BackgroundInvestigation)
    experience: Experience = Field(default_factory=Experience)
    questions: List[Question] = Field(default_factory=list, description="A list of questions to be answered")