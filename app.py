from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from pipeline import run_research_pipeline_stream

app = FastAPI()


class SearchRequest(BaseModel):
  topic: str

@app.post("/research")
def research(request: SearchRequest):
  return StreamingResponse(run_research_pipeline_stream(request.topic), media_type="text/event-stream")