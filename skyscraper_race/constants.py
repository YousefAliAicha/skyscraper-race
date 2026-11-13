"""All tunable game numbers in one place."""

# --- Win condition ---
TARGET_HEIGHT = 150  # meters to win

# --- Roll ---
ROLL_MIN = 10000
ROLL_MAX = 99999
ROLLS_PER_TURN = 3

# Digit 1 -> material tier
TIER_RANGES = {
    1: "junk",
    2: "junk",
    3: "junk",
    4: "common",
    5: "common",
    6: "common",
    7: "common",
    8: "strong",
    9: "strong",
}

# --- Challenges (phase 2 — can stay deferred for a thinner MVP) ---
NUM_CHALLENGES = 4
CHALLENGE_MIN_HEIGHT = 30
CHALLENGE_MAX_HEIGHT = 140
CHALLENGE_MIN_GAP = 15

EARTHQUAKE_DAMAGE = 0.10  # all floors
WINDSTORM_DAMAGE = 0.15  # top 3 floors
DRUNK_DRIVER_DAMAGE = 0.25  # ground floor

# --- Board layout (game2dboard) ---
BOARD_ROWS = 14
BOARD_COLS = 10
CELL_SIZE = 60

# Player tower columns on the board
P1_COLS = (0, 1, 2)
P2_COLS = (7, 8, 9)
# Visible floor slots: rows 2..12 (11 slots), ground visual at row 13
TOWER_TOP_ROW = 2
TOWER_BOTTOM_ROW = 12
GROUND_ROW = 13
MAX_VISIBLE_FLOORS = TOWER_BOTTOM_ROW - TOWER_TOP_ROW + 1  # 11
