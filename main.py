from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.time_machine import calculate_downstream_impact
from core.group_matcher import match_study_groups

# Creates the FastAPI instance
app = FastAPI(title="Aura Study Graph API", version="1.0")

# Defined request models using Pydantic
class TimeMachineRequest(BaseModel):
    topic_id: str

@app.post("/api/simulation/time-machine")
def run_time_machine(request: TimeMachineRequest):
    """
    Evaluates the downstream GPA impact if a specific topic is missed.
    """
    try:
        result = calculate_downstream_impact(request.topic_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/groups/match")
def get_study_groups():
    """
    Executes K-Means clustering to pair students based on complementary skills.
    """
    try:
        result = match_study_groups()
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/prompts")
def get_agent_guardrails():
    """
    Provides the strict system prompts for Sidney's Gemma 4 models.
    """
    return {
        "AI_Lab_Partner": "You are the AI Lab Partner. You must ONLY provide hints, structural frameworks, and Socratic questions. NEVER output the final answer.",
        "Assignment_Integrity_TA": "You are the Assignment Integrity TA. Cross-reference the student's submission against their completed graph topics. Flag any concepts used that they have not yet learned as potential plagiarism risks."
    }