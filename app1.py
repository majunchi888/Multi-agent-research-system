from fastapi import FastAPI
from pydantic import BaseModel

from pipeline import run_research_pipeline

app = FastAPI()


class SearchRequest(BaseModel):
  topic: str

@app.post("/research")
def research(request: SearchRequest):
  result = run_research_pipeline(request.topic)  
  return {
        "topic": request.topic,
        "search_results": result["search_results"],
        "scraped_content": result["scraped_content"],
        "report": result["report"],
        "feedback": result["feedback"],
    }
