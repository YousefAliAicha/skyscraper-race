"""Challenge schedule — min-heap of trigger heights + height lookup.

DSA:
  - Min-heap (heapq): next challenge by tower height
  - Binary search (bisect): which floor sits at a damaged height

PHASE 2 / OPTIONAL for a thinner MVP:
  Can be deferred if the team needs fewer presentation topics.
  Core game (roll → place → stability → collapse → win) works without this.
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


CHALLENGE_TYPES = ("earthquake", "windstorm", "drunk_driver")

DAMAGE_BY_TYPE = {
    "earthquake": EARTHQUAKE_DAMAGE,
    "windstorm": WINDSTORM_DAMAGE,
    "drunk_driver": DRUNK_DRIVER_DAMAGE,
}


def generate_challenge_heights(
    n: int = NUM_CHALLENGES,
    lo: int = CHALLENGE_MIN_HEIGHT,
    hi: int = CHALLENGE_MAX_HEIGHT,
    min_gap: int = CHALLENGE_MIN_GAP,
) -> list:
    """Return n sorted heights in [lo, hi] with at least min_gap between them.

    TODO: implement spacing logic — Step 7.
    """
    raise NotImplementedError("generate_challenge_heights — Step 7")


def make_challenge_heap(heights=None) -> list:
    """Build a min-heap of challenge heights."""
    if heights is None:
        heights = generate_challenge_heights()
    heap = list(heights)
    heapq.heapify(heap)
    return heap


def find_floor_index_at_height(cumulative_heights: list, height: float) -> int:
    """Binary search: index of the floor that contains `height`.

    cumulative_heights[i] = total height up through floor i (bottom-up).
    TODO: implement with bisect_right — Step 7.
    """
    raise NotImplementedError("find_floor_index_at_height — Step 7")


def process_challenges(tower, challenge_heap: list) -> list:
    """Pop and apply every challenge whose height <= tower.total_height().

    Returns a list of event dicts for the UI / message bar.
    TODO: implement — Step 7.
    """
    raise NotImplementedError("process_challenges — Step 7")
