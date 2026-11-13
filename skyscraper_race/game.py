"""Turn loop: roll → place/scrap → stability → win. No GUI dependency."""

from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import full_decode, generate_roll
from tower import Floor


class Game:
    def __init__(self, name1="P1", name2="P2"):
        self.players = [Player(name1, ROLLS_PER_TURN), Player(name2, ROLLS_PER_TURN)]
        self.current_index = 0
        self.phase = "roll"  # roll | place | game_over
        self.winner = None
        self.last_collapse = None
        self.message = self._prompt_roll()

    def current_player(self):
        return self.players[self.current_index]

    def side_hint(self):
        return "LEFT" if self.current_index == 0 else "RIGHT"

    def _prompt_roll(self):
        p = self.current_player()
        return (
            f"{p.name}'s turn ({self.side_hint()}) — ROLL or press R "
            f"[{p.rolls_remaining} rolls]"
        )

    def roll(self):
        if self.phase == "game_over":
            raise RuntimeError("Game over")
        if self.phase != "roll":
            raise RuntimeError("Already rolled — PLACE (Space/click) or SCRAP")
        p = self.current_player()
        if p.rolls_remaining <= 0:
            raise RuntimeError("No rolls left")
        decoded = full_decode(generate_roll())
        p.current_roll = decoded
        p.rolls_remaining -= 1
        self.phase = "place"
        self.message = (
            f"{p.name} got {decoded['material_name']} {decoded['height']}m "
            f"(roll {decoded['roll']}) — click {self.side_hint()} tower, "
            f"Space=top, or SCRAP"
        )
        return decoded

    def scrap_roll(self):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("Nothing to scrap — ROLL first")
        p = self.current_player()
        p.current_roll = None
        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message = f"{p.name} scrapped. {self._prompt_roll()}"
        else:
            self.end_turn()

    def place_floor(self, position: int):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("ROLL first, then place")
        p = self.current_player()
        decoded = p.current_roll
        pos = max(0, min(position, p.tower.floor_count()))
        p.tower.insert_at(pos, Floor(decoded))
        p.current_roll = None
        self.last_collapse = None

        ratio, weakest = p.tower.check_stability()
        collapsed = False
        if weakest is not None and ratio < 1.0:
            fallen, lost = p.tower.collapse(weakest)
            self.last_collapse = (fallen, lost)
            collapsed = True
            self.message = (
                f"{p.name} COLLAPSE! lost {len(fallen)} floors / {lost:.0f}m "
                f"(now {p.tower_height():.0f}m)"
            )
        else:
            self.message = (
                f"{p.name} +{decoded['material_name']} {decoded['height']}m "
                f"@pos{pos} → {p.tower_height():.0f}m / {TARGET_HEIGHT}m"
            )

        if self.check_win():
            return {"collapsed": collapsed, "won": True}

        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message += f" — ROLL again [{p.rolls_remaining} left]"
        else:
            self.end_turn()
        return {"collapsed": collapsed, "won": False}

    def place_on_top(self):
        """Most common move: append above current top."""
        return self.place_floor(self.current_player().tower.floor_count())

    def check_win(self):
        p = self.current_player()
        if p.tower_height() >= TARGET_HEIGHT:
            self.winner = p
            self.phase = "game_over"
            p.won = True
            self.message = f"{p.name} WINS at {p.tower_height():.0f}m!"
            return True
        return False

    def end_turn(self):
        if self.phase == "game_over":
            return
        self.current_index = 1 - self.current_index
        self.current_player().reset_rolls()
        self.phase = "roll"
        self.message = f"Turn over → {self._prompt_roll()}"
