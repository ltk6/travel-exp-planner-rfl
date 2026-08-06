from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class N5UserInput(BaseModel):
    text: Optional[str] = ""
    tags: List[str] = Field(default_factory=list)
    img_desc: Optional[str] = ""

class N5LocationMetadata(BaseModel):
    name: Optional[str] = ""
    description: Optional[str] = ""
    tags: List[str] = Field(default_factory=list)

class N5LocationItem(BaseModel):
    location_id: str
    metadata: Optional[N5LocationMetadata] = None

class N5GenerateInput(BaseModel):
    user: N5UserInput = Field(default_factory=N5UserInput)
    locations: List[N5LocationItem] = Field(default_factory=list)
