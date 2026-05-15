from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import run_agent

app = FastAPI(
    title="EduNexus AI Agent API",
    description="API for interacting with the EduNexus LangGraph agent",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    try:
        result = await run_agent(request.query)
        return QueryResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
