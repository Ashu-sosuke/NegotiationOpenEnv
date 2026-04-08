# NegotiationOpenEnv — Meta Hackathon

A specialized OpenEnv environment that simulates real-world commercial negotiations. This environment is designed to evaluate the strategic reasoning, emotional intelligence, and compromise-making abilities of AI agents in a multi-turn, business-oriented dialogue.

---

### 🌟 Project Vision
In the future of agentic commerce, AI will not just buy products — it will **negotiate** them. This environment provides the first standardized benchmark for training and evaluating agents on:
- **Price Anchoring**: Managing start and end points of a negotiation.
- **Concession Dynamics**: Knowing when and how much to concede.
- **Strategic Communication**: Balancing toughness with rapport.

---

### 🏗️ Environment Specification

#### Observation Space (Typed)
Every turn, the agent receives a structured `Observation` model:
- `history (List[Dict])`: The full conversation including all prior offers.
- `current_opponent_offer (float)`: The most recent price proposed by the seller.
- `sentiment_score (float)`: A value from 0.0 to 1.0 indicating the opponent's "patience" or "satisfaction".
- `turns_left (int)`: Count of turns remaining before a deadlock is declared.

#### Action Space (Typed)
The agent must respond with a structured `Action` model:
- `intent (Literal)`: One of `OFFER`, `ACCEPT`, `REJECT`, or `QUIT`.
- `price (float)`: The buyer's counter-offer.
- `message (str)`: Natural language justification for the move.
- `terms (Dict)`: (Optional) Complex variables like "shipping_speed" or "sla_uptime".

---

### 🎯 Tasks & Complexity
1.  **Easy: Buy Vintage Camera**
    - Single-item, low-stakes. Good for testing basic "price-following" logic.
2.  **Medium: Event Catering Bundle**
    - Multi-variable. Now includes "setup_time" and "waste_removal" terms.
3.  **Hard: Server Hardware Procurement**
    - High-stakes B2B. Includes SLAs, delivery penalties, and a "TOUGH" opponent strategy.

---

### 🧩 Reward & Grading System
- **Progressive Reward**: Awarded per-step based on the realism of the offer and closeness to the ZOPA (Zone of Possible Agreement).
- **Final Grade (0.0 - 1.0)**:
  - **Agreement (0.5)**: Did a deal close?
  - **Efficiency (0.3)**: How close did the final price get to the buyer's ideal target?
  - **Terms (0.2)**: Were all required contract terms mentioned and agreed upon?

---

### 🛠️ Setup & Usage

#### 1. Quick Start (Local)
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```
The API will be available at `http://localhost:8000/docs`.

#### 2. Run Inference Agent
```bash
# Set your Gemini API key in .env
GEMINI_API_KEY=your_key_here

# Start the server, then run inference
python app.py          # Terminal 1
python inference.py    # Terminal 2
```

#### 3. Docker Deployment
```bash
docker build -t negotiation-env .
docker run -p 8000:8000 negotiation-env
```

---

### ✅ OpenEnv Validation
To verify this environment against the Meta Hackathon spec:
```bash
pip install openenv-core
openenv validate
```
