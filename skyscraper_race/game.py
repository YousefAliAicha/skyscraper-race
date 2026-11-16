"""Turn logic only — no GUI. The UI calls these methods.

Each turn:
  roll → place or scrap → challenges → check collapse → check win
"""

from challenges import run_challenges
from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import full_decode, generate_roll
from floor import Floor


class Game:
    def __init__(self, name1="P1", name2="P2", enable_challenges=True):
        self.players = [
            Player(name1, ROLLS_PER_TURN),
            Player(name2, ROLLS_PER_TURN),
        ]
        self.current_index = 0
        self.phase = "roll"  # roll | place | game_over
        self.winner = None
        self.last_collapse = None
        self.enable_challenges = enable_challenges
        self.message = ""
        self.feed = {
            "headline": f"{name1}'s turn",
            "detail": "Press R or click ROLL",
            "result": "Waiting",
            "result_ok": True,
            "events": [],
        }
        self.message = self._prompt_roll()

    def current_player(self):
        return self.players[self.current_index]

    def side_hint(self):
        return "LEFT" if self.current_index == 0 else "RIGHT"

    def _prompt_roll(self):
        return f"{self.current_player().name}'s turn — roll a floor"

    def _set_feed(self, headline, detail, result="OK", result_ok=True, events=None):
        self.feed = {
            "headline": headline,
            "detail": detail,
            "result": result,
            "result_ok": result_ok,
            "events": events or [],
        }

    def roll(self):
        if self.phase == "game_over":
            raise RuntimeError("Game over")
        if self.phase != "roll":
            raise RuntimeError("Place or scrap first")

        player = self.current_player()
        if player.rolls_left <= 0:
            raise RuntimeError("No rolls left")

        recipe = full_decode(generate_roll())
        player.pending_roll = recipe
        player.rolls_left -= 1
        self.phase = "place"

        tips = {
            "junk": "Weak — put on top or scrap",
            "strong": "Strong — good at the bottom",
            "common": "Move the arrow, then press Enter",
        }
        tip = tips[recipe["tier"]]

        self.message = f"Rolled {recipe['material_name']} {recipe['height']}m"
        self._set_feed(
            f"Rolled {recipe['material_name']}",
            f"{recipe['height']} m — {tip}",
            "Choose a height",
        )
        return recipe

    def scrap_roll(self):
        if self.phase != "place" or not self.current_player().pending_roll:
            raise RuntimeError("Nothing to scrap")

        player = self.current_player()
        player.pending_roll = None
        self._set_feed("Scrapped", "That roll was discarded", "OK")

        if player.rolls_left > 0:
            self.phase = "roll"
            self.message = self._prompt_roll()
        else:
            self.end_turn()

    def place_floor(self, position):
        if self.phase != "place" or not self.current_player().pending_roll:
            raise RuntimeError("Roll first")

        player = self.current_player()
        recipe = player.pending_roll
        slot = max(0, min(position, player.tower.floor_count()))

        player.tower.insert_at(slot, Floor(recipe))
        player.pending_roll = None
        self.last_collapse = None

        events = []
        if self.enable_challenges:
            events, _fired = run_challenges(player.tower, player.challenge_heap)

        collapsed = False
        ratio, weakest = player.tower.check_stable()
        if weakest is not None and ratio < 1.0:
            self.last_collapse = player.tower.collapse(weakest)
            collapsed = True

        height = player.tower_height()
        if collapsed:
            fallen_floors, meters_lost = self.last_collapse
            self._set_feed(
                f"Placed {recipe['material_name']} ({recipe['height']} m)",
                f"Slot {slot} → tower {height:.0f} m",
                f"Collapsed — lost {len(fallen_floors)} floors ({meters_lost:.0f} m)",
                result_ok=False,
                events=events,
            )
            self.message = f"Collapse! {height:.0f} m left"
        else:
            self._set_feed(
                f"Placed {recipe['material_name']} ({recipe['height']} m)",
                f"Slot {slot} → tower {height:.0f} m",
                "Stable",
                events=events,
            )
            self.message = f"Placed — {height:.0f} m"

        if self.check_win():
            return {"collapsed": collapsed, "won": True}

        if player.rolls_left > 0:
            self.phase = "roll"
        else:
            self.end_turn()
        return {"collapsed": collapsed, "won": False}

    def place_on_top(self):
        return self.place_floor(self.current_player().tower.floor_count())

    def check_win(self):
        player = self.current_player()
        if player.tower_height() >= TARGET_HEIGHT:
            self.winner = player
            self.phase = "game_over"
            player.won = True
            self.message = f"{player.name} wins!"
            self._set_feed(
                f"{player.name} wins",
                f"Reached {player.tower_height():.0f} m",
                "Victory",
            )
            return True
        return False

    def end_turn(self):
        if self.phase == "game_over":
            return
        self.current_index = 1 - self.current_index
        player = self.current_player()
        player.reset_rolls()
        self.phase = "roll"
        self.message = self._prompt_roll()
        self._set_feed(
            f"{player.name}'s turn",
            f"Build on the {self.side_hint()} side",
            f"{player.rolls_left} rolls ready",
        )
