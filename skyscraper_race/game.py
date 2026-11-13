"""Turn loop: roll → place/scrap → challenges → stability → win."""

from challenges import process_challenges
from constants import ROLLS_PER_TURN, TARGET_HEIGHT
from player import Player
from roll import full_decode, generate_roll
from tower import Floor


class Game:
    def __init__(self, name1="P1", name2="P2", enable_challenges=True):
        self.players = [Player(name1, ROLLS_PER_TURN), Player(name2, ROLLS_PER_TURN)]
        self.current_index = 0
        self.phase = "roll"
        self.winner = None
        self.last_collapse = None
        self.last_events = []
        self.enable_challenges = enable_challenges
        self.feed = {
            "headline": "Match start",
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
        p = self.current_player()
        return f"{p.name}'s turn — roll a floor"

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
        p = self.current_player()
        if p.rolls_remaining <= 0:
            raise RuntimeError("No rolls left")
        decoded = full_decode(generate_roll())
        p.current_roll = decoded
        p.rolls_remaining -= 1
        self.phase = "place"
        tip = "Keep on TOP or scrap" if decoded["tier"] == "junk" else (
            "Good for the BASE" if decoded["tier"] == "strong" else "Place with ↑↓"
        )
        self.message = f"Rolled {decoded['material_name']} {decoded['height']}m"
        self._set_feed(
            f"Rolled {decoded['material_name'].upper()}",
            f"{decoded['height']} m tall  ·  {tip}",
            result="Choose height with ↑↓",
            result_ok=True,
        )
        return decoded

    def scrap_roll(self):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("Nothing to scrap")
        p = self.current_player()
        p.current_roll = None
        self._set_feed("Scrapped", "Roll discarded", "OK", True)
        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message = self._prompt_roll()
        else:
            self.end_turn()

    def place_floor(self, position: int):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("ROLL first")
        p = self.current_player()
        decoded = p.current_roll
        pos = max(0, min(position, p.tower.floor_count()))
        p.tower.insert_at(pos, Floor(decoded))
        p.current_roll = None
        self.last_collapse = None
        self.last_events = []

        events = []
        if self.enable_challenges:
            events, _ = process_challenges(p.tower, p.challenge_heap)
            self.last_events = events

        collapsed = self._resolve_stability(p)
        height = p.tower_height()
        if collapsed:
            fallen, lost = self.last_collapse
            self._set_feed(
                f"Placed {decoded['material_name'].upper()} {decoded['height']}m",
                f"Slot {pos}  ·  tower now {height:.0f} m",
                result=f"COLLAPSE  −{len(fallen)} floors  (−{lost:.0f} m)",
                result_ok=False,
                events=events,
            )
            self.message = f"Collapse! tower {height:.0f}m"
        else:
            self._set_feed(
                f"Placed {decoded['material_name'].upper()} {decoded['height']}m",
                f"Slot {pos}  ·  tower now {height:.0f} m",
                result="Stable",
                result_ok=True,
                events=events,
            )
            self.message = f"Placed — {height:.0f}m"

        if self.check_win():
            return {"collapsed": collapsed, "won": True}

        if p.rolls_remaining > 0:
            self.phase = "roll"
        else:
            self.end_turn()
        return {"collapsed": collapsed, "won": False}

    def place_on_top(self):
        return self.place_floor(self.current_player().tower.floor_count())

    def _resolve_stability(self, player):
        ratio, weakest = player.tower.check_stability()
        if weakest is not None and ratio < 1.0:
            fallen, lost = player.tower.collapse(weakest)
            self.last_collapse = (fallen, lost)
            return True
        return False

    def check_win(self):
        p = self.current_player()
        if p.tower_height() >= TARGET_HEIGHT:
            self.winner = p
            self.phase = "game_over"
            p.won = True
            self.message = f"{p.name} wins!"
            self._set_feed(
                f"{p.name} WINS",
                f"Tower reached {p.tower_height():.0f} m",
                result="Victory",
                result_ok=True,
            )
            return True
        return False

    def end_turn(self):
        if self.phase == "game_over":
            return
        self.current_index = 1 - self.current_index
        self.current_player().reset_rolls()
        self.phase = "roll"
        self.message = self._prompt_roll()
        p = self.current_player()
        self._set_feed(
            f"{p.name}'s turn",
            f"Build on the {self.side_hint()} tower",
            result=f"{p.rolls_remaining} rolls ready",
            result_ok=True,
        )
