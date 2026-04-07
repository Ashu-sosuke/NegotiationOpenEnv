from typing import List, Dict, Any, Tuple
from env.models import TaskConfig

def evaluate_negotiation(history: List[Dict[str, Any]], config: TaskConfig) -> float:
    """Evaluates the final negotiation history and returns a score 0.0-1.0."""
    if not history:
        return 0.0

    last_item = history[-1]
    is_deal_reached = (last_item.get("intent") == "ACCEPT" or 
                      (last_item.get("sender") == "SELLER" and last_item.get("intent") == "ACCEPT"))

    if not is_deal_reached:
        return 0.0

    # 1. Base Score for reaching an agreement (0.5)
    score = 0.5

    # 2. Price Efficiency (up to 0.3)
    # How much did the buyer save?
    # Max savings = Starting Seller Price - Seller Min Accept
    final_price = last_item.get("price", config.starting_seller_price)
    total_potential_savings = config.starting_seller_price - config.seller_min_accept
    actual_savings = config.starting_seller_price - final_price
    
    if total_potential_savings > 0:
        price_efficiency = (actual_savings / total_potential_savings) * 0.3
        score += max(0, min(0.3, price_efficiency))

    # 3. Terms Fulfillment (up to 0.2)
    # Check if required terms for the task were present in the final agreed history
    if not config.required_terms:
        score += 0.2 # Automatically get these points if no terms required
    else:
        # Check all buyer moves for terms
        buyer_terms_found = set()
        for h in history:
            if h["sender"] == "BUYER" and h.get("terms"):
                for t in config.required_terms:
                    if t in h["terms"]:
                        buyer_terms_found.add(t)
        
        terms_fulfillment = (len(buyer_terms_found) / len(config.required_terms)) * 0.2
        score += terms_fulfillment

    return round(min(score, 1.0), 3)
