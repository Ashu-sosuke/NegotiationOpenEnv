import os
import json
import requests
import time
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Mandatory Environment Variables as per Hackathon Checklist
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash") # Stable for OpenAI wrapper
HF_TOKEN = os.getenv("HF_TOKEN") # No default as per checklist

# OpenAI-compatible Client Configuration for Gemini
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MAX_RETRIES = 5

def get_agent_action(obs_history: List[Dict], turns_left: int, current_offer: float) -> Dict[str, Any]:
    history_str = "\n".join([f"{h['sender']}: {h['message']} (Price: ${h.get('price', 'N/A')})" for h in obs_history])
    
    prompt = f"""
    You are a smart negotiator acting as the BUYER. 
    Negotiation History:
    {history_str}
    
    Current Opponent Offer: ${current_offer if current_offer else 'N/A'}
    Turns Left: {turns_left}
    
    Respond in JSON:
    {{
        "intent": "OFFER" | "ACCEPT" | "REJECT",
        "price": number,
        "message": "justification",
        "terms": {{}}
    }}
    """
    
    # Retry with exponential backoff for 429 rate limits
    for attempt in range(MAX_RETRIES):
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < MAX_RETRIES - 1:
                wait_time = min(2 ** (attempt + 2), 60)  # 4s, 8s, 16s, 32s, 60s
                print(f"(STEP) Rate limited, retrying in {wait_time}s (attempt {attempt+1}/{MAX_RETRIES})")
                time.sleep(wait_time)
            else:
                raise

def run_task(difficulty: str):
    # Mandatory Log Format: (START)
    print(f"(START) Task: Negotiation-{difficulty.upper()}")
    
    # 1. Reset Environment
    try:
        response = requests.post(f"{API_BASE_URL}/reset?difficulty={difficulty}")
        obs = response.json()
    except Exception as e:
        print(f"Error Resetting: {e}")
        return
    
    done = False
    total_reward = 0.0
    
    while not done:
        # 2. Get Agent Action
        try:
            action_data = get_agent_action(
                obs['history'], 
                obs['turns_left'], 
                obs.get('current_opponent_offer')
            )
            time.sleep(3) # Per-turn rate limit safety
        except Exception as e:
            print(f"Agent Error: {e}")
            break

        # Mandatory Log Format: (STEP)
        print(f"(STEP) Action: {json.dumps(action_data)}")
        
        # 3. Step Environment
        try:
            step_response = requests.post(f"{API_BASE_URL}/step", json=action_data)
            step_data = step_response.json()
        except Exception as e:
            print(f"Server Error: {e}")
            break
        
        obs = step_data['observation']
        total_reward = step_data['reward']['value']
        done = step_data['done']
        
        if done:
            # Mandatory Log Format: (END)
            print(f"(END) Outcome: {step_data['info'].get('reason')} | Score: {total_reward}")
            
if __name__ == "__main__":
    for diff in ["easy", "medium", "hard"]:
        run_task(diff)
        time.sleep(10) # Rate limit safety between tasks
