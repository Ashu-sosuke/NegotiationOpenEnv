from __future__ import annotations
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field

class Action(BaseModel):
    """The structured input an agent provides to the environment."""
    intent: Literal["OFFER", "ACCEPT", "REJECT", "QUIT"] = Field(..., description="The high-level intent of the move.")
    price: Optional[float] = Field(None, description="The proposed price for the item/service.")
    terms: Optional[Dict[str, Any]] = Field(None, description="Optional dictionary of additional terms (e.g., shipping, quantity, delivery_time).")
    message: str = Field(..., description="The natural language message sent along with the structured action.")

class Observation(BaseModel):
    """The structured output the environment returns to the agent."""
    history: List[Dict[str, Any]] = Field(..., description="The full conversation history including offers and messages.")
    current_opponent_offer: Optional[float] = Field(None, description="The most recent price offer from the opponent.")
    current_opponent_terms: Optional[Dict[str, Any]] = Field(None, description="The most recent terms from the opponent.")
    sentiment_score: float = Field(0.0, description="The current emotional state of the opponent (0.0=Frustrated, 1.0=Satisfied).")
    turns_left: int = Field(..., description="The remaining number of turns before the negotiation fails.")
    is_done: bool = Field(False, description="Whether the negotiation session has ended (deal reached or quit).")

class Reward(BaseModel):
    """The structured reward object returned after each step."""
    value: float = Field(..., description="The scalar reward signal (0.0-1.0).")
    concession_points: float = Field(default=0.0, description="Points awarded for making a meaningful concession.")
    sentiment_bonus: float = Field(default=0.0, description="Bonus for maintaining positive sentiment.")

class State(BaseModel):
    """The internal episode-level state tracking data."""
    zopa_min: float = Field(..., description="The minimum price the seller (environment) will accept.")
    zopa_max: float = Field(..., description="The maximum price the buyer (agent) should pay.")
    target_price: float = Field(..., description="The optimal target price for the agent.")
    opponent_strategy: str = Field(..., description="The internal personality/strategy of the opponent.")
    step_count: int = Field(0, description="The current turn number.")
    
class TaskConfig(BaseModel):
    """Configuration for a specific negotiation scenario."""
    id: str
    name: str
    difficulty: Literal["easy", "medium", "hard"]
    starting_buyer_price: float
    starting_seller_price: float
    seller_min_accept: float
    max_turns: int
    required_terms: List[str] = []
