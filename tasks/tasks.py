from env.models import TaskConfig

# 1. Easy Task: Vintage Camera
# Goal: Get price down to $150 or lower.
TASK_EASY = TaskConfig(
    id="buy_vintage_camera",
    name="Buy Vintage Camera",
    difficulty="easy",
    starting_buyer_price=100.0,
    starting_seller_price=250.0,
    seller_min_accept=140.0,
    max_turns=10,
    required_terms=[]
)

# 2. Medium Task: Event Catering
# Goal: Price + Setup details.
TASK_MEDIUM = TaskConfig(
    id="event_catering_bundle",
    name="Event Catering Bundle",
    difficulty="medium",
    starting_buyer_price=500.0,
    starting_seller_price=1200.0,
    seller_min_accept=800.0,
    max_turns=15,
    required_terms=["setup_time", "waste_removal"]
)

# 3. Hard Task: Server Hardware Procurement
# Goal: Complex price-per-unit + SLA terms + Delivery schedule.
TASK_HARD = TaskConfig(
    id="server_hardware_procurement",
    name="Server Hardware Procurement",
    difficulty="hard",
    starting_buyer_price=50000.0,
    starting_seller_price=150000.0,
    seller_min_accept=105000.0,
    max_turns=20,
    required_terms=["sla_uptime", "delivery_penalty", "maintenance_plan"]
)

TASKS = {
    "easy": TASK_EASY,
    "medium": TASK_MEDIUM,
    "hard": TASK_HARD
}
