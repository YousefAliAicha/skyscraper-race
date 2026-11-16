"""One player: name, tower, rolls left, and a challenge heap."""

from challenges import make_challenge_heights, make_heap
from tower import Tower


class Player:
    def __init__(self, name, rolls_per_turn=3):
        self.name = name
        self.tower = Tower()
        self.rolls_per_turn = rolls_per_turn
        self.rolls_left = rolls_per_turn
        self.pending_roll = None  # floor recipe waiting to be placed

        # DSA: min-heap of challenge heights (smallest next)
        self.challenge_heights = make_challenge_heights()
        self.challenge_heap = make_heap(list(self.challenge_heights))
        self.won = False

    def reset_rolls(self):
        self.rolls_left = self.rolls_per_turn
        self.pending_roll = None

    def tower_height(self):
        return self.tower.get_height()

    def floor_count(self):
        return self.tower.floor_count()

    def next_challenge(self):
        """Peek at the heap root (next challenge), or None."""
        if self.challenge_heap:
            return self.challenge_heap[0]
        return None
