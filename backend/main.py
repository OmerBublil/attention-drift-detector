from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from data_store import save_event

app = FastAPI()

# Allow frontend (Vite/React) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for reading task events
class SegmentEvent(BaseModel):
    session_id: str
    segment_id: int
    text_length: int
    reading_time_ms: float

# Data model for reaction task events
class ReactionEvent(BaseModel):
    session_id: str
    question_index: int
    reaction_time_ms: float
    is_correct: bool

@app.get("/health")
def health_check():
    """
    Simple health check to verify that backend is running.
    """
    return {"status": "ok"}

@app.post("/segment")
def receive_segment(event: SegmentEvent):
    """
    Receive a reading segment event from frontend.
    Save event to data.json via data_store.
    """
    save_event(event.dict())
    return {"status": "saved"}

@app.post("/reaction")
def receive_reaction(event: ReactionEvent):
    """
    Receive a reaction-time event from frontend.
    Save event to data.json via data_store.
    """
    save_event(event.dict())
    return {"status": "saved"}
