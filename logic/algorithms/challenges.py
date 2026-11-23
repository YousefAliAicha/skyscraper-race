"""DATA STRUCTURE #3 — Min-heap of challenge heights.

ALGORITHM #2 — heap peek / pop:
  peek = challenge_heap[0]   (next / smallest height)
  pop  = heappop(...)        when the tower reaches that height
"""

import heapq
import random

from logic.data.constants import (
    CHALLENGE_MAX_HEIGHT,
    CHALLENGE_MIN_GAP,
    CHALLENGE_MIN_HEIGHT,
    DRUNK_DRIVER_DAMAGE,
    EARTHQUAKE_DAMAGE,
    NUM_CHALLENGES,
    WINDSTORM_DAMAGE,
)

EVENT_NAMES = ("earthquake", "windstorm", "drunk_driver")
DAMAGE = {
    "earthquake": EARTHQUAKE_DAMAGE,
    "windstorm": WINDSTORM_DAMAGE,
    "drunk_driver": DRUNK_DRIVER_DAMAGE,
}


def make_challenge_heights():
    """Pick spaced challenge heights (low → high)."""
    heights = []
    lowest_allowed = CHALLENGE_MIN_HEIGHT

    for left in range(NUM_CHALLENGES, 0, -1):
        highest_allowed = CHALLENGE_MAX_HEIGHT - CHALLENGE_MIN_GAP * (left - 1)
        if lowest_allowed > highest_allowed:
            break
        height = random.randint(lowest_allowed, highest_allowed)
        heights.append(height)
        lowest_allowed = height + CHALLENGE_MIN_GAP

    return heights


def make_heap(heights=None):
    """Build a min-heap (smallest height at the front)."""
    if heights is None:
        heights = make_challenge_heights()
    heap = list(heights)
    heapq.heapify(heap)
    return heap


def apply_event(tower, event_name):
    """Hurt floors. Returns a short sidebar message."""
    floors = tower.floors_from_ground()
    if not floors:
        return event_name + ": empty tower"

    damage = DAMAGE[event_name]
    percent = int(damage * 100)

    if event_name == "earthquake":
        for floor in floors:
            floor.take_damage(damage)
        return f"Earthquake -{percent}% all floors"

    if event_name == "windstorm":
        for floor in floors[-3:]:
            floor.take_damage(damage)
        return f"Windstorm -{percent}% top floors"

    # drunk driver hits the ground floor (index 0) — no search needed
    floors[0].take_damage(damage)
    return f"Drunk driver -{percent}% ground"


def run_challenges(tower, challenge_heap):
    """Peek/pop every challenge whose height <= tower height."""
    messages = []
    fired = []

    while challenge_heap and challenge_heap[0] <= tower.get_height():
        height = heapq.heappop(challenge_heap)
        event_name = random.choice(EVENT_NAMES)
        messages.append(f"@{height}m {apply_event(tower, event_name)}")
        fired.append(height)

    return messages, fired
