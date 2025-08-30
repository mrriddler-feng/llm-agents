from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ExperienceType(str, Enum):
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"
    AWARD = "award"

class Experience(BaseModel):
    description: str = Field(..., description="Specify exactly what key data to collect")
    supplement: str = Field(..., description="Specify what supplement data to collect")
    begin_time: Optional[str] = Field(
        default=None, description="The experience begin time"
    )
    end_time: Optional[str] = Field(
        default=None, description="The experience end time"
    )
    experience_type: ExperienceType = Field(..., description="Indicates the nature of the experience")

class Resume(BaseModel):
    locale: str = Field(..., description="e.g. 'en-US' or 'zh-CN', based on the user's language")
    experiences: List[Experience] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "locale": "en",
                    "experiences": [
                        {
                            "begin_time": "2015.09",
                            "end_time": "2018.09",
                            "description": "NYU",
                            "experience_type": "professional",
                        }
                    ],
                }
            ]
        }