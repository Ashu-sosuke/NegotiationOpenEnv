import os
import json
import requests
import time
from typing import Dict, Any, List
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the new Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
# Using gemini-2.5-flash instead of deprecated 1.5
MODEL_ID = "gemini-2.5-flash"

def get_agent_action(obs_history: List[Dict], turns_left: int, current_offer: float) -> Dict[str, Any]:
    history_str = "\n".join([f"{h['sender']}: {h['message']} (Price: ${h.get('price', 'N/A')})" for h in obs_history])
    
    prompt = f"""
    You are a smart negotiator acting as the BUYER. 
    Your goal is to get the best deal (lowest price) while maintaining a professional relationship.
    
    Negotiation History:
    {history_str}
    
    Current Opponent Offer: ${current_offer if current_offer else 'N/A'}
    Turns Left: {turns_left}
    
    Respond with a JSON object containing:
    - "intent": "OFFER", "ACCEPT", or "REJECT"
    - "price": your proposed price (number)
    - "message": your natural language message
    - "terms": {{}} (any additional terms)
    
    JSON Only:
    """
    
    # Use the new generate_content with JSON response mode
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    return json.loads(response.text)

def run_task(difficulty: str) -> float:
    print(f"\n--- Starting Gemini Task ({MODEL_ID}): {difficulty.upper()} ---")
    
    # 1. Reset Environment
    try:
        response = requests.post(f"{API_BASE_URL}/reset?difficulty={difficulty}")
        obs = response.json()
    except Exception as e:
        print(f"Server Reset Error: {e}")
        return 0.0
    
    done = False
    total_reward = 0.0
    
    while not done:
        # 2. Get Agent Action from Gemini
        try:
            action_data = get_agent_action(
                obs['history'], 
                obs['turns_left'], 
                obs.get('current_opponent_offer')
            )
        except Exception as e:
            print(f"Gemini API Error: {e}")
            break

        print(f"Agent ({difficulty}): {action_data['message']} | Price: ${action_data.get('price')}")
        
        # 3. Step Environment
        try:
            step_response = requests.post(f"{API_BASE_URL}/step", json=action_data)
            step_data = step_response.json()
        except Exception as e:
            print(f"Server Step Error: {e}")
            break
        
        obs = step_data['observation']
        total_reward = step_data['reward']['value'] # Using terminal reward for final score
        done = step_data['done']
        
        if done:
            print(f"Negotiation Ended. Reason: {step_data['info'].get('reason')}")
            
    return total_reward

if __name__ == "__main__":
    # Ensure uvicorn app:app (or equivalent server) is running.
    results = {}
    for diff in ["easy", "medium", "hard"]:
        try:
            score = run_task(diff)
            results[diff] = score
        except Exception as e:
            print(f"Fatal Error running task {diff}: {e}")
            results[diff] = 0.0
            
    print("\n" + "="*40)
    print("GEMINI BASELINE EVALUATION")
    print("="*40)
    for diff, score in results.items():
        print(f"{diff.capitalize()}: {round(score, 3)}")
    print("="*40)
