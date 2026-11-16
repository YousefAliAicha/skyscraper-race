"""Random challenge events as the tower climbs.

DSA used here:
  Min-heap       — next challenge is always heap[0] (smallest height)
  Binary search  — find which floor sits at a given height (bisect)
"""

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
    """Pick n heights in [lo, hi], each at least `gap` meters apart.

    Strategy: place them in order from low to high so a gap is always possible.
    """
    heights = []
    next_lo = lo
    for remaining in range(n, 0, -1):
        # Leave room for the later challenges (each needs `gap` after the previous)
        max_for_this = hi - gap * (remaining - 1)
        if next_lo > max_for_this:
            break
        h = random.randint(next_lo, max_for_this)
        heights.append(h)
        next_lo = h + gap
    return heights


def make_heap(heights=None):
    """Build a min-heap of challenge heights."""
    heap = list(heights if heights is not None else generate_challenge_heights())
    heapq.heapify(heap)
    return heap


def cumulative_heights(tower):
    """Running total of height from ground up — a sorted list."""
    totals = []
    total = 0.0
    for floor in tower.floors_bottom_up():
        total += floor.height
        totals.append(total)
    return totals


def find_floor_at_height(tower, height):
    """Binary search: which floor contains `height` meters from the ground?"""
    floors = tower.floors_bottom_up()
    if not floors:
        return None
    cum = cumulative_heights(tower)
    idx = bisect_right(cum, height - 1e-9)
    if idx >= len(floors):
        idx = len(floors) - 1
    return floors[idx]


def apply_challenge(tower, kind):
    """Apply one challenge's damage. Returns a short description."""
    floors = tower.floors_bottom_up()
    if not floors:
        return f"{kind}: empty tower"

    pct = DAMAGE[kind]
    if kind == "earthquake":
        for f in floors:
            f.take_damage(pct)
        return f"Earthquake −{int(pct * 100)}% all floors"

    if kind == "windstorm":
        for f in floors[-3:]:
            f.take_damage(pct)
        return f"Windstorm −{int(pct * 100)}% top floors"

    # drunk driver hits the ground floor (found via binary search)
    ground = find_floor_at_height(tower, 0.1) or floors[0]
    ground.take_damage(pct)
    return f"Drunk driver −{int(pct * 100)}% ground"


def process_challenges(tower, heap):
    """Pop and apply every challenge whose height ≤ current tower height."""
    events, triggered = [], []
    while heap and heap[0] <= tower.total_height:
        h = heapq.heappop(heap)
        kind = random.choice(TYPES)
        events.append(f"@{h}m {apply_challenge(tower, kind)}")
        triggered.append(h)
    return events, triggered
