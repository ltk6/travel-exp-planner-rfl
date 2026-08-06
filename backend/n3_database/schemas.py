from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# =============================================================================
# LOCATIONS
# =============================================================================

class N3LocationVectors(BaseModel):
    text: Optional[List[float]] = None
    aug_text: Optional[List[float]] = None
    aug_tags: Optional[List[float]] = None
    img_desc: Optional[List[float]] = None

class N3LocationMetadata(BaseModel):
    name: Optional[str] = Field(default="Unnamed Location", description="The user-friendly name of the location.")
    description: Optional[str] = ""
    tags: List[str] = Field(default_factory=list)
    coordinates: Optional[Dict[str, Optional[float]]] = None
    address: Optional[str] = None
    model_config = {"extra": "allow"}

class N3Geo(BaseModel):
    lat: Optional[float] = 0.0
    lng: Optional[float] = 0.0
    model_config = {"extra": "allow"}

class N3LocationModel(BaseModel):
    location_id: str
    vectors: N3LocationVectors = Field(default_factory=N3LocationVectors)
    metadata: N3LocationMetadata = Field(default_factory=N3LocationMetadata)
    geo: Optional[N3Geo] = None
    images: List[str] = Field(default_factory=list)

class N3GetLocationsOutput(BaseModel):
    status: Optional[str] = "success"
    total: Optional[int] = 0
    data: List[N3LocationModel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    

# =============================================================================
# USER AUTH
# =============================================================================

class N3RegisterInput(BaseModel):
    username: str
    password: str

class N3LoginInput(BaseModel):
    username: str
    password: str

class N3AuthOutput(BaseModel):
    status: Optional[str] = ""
    message: Optional[str] = ""
    user_id: Optional[int] = None


# =============================================================================
# RECOMMENDATION HISTORY
# =============================================================================

class N3SaveHistoryInput(BaseModel):
    user_id: int
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    history_id: Optional[int] = None

class N3HistoryItem(BaseModel):
    history_id: Optional[int] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None

class N3GetHistoryOutput(BaseModel):
    status: Optional[str] = "success"
    data: List[N3HistoryItem] = Field(default_factory=list)
