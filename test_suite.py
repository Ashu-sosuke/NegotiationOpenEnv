import json
from env.negotiation_env import NegotiationOpenEnv
from env.models import Action
from tasks.tasks import TASKS
from tasks.graders import evaluate_negotiation

def test_negotiation(difficulty: str):
    print(f"\n--- Testing Local Environment: {difficulty.upper()} ---")
    config = TASKS[difficulty]
    env = NegotiationOpenEnv(config)
    obs = env.reset()
    
    done = False
    total_reward = 0.0
    
    # Simple Rule-based Agent Strategy:
    # 1. Start at a low price.
    # 2. Concede by 5% each turn until the seller accepts or max_turns reached.
    current_buyer_price = config.starting_buyer_price
    
    while not done:
        action = Action(
            intent="OFFER",
            price=round(current_buyer_price, 2),
            message=f"My counter-offer is ${round(current_buyer_price, 2)}.",
            terms={"note": "local_test"}
        )
        
        # Process Agent move
        obs, reward, done, info = env.step(action)
        total_reward = reward.value
        
        # More aggressive strategy for test verification
        if obs.current_opponent_offer:
            # If within 5 units, just ACCEPT to finish the test
            if abs(current_buyer_price - obs.current_opponent_offer) < 5:
                action = Action(
                    intent="ACCEPT",
                    price=obs.current_opponent_offer,
                    message="I accept your offer!",
                    terms={"note": "local_test_finish"}
                )
                obs, reward, done, info = env.step(action)
                break

            # Faster concession (40% move towards seller)
            current_buyer_price += (obs.current_opponent_offer - current_buyer_price) * 0.4
        
        if done:
            print(f"Outcome: {info.get('reason')} | Final History Length: {len(obs.history)}")
            
    # Final Evaluation (Grading)
    final_score = evaluate_negotiation(obs.history, config)
    print(f"Final Grader Score (0-1.0): {final_score}")
    return final_score

if __name__ == "__main__":
    results = {}
    for diff in ["easy", "medium", "hard"]:
        try:
            score = test_negotiation(diff)
            results[diff] = score
        except Exception as e:
            print(f"Error testing {diff}: {e}")
            
    print("\n" + "="*40)
    print("LOCAL SYSTEM TEST (LOGIC ONLY)")
    print("="*40)
    for k, v in results.items():
        print(f"{k.capitalize()}: {v}")
    print("="*40)
