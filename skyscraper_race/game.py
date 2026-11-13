"""Game orchestration: turns, placement, win check.

UI (main.py) calls into this; this module must not depend on game2dboard
so logic can be tested headlessly.
"""

from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import decode_roll, full_decode, generate_roll
from tower import Floor


class Game:
    """Two-player skyscraper race."""

    def __init__(self, name1: str = "Player 1", name2: str = "Player 2"):
        self.players = [
            Player(name1, ROLLS_PER_TURN),
            Player(name2, ROLLS_PER_TURN),
        ]
        self.current_index = 0
        self.phase = "roll"  # roll | place | game_over
        self.message = f"{self.current_player().name}'s turn — press ROLL"
        self.winner = None
        self.last_collapse = None  # (fallen, height_lost) or None
        self.enable_challenges = False  # Phase 2

    def current_player(self) -> Player:
        return self.players[self.current_index]

    def other_player(self) -> Player:
        return self.players[1 - self.current_index]

    def roll(self) -> dict:
        """Generate and store a decoded roll for the current player."""
        if self.phase == "game_over":
            raise RuntimeError("Game is over")
        if self.phase != "roll":
            raise RuntimeError(f"Cannot roll during phase {self.phase!r}")

        player = self.current_player()
        if player.rolls_remaining <= 0:
            raise RuntimeError("No rolls remaining this turn")

        number = generate_roll()
        decoded = full_decode(number)
        player.current_roll = decoded
        player.rolls_remaining -= 1
        self.phase = "place"
        self.message = (
            f"{player.name} rolled {number}: {decoded['material_name']} "
            f"{decoded['height']}m — click a tower row to place (or SCRAP)"
        )
        return decoded

    def scrap_roll(self) -> None:
        """Discard current roll without placing."""
        if self.phase == "game_over":
            raise RuntimeError("Game is over")
        if self.phase != "place" or self.current_player().current_roll is None:
            raise RuntimeError("No roll to scrap")

        player = self.current_player()
        player.current_roll = None
        if player.rolls_remaining > 0:
            self.phase = "roll"
            self.message = (
                f"{player.name} scrapped — {player.rolls_remaining} rolls left"
            )
        else:
            self.end_turn()

    def place_floor(self, position: int) -> dict:
        """Insert current roll at `position`, then stability / win checks.

        Returns a result dict for the UI.
        """
        if self.phase == "game_over":
            raise RuntimeError("Game is over")
        if self.phase != "place" or self.current_player().current_roll is None:
            raise RuntimeError("No roll to place")

        player = self.current_player()
        decoded = player.current_roll
        floor = Floor(decoded)

        # Clamp position into [0, size]
        position = max(0, min(position, player.tower.floor_count()))
        player.tower.insert_at(position, floor)
        player.current_roll = None
        self.last_collapse = None

        ratio, weakest = player.tower.check_stability()
        collapsed = False
        if weakest is not None and ratio < 1.0:
            fallen, lost = player.tower.collapse(weakest)
            self.last_collapse = (fallen, lost)
            collapsed = True
            self.message = (
                f"{player.name} placed {decoded['material_name']} — "
                f"COLLAPSE! lost {len(fallen)} floors / {lost}m"
            )
        else:
            self.message = (
                f"{player.name} placed {decoded['material_name']} "
                f"({decoded['height']}m) at pos {position} — "
                f"tower {player.tower_height():.0f}m"
            )

        # Challenges (Phase 2) would run here

        if self.check_win():
            return {
                "placed": True,
                "collapsed": collapsed,
                "won": True,
                "decoded": decoded,
            }

        if player.rolls_remaining > 0:
            self.phase = "roll"
            self.message += f" — {player.rolls_remaining} rolls left"
        else:
            self.end_turn()

        return {
            "placed": True,
            "collapsed": collapsed,
            "won": False,
            "decoded": decoded,
        }

    def check_win(self) -> bool:
        player = self.current_player()
        if player.tower_height() >= TARGET_HEIGHT:
            self.winner = player
            self.phase = "game_over"
            player.won = True
            self.message = (
                f"{player.name} wins at {player.tower_height():.1f}m!"
            )
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
        self.message = f"{player.name}'s turn — press ROLL"
