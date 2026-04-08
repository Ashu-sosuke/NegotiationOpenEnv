from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
from env.models import Action, Observation, Reward, State
from env.negotiation_env import NegotiationOpenEnv
from tasks.tasks import TASKS

app = FastAPI(title="NegotiationOpenEnv API")

# Global singleton representing the environment
env: Optional[NegotiationOpenEnv] = None

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NegotiationOpenEnv - Meta Hackathon</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Outfit', sans-serif; background-color: #0f172a; color: #f8fafc; }
            .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
            .gradient-text { background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            .btn-primary { background: linear-gradient(135deg, #0ea5e9, #6366f1); transition: all 0.3s ease; }
            .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
        </style>
    </head>
    <body class="min-h-screen flex flex-col items-center justify-center p-6 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-900 to-slate-900">
        <div class="max-w-4xl w-full glass rounded-3xl p-8 md:p-12 shadow-2xl text-center">
            <div class="mb-6 inline-block px-4 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium">
                🚀 Meta Hackathon Submission
            </div>
            <h1 class="text-5xl md:text-7xl font-bold mb-6 tracking-tight">
                Negotiation<span class="gradient-text">OpenEnv</span>
            </h1>
            <p class="text-lg md:text-xl text-slate-400 mb-10 leading-relaxed max-w-2xl mx-auto">
                The first standardized benchmark for training AI agents in complex, multi-turn commercial negotiation. 
                Evaluate price anchoring, concession dynamics, andrapport building in real-time.
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div class="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
                    <div class="text-3xl mb-2">📸</div>
                    <h3 class="font-semibold mb-1">Easy</h3>
                    <p class="text-xs text-slate-500">Vintage Camera Swap</p>
                </div>
                <div class="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
                    <div class="text-3xl mb-2">🍱</div>
                    <h3 class="font-semibold mb-1">Medium</h3>
                    <p class="text-xs text-slate-500">Event Catering Bundle</p>
                </div>
                <div class="p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
                    <div class="text-3xl mb-2">🖥️</div>
                    <h3 class="font-semibold mb-1">Hard</h3>
                    <p class="text-xs text-slate-500">B2B Server Procurement</p>
                </div>
            </div>

            <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                <a href="/docs" class="btn-primary px-8 py-4 rounded-xl font-bold text-white shadow-lg w-full sm:w-auto">
                    Explore API Docs
                </a>
                <a href="https://huggingface.co/spaces/AshuBharti/NegotiationOpenEnv" target="_blank" class="px-8 py-4 rounded-xl font-bold bg-slate-800 border border-slate-700 hover:bg-slate-700 transition-all w-full sm:w-auto">
                    View Space
                </a>
            </div>

            <div class="mt-12 pt-8 border-t border-slate-700/50 flex flex-wrap justify-center gap-8 text-sm text-slate-500">
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    API Status: Online
                </div>
                <div>v0.1.0</div>
                <div>Created by AshuBharti</div>
            </div>
        </div>
    </body>
    </html>
    """

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

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
