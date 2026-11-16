"""Challenges that fire when the tower grows tall enough.

DSA used here (2 of the 6):
  Min-heap       — smallest challenge height is always at the front
  Binary search  — find which floor sits at a given height
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

EVENT_NAMES = ("earthquake", "windstorm", "drunk_driver")
DAMAGE = {
    "earthquake": EARTHQUAKE_DAMAGE,
    "windstorm": WINDSTORM_DAMAGE,
    "drunk_driver": DRUNK_DRIVER_DAMAGE,
}


def make_challenge_heights():
    """Pick NUM_CHALLENGES heights, spaced at least CHALLENGE_MIN_GAP apart."""
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
    """Turn a list of heights into a min-heap (smallest on top)."""
    if heights is None:
        heights = make_challenge_heights()
    heap = list(heights)
    heapq.heapify(heap)
    return heap


def height_milestones(tower):
    """Running totals from ground up, e.g. [10, 25, 40] for floors 10+15+15.

    This list is sorted, so we can binary-search it.
    """
    milestones = []
    total = 0.0
    for floor in tower.floors_from_ground():
        total += floor.height
        milestones.append(total)
    return milestones


def find_floor_at_height(tower, target_height):
    """Binary search: which floor contains `target_height` meters from ground?"""
    floors = tower.floors_from_ground()
    if not floors:
        return None

    milestones = height_milestones(tower)
    index = bisect_right(milestones, target_height - 1e-9)
    if index >= len(floors):
        index = len(floors) - 1
    return floors[index]


def apply_event(tower, event_name):
    """Hurt floors. Returns a short message for the sidebar."""
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

    # drunk driver → binary search finds the ground floor
    ground_floor = find_floor_at_height(tower, 0.1)
    if ground_floor is None:
        ground_floor = floors[0]
    ground_floor.take_damage(damage)
    return f"Drunk driver -{percent}% ground"


def run_challenges(tower, challenge_heap):
    """Pop and apply every challenge whose height <= tower height.

    Min-heap: challenge_heap[0] is always the next (smallest) height.
    """
    messages = []
    fired = []

    while challenge_heap and challenge_heap[0] <= tower.get_height():
        height = heapq.heappop(challenge_heap)
        event_name = random.choice(EVENT_NAMES)
        messages.append(f"@{height}m {apply_event(tower, event_name)}")
        fired.append(height)

    return messages, fired
