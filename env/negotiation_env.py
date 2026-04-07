import random
from typing import Tuple, Dict, Any, List
from .models import Action, Observation, Reward, State, TaskConfig

class NegotiationOpenEnv:
    def __init__(self, config: TaskConfig):
        self.config = config
        self.reset()

    def reset(self) -> Observation:
        """Resets the environment to the initial state."""
        self._state = State(
            zopa_min=self.config.seller_min_accept,
            zopa_max=self.config.starting_seller_price,
            target_price=self.config.starting_buyer_price,
            opponent_strategy=random.choice(["TOUGH", "FAIR", "SOFT"]),
            step_count=0
        )
        self._history = [
            {
                "sender": "SELLER",
                "price": self.config.starting_seller_price,
                "message": f"Hello! I am selling this for ${self.config.starting_seller_price}. Are you interested?"
            }
        ]
        self._is_done = False
        return self._get_observation()

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """Executes one turn in the negotiation."""
        if self._is_done:
            raise RuntimeError("Episode is already finished. Call reset() to start a new one.")

        self._state.step_count += 1
        
        # 1. Process Agent (Buyer) Action
        self._history.append({
            "sender": "BUYER",
            "price": action.price,
            "terms": action.terms,
            "message": action.message,
            "intent": action.intent
        })

        # 2. Check for Termination (Accept / Reject / Quit / Max Turns)
        reward_val = 0.0
        if action.intent == "ACCEPT":
            if action.price and action.price >= self._state.zopa_min:
                self._is_done = True
                reward_val = self._calculate_final_reward(success=True)
                return self._get_observation(), Reward(value=reward_val), True, {"reason": "deal_reached"}
            else:
                # Agent accepted but provided price is below seller min? 
                # In real world, seller would just be happy, but we'll treat it as a deal.
                self._is_done = True
                reward_val = 1.0 
                return self._get_observation(), Reward(value=reward_val), True, {"reason": "deal_reached_favorable"}

        if action.intent == "QUIT" or self._state.step_count >= self.config.max_turns:
            self._is_done = True
            return self._get_observation(), Reward(value=0.0), True, {"reason": "failed"}

        # 3. Simulate Opponent (Seller) Response
        opponent_action = self._generate_opponent_response(action)
        self._history.append(opponent_action)

        # 4. Calculate Intermediate Reward (Progressive)
        reward_val = self._calculate_step_reward(action)
        
        return self._get_observation(), Reward(value=reward_val), False, {}

    def state(self) -> State:
        """Returns the current internal state."""
        return self._state

    def _get_observation(self) -> Observation:
        """Helper to construct the observation from the current state."""
        last_item = self._history[-1]
        return Observation(
            history=self._history,
            current_opponent_offer=last_item.get("price") if last_item["sender"] == "SELLER" else None,
            current_opponent_terms=last_item.get("terms") if last_item["sender"] == "SELLER" else None,
            sentiment_score=self._calculate_sentiment(),
            turns_left=self.config.max_turns - self._state.step_count,
            is_done=self._is_done
        )

    def _generate_opponent_response(self, agent_action: Action) -> Dict[str, Any]:
        """Heuristic-based opponent logic."""
        current_seller_price = next(h["price"] for h in reversed(self._history[:-1]) if h["sender"] == "SELLER")
        
        # Simple concession logic
        if self._state.opponent_strategy == "TOUGH":
            concession_rate = 0.02
        elif self._state.opponent_strategy == "FAIR":
            concession_rate = 0.05
        else: # SOFT
            concession_rate = 0.10

        new_price = max(self._state.zopa_min, current_seller_price * (1 - concession_rate))
        
        # If agent is very close, just accept
        if agent_action.price and agent_action.price >= new_price:
            return {
                "sender": "SELLER",
                "intent": "ACCEPT",
                "price": agent_action.price,
                "message": "That sounds fair. I accept your offer!"
            }

        return {
            "sender": "SELLER",
            "price": round(new_price, 2),
            "message": f"I can't go that low. How about ${round(new_price, 2)}?"
        }

    def _calculate_step_reward(self, action: Action) -> float:
        """Provides partial signals for training."""
        if not action.price: return 0.0
        
        # Reward for moving closer to the midpoint of ZOPA
        # Closer to seller price is bad for buyer, so we reward low prices that are still 'realistic'
        midpoint = (self._state.zopa_min + self._state.zopa_max) / 2
        dist = abs(action.price - midpoint)
        return max(0.0, 0.1 * (1.0 - dist/self._state.zopa_max))

    def _calculate_final_reward(self, success: bool) -> float:
        """Calculates final 0.0-1.0 score based on deal quality."""
        if not success: return 0.0
        
        last_price = self._history[-1].get("price", self.config.starting_seller_price)
        # Efficiency: How much of the 'saving' did the buyer get?
        # Saving = StartingSellerPrice - FinalPrice
        # MaxSaving = StartingSellerPrice - SellerMinAccept
        total_possible_saving = self.config.starting_seller_price - self._state.zopa_min
        actual_saving = self.config.starting_seller_price - last_price
        
        score = actual_saving / total_possible_saving if total_possible_saving > 0 else 1.0
        return min(max(score, 0.0), 1.0)

    def _calculate_sentiment(self) -> float:
        """Internal heuristic for sentiment."""
        return max(0.0, 1.0 - (self._state.step_count / self.config.max_turns))
