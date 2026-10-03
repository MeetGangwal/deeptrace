from pydantic import BaseModel
from typing import List, Optional

class RegionBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class FrameAnalysisRequest(BaseModel):
    image_base64: str
    timestamp: Optional[float] = 0.0

class FrameAnalysisResponse(BaseModel):
    status: str
    prediction: str            # "Real" or "Potential Manipulation"
    confidence: float          # e.g., 0.94
    is_fake: bool
    suspicious_region_name: Optional[str] = None
    face_box: Optional[RegionBox] = None
    manipulation_box: Optional[RegionBox] = None
    signals: List[str] = []
    latency_ms: float