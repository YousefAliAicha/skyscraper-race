"""Turn loop: roll → place/scrap → stability → win. No GUI dependency."""

from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import full_decode, generate_roll
from tower import Floor


class Game:
    def __init__(self, name1="Player 1", name2="Player 2"):
        self.players = [Player(name1, ROLLS_PER_TURN), Player(name2, ROLLS_PER_TURN)]
        self.current_index = 0
        self.phase = "roll"  # roll | place | game_over
        self.winner = None
        self.last_collapse = None
        self.message = f"{self.current_player().name}'s turn — press ROLL"

    def current_player(self):
        return self.players[self.current_index]

    def roll(self):
        if self.phase != "roll":
            raise RuntimeError(f"Cannot roll during {self.phase}")
        p = self.current_player()
        if p.rolls_remaining <= 0:
            raise RuntimeError("No rolls left")
        decoded = full_decode(generate_roll())
        p.current_roll = decoded
        p.rolls_remaining -= 1
        self.phase = "place"
        self.message = (
            f"{p.name} rolled {decoded['roll']}: {decoded['material_name']} "
            f"{decoded['height']}m — place or SCRAP"
        )
        return decoded

    def scrap_roll(self):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("No roll to scrap")
        p = self.current_player()
        p.current_roll = None
        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message = f"{p.name} scrapped — {p.rolls_remaining} left"
        else:
            self.end_turn()

    def place_floor(self, position: int):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("No roll to place")
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
                f"{p.name} COLLAPSE — lost {len(fallen)} floors / {lost}m"
            )
        else:
            self.message = (
                f"{p.name} placed {decoded['material_name']} "
                f"({decoded['height']}m) — tower {p.tower_height():.0f}m"
            )

        if self.check_win():
            return {"collapsed": collapsed, "won": True}

        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message += f" — {p.rolls_remaining} left"
        else:
            self.end_turn()
        return {"collapsed": collapsed, "won": False}

    def check_win(self):
        p = self.current_player()
        if p.tower_height() >= TARGET_HEIGHT:
            self.winner = p
            self.phase = "game_over"
            p.won = True
            self.message = f"{p.name} wins at {p.tower_height():.1f}m!"
            return True
        return False

    def end_turn(self):
        if self.phase == "game_over":
            return
        self.current_index = 1 - self.current_index
        p = self.current_player()
        p.reset_rolls()
        self.phase = "roll"
        self.message = f"{p.name}'s turn — press ROLL"
