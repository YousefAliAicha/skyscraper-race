"""One player: name, tower, rolls, and personal challenge heap."""

from challenges import generate_challenge_heights, make_heap
from tower import Tower


class Player:
    def __init__(self, name: str, rolls_per_turn: int = 3):
        self.name = name
        self.tower = Tower()
        self.rolls_per_turn = rolls_per_turn
        self.rolls_remaining = rolls_per_turn
        self.current_roll = None  # decoded roll waiting to be placed
        self.challenge_heights = generate_challenge_heights()
        self.challenge_heap = make_heap(list(self.challenge_heights))
        self.won = False

    def reset_rolls(self):
        self.rolls_remaining = self.rolls_per_turn
        self.current_roll = None

    def tower_height(self):
        return self.tower.total_height

    def floor_count(self):
        return self.tower.size

    def next_challenge(self):
        """Peek at the next challenge height (min-heap root), or None."""
        return self.challenge_heap[0] if self.challenge_heap else None
