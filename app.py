from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional
from env.models import Action, Observation, Reward, State
from env.negotiation_env import NegotiationOpenEnv
from tasks.tasks import TASKS

app = FastAPI(title="NegotiationOpenEnv API")

# Global singleton representing the environment (for demonstration / hackathon)
# In production, this would be session-based.
env: Optional[NegotiationOpenEnv] = None

@app.get("/health")
def health():
    return {"status": "healthy", "version": "0.1.0"}

@app.post("/reset", response_model=Observation)
def reset(difficulty: str = "easy"):
    global env
    if difficulty not in TASKS:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty. Must be one of: {list(TASKS.keys())}")
    
    config = TASKS[difficulty]
    env = NegotiationOpenEnv(config)
    return env.reset()

@app.post("/step")
def step(action: Action):
    global env
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state", response_model=State)
def get_state():
    global env
    if env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized.")
    return env.state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
