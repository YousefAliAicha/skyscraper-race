"""Turn logic — no GUI. UI calls these methods.

Flow each turn:
  roll → (place or scrap) → challenges → stability/collapse → win check
"""

from challenges import process_challenges
from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import full_decode, generate_roll
from tower import Floor


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
        self.last_events = []
        self.enable_challenges = enable_challenges
        self.message = ""
        self.feed = {}
        self._set_feed(
            f"{self.current_player().name}'s turn",
            "Press R or click ROLL",
            "Waiting",
        )
        self.message = self._prompt_roll()

    # --- helpers ---

    def current_player(self):
        return self.players[self.current_index]

    def side_hint(self):
        return "LEFT" if self.current_index == 0 else "RIGHT"

    def _prompt_roll(self):
        return f"{self.current_player().name}'s turn — roll a floor"

    def _set_feed(self, headline, detail, result="OK", result_ok=True, events=None):
        """Structured status for the sidebar UI."""
        self.feed = {
            "headline": headline,
            "detail": detail,
            "result": result,
            "result_ok": result_ok,
            "events": events or [],
        }

    # --- actions ---

    def roll(self):
        if self.phase == "game_over":
            raise RuntimeError("Game over")
        if self.phase != "roll":
            raise RuntimeError("Place or scrap first")

        player = self.current_player()
        if player.rolls_remaining <= 0:
            raise RuntimeError("No rolls left")

        decoded = full_decode(generate_roll())
        player.current_roll = decoded
        player.rolls_remaining -= 1
        self.phase = "place"

        tip = {
            "junk": "Weak — put on top or scrap",
            "strong": "Strong — good at the bottom",
            "common": "Move the arrow, then press Enter",
        }[decoded["tier"]]

        self.message = f"Rolled {decoded['material_name']} {decoded['height']}m"
        self._set_feed(
            f"Rolled {decoded['material_name']}",
            f"{decoded['height']} m — {tip}",
            "Choose a height",
        )
        return decoded

    def scrap_roll(self):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("Nothing to scrap")

        player = self.current_player()
        player.current_roll = None
        self._set_feed("Scrapped", "That roll was discarded", "OK")

        if player.rolls_remaining > 0:
            self.phase = "roll"
            self.message = self._prompt_roll()
        else:
            self.end_turn()

    def place_floor(self, position: int):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("Roll first")

        player = self.current_player()
        decoded = player.current_roll
        pos = max(0, min(position, player.tower.floor_count()))

        player.tower.insert_at(pos, Floor(decoded))
        player.current_roll = None
        self.last_collapse = None
        self.last_events = []

        events = []
        if self.enable_challenges:
            events, _ = process_challenges(player.tower, player.challenge_heap)
            self.last_events = events

        collapsed = self._resolve_stability(player)
        height = player.tower_height()

        if collapsed:
            fallen, lost = self.last_collapse
            self._set_feed(
                f"Placed {decoded['material_name']} ({decoded['height']} m)",
                f"Slot {pos} → tower {height:.0f} m",
                f"Collapsed — lost {len(fallen)} floors ({lost:.0f} m)",
                result_ok=False,
                events=events,
            )
            self.message = f"Collapse! {height:.0f} m left"
        else:
            self._set_feed(
                f"Placed {decoded['material_name']} ({decoded['height']} m)",
                f"Slot {pos} → tower {height:.0f} m",
                "Stable",
                events=events,
            )
            self.message = f"Placed — {height:.0f} m"

        if self.check_win():
            return {"collapsed": collapsed, "won": True}

        if player.rolls_remaining > 0:
            self.phase = "roll"
        else:
            self.end_turn()
        return {"collapsed": collapsed, "won": False}

    def place_on_top(self):
        return self.place_floor(self.current_player().tower.floor_count())

    def _resolve_stability(self, player):
        ratio, weakest = player.tower.check_stability()
        if weakest is not None and ratio < 1.0:
            self.last_collapse = player.tower.collapse(weakest)
            return True
        return False

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
            f"{player.rolls_remaining} rolls ready",
        )
