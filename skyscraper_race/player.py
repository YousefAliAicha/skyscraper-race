"""Player state: name, tower, rolls remaining, optional challenge heap."""

from tower import Tower


class Player:
    def __init__(self, name: str, rolls_per_turn: int = 3):
        self.name = name
        self.tower = Tower()
        self.rolls_remaining = rolls_per_turn
        self.rolls_per_turn = rolls_per_turn
        self.current_roll = None  # decoded roll dict or None
        self.challenge_heap = []  # filled when challenges phase is enabled
        self.won = False

    def reset_rolls(self) -> None:
        self.rolls_remaining = self.rolls_per_turn
        self.current_roll = None

    def tower_height(self) -> float:
        return self.tower.total_height()

    def floor_count(self) -> int:
        return self.tower.size

    def __repr__(self) -> str:
        return (
            f"Player({self.name!r}, height={self.tower_height():.1f}m, "
            f"floors={self.floor_count()})"
        )
