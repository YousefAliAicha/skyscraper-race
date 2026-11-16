"""Game settings — change values here to tune balance."""

# Win
TARGET_HEIGHT = 150

# Rolls
ROLL_MIN = 10000
ROLL_MAX = 99999
ROLLS_PER_TURN = 3

# Digit 1 of the roll → material tier
TIER_RANGES = {
    1: "junk", 2: "junk", 3: "junk",
    4: "common", 5: "common", 6: "common", 7: "common",
    8: "strong", 9: "strong",
}

# amount (1–10) × this = material units used for weight/capacity
UNITS_PER_AMOUNT = 150

# capacity = capacity_mult × height × CAPACITY_CONSTANT × integrity
CAPACITY_CONSTANT = 1200

# Challenges (min-heap of heights)
NUM_CHALLENGES = 3
CHALLENGE_MIN_HEIGHT = 50
CHALLENGE_MAX_HEIGHT = 130
CHALLENGE_MIN_GAP = 25
EARTHQUAKE_DAMAGE = 0.06
WINDSTORM_DAMAGE = 0.10
DRUNK_DRIVER_DAMAGE = 0.15

# Board grid (game2dboard)
BOARD_ROWS = 14
BOARD_COLS = 10
CELL_SIZE = 64
P1_COLS = (0, 1, 2)
P2_COLS = (7, 8, 9)
TOWER_TOP_ROW = 2
TOWER_BOTTOM_ROW = 12
GROUND_ROW = 13
MAX_VISIBLE_FLOORS = TOWER_BOTTOM_ROW - TOWER_TOP_ROW + 1
