"""Game orchestration: turns, placement, win check.

UI (main.py) calls into this; this module must not depend on game2dboard
so logic can be tested headlessly.
"""

from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import decode_roll, generate_roll


class Game:
    """Two-player skyscraper race."""

    def __init__(self, name1: str = "Player 1", name2: str = "Player 2"):
        self.players = [
            Player(name1, ROLLS_PER_TURN),
            Player(name2, ROLLS_PER_TURN),
        ]
        self.current_index = 0
        self.phase = "roll"  # roll | place | game_over
        self.message = f"{self.current_player().name}'s turn — roll"
        self.winner = None
        self.enable_challenges = False  # flip True when Step 7 is ready

    def current_player(self) -> Player:
        return self.players[self.current_index]

    def other_player(self) -> Player:
        return self.players[1 - self.current_index]

    def roll(self) -> dict:
        """Generate and store a decoded roll for the current player.

        TODO: enforce rolls_remaining, scrap, phase checks — Step 8/10.
        """
        raise NotImplementedError("Game.roll — Step 8")

    def scrap_roll(self) -> None:
        """Discard current roll without placing."""
        raise NotImplementedError("Game.scrap_roll — Step 8")

    def place_floor(self, position: int) -> None:
        """Insert current roll as a floor at `position`, then stability check.

        TODO: insert, weakest/collapse, optional challenges, win, end turn.
        """
        raise NotImplementedError("Game.place_floor — Step 8/10")

    def check_win(self) -> bool:
        player = self.current_player()
        if player.tower_height() >= TARGET_HEIGHT:
            self.winner = player
            self.phase = "game_over"
            player.won = True
            self.message = f"{player.name} wins at {player.tower_height():.1f}m!"
            return True
        return False

    def end_turn(self) -> None:
        """Hand play to the other player."""
        if self.phase == "game_over":
            return
        self.current_index = 1 - self.current_index
        player = self.current_player()
        player.reset_rolls()
        self.phase = "roll"
        self.message = f"{player.name}'s turn — roll"
