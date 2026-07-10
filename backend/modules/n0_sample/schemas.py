from typing import Any
from pydantic import BaseModel, Field


class N0SampleInput(BaseModel):
    text: str = Field(default="", description="Sample input text.")
    tags: list[str] = Field(default_factory=list, description="Sample input list of tags.")

class N0SampleData(BaseModel):
    text: str | None = ""
    tags: list[str] = Field(default_factory=list)

class N0SampleMetadata(BaseModel):
    module: str = "n0_sample"
    latency_ms: float = 0.0

class N0SampleOutput(BaseModel):
    data: N0SampleData = Field(default_factory=N0SampleData)
    metadata: N0SampleMetadata = Field(default_factory=N0SampleMetadata)
