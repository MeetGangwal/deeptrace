from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schemas import FrameAnalysisRequest, FrameAnalysisResponse
from inference_service import InferenceService

app = FastAPI(title="DeepTrace AI Engine", version="1.0")

# Allow requests originating from any Chrome Extension (chrome-extension://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = None

@app.on_event("startup")
def load_service():
    global service
    service = InferenceService()

@app.get("/health")
def health_check():
    return {"status": "online", "engine": "Apple M5 Metal Performance Shaders"}

@app.post("/analyze-frame", response_model=FrameAnalysisResponse)
def analyze_frame(payload: FrameAnalysisRequest):
    result = service.analyze_frame(payload.image_base64, payload.timestamp)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)