"""Challenge schedule: min-heap of heights + binary search for floor-at-height."""

import heapq
import random
from bisect import bisect_right

from constants import (
    CHALLENGE_MAX_HEIGHT,
    CHALLENGE_MIN_GAP,
    CHALLENGE_MIN_HEIGHT,
    DRUNK_DRIVER_DAMAGE,
    EARTHQUAKE_DAMAGE,
    NUM_CHALLENGES,
    WINDSTORM_DAMAGE,
)

TYPES = ("earthquake", "windstorm", "drunk_driver")
DAMAGE = {
    "earthquake": EARTHQUAKE_DAMAGE,
    "windstorm": WINDSTORM_DAMAGE,
    "drunk_driver": DRUNK_DRIVER_DAMAGE,
}


def generate_challenge_heights(
    n=NUM_CHALLENGES,
    lo=CHALLENGE_MIN_HEIGHT,
    hi=CHALLENGE_MAX_HEIGHT,
    gap=CHALLENGE_MIN_GAP,
):
    heights = []
    guard = 0
    while len(heights) < n and guard < 500:
        guard += 1
        h = random.randint(lo, hi)
        if all(abs(h - e) >= gap for e in heights):
            heights.append(h)
    return sorted(heights)


def make_heap(heights=None):
    heap = list(heights if heights is not None else generate_challenge_heights())
    heapq.heapify(heap)
    return heap


def cumulative_heights(tower):
    totals, total = [], 0.0
    for floor in tower.floors_bottom_up():
        total += floor.height
        totals.append(total)
    return totals


def find_floor_at_height(tower, height):
    """Binary search: floor whose band contains `height` meters from ground."""
    floors = tower.floors_bottom_up()
    if not floors:
        return None
    cum = cumulative_heights(tower)
    idx = bisect_right(cum, height - 1e-9)
    if idx >= len(floors):
        idx = len(floors) - 1
    return floors[idx]


def apply_challenge(tower, kind):
    floors = tower.floors_bottom_up()
    if not floors:
        return f"{kind}: tower empty"
    pct = DAMAGE[kind]
    if kind == "earthquake":
        for f in floors:
            f.take_damage(pct)
        return f"Earthquake -{int(pct * 100)}% all"
    if kind == "windstorm":
        for f in floors[-3:]:
            f.take_damage(pct)
        return f"Windstorm -{int(pct * 100)}% top"
    ground = find_floor_at_height(tower, 0.1) or floors[0]
    ground.take_damage(pct)
    return f"Drunk driver -{int(pct * 100)}% ground"


def process_challenges(tower, heap):
    """Pop challenges at/under tower height. Returns (event_strings, triggered_heights)."""
    events, triggered = [], []
    while heap and heap[0] <= tower.total_height:
        h = heapq.heappop(heap)
        kind = random.choice(TYPES)
        events.append(f"@{h}m {apply_challenge(tower, kind)}")
        triggered.append(h)
    return events, triggered
