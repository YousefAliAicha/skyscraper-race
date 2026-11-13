"""Turn loop: roll → place/scrap → challenges → stability → win."""

from challenges import process_challenges, requeue_below
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
        self.message = self._prompt_roll()

    def current_player(self):
        return self.players[self.current_index]

    def side_hint(self):
        return "LEFT" if self.current_index == 0 else "RIGHT"

    def _prompt_roll(self):
        p = self.current_player()
        nxt = p.next_challenge()
        ch = f" next⚠{nxt}m" if nxt else ""
        return (
            f"{p.name} ({self.side_hint()}) — ROLL/R  "
            f"[{p.rolls_remaining} left]{ch}"
        )

    def roll(self):
        if self.phase == "game_over":
            raise RuntimeError("Game over — restart the app")
        if self.phase != "roll":
            raise RuntimeError("Place (Space) or Scrap first")
        p = self.current_player()
        if p.rolls_remaining <= 0:
            raise RuntimeError("No rolls left")
        decoded = full_decode(generate_roll())
        p.current_roll = decoded
        p.rolls_remaining -= 1
        self.phase = "place"
        self.message = (
            f"{p.name}: {decoded['material_name'].upper()} {decoded['height']}m  "
            f"— Space=TOP · click {self.side_hint()} · S=scrap"
        )
        return decoded

    def scrap_roll(self):
        if self.phase != "place" or not self.current_player().current_roll:
            raise RuntimeError("Nothing to scrap")
        p = self.current_player()
        p.current_roll = None
        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message = f"Scrapped. {self._prompt_roll()}"
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

        notes = [
            f"+{decoded['material_name']} {decoded['height']}m → {p.tower_height():.0f}m"
        ]

        # Challenges when tower crosses hidden heights
        if self.enable_challenges:
            events, _ = process_challenges(p.tower, p.challenge_heap)
            self.last_events = events
            notes.extend(events)

        # Stability after place + damage
        collapsed = self._resolve_stability(p)
        if collapsed:
            notes.append(
                f"COLLAPSE -{len(self.last_collapse[0])}floors/"
                f"{self.last_collapse[1]:.0f}m"
            )
            if self.enable_challenges:
                requeue_below(
                    p.challenge_heap, p.challenge_heights, p.tower_height()
                )

        self.message = " · ".join(notes) + f" /{TARGET_HEIGHT}m"

        if self.check_win():
            return {"collapsed": collapsed, "won": True}

        if p.rolls_remaining > 0:
            self.phase = "roll"
            self.message += f" — ROLL [{p.rolls_remaining}]"
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
            self.message = f"{p.name} WINS at {p.tower_height():.0f}m!"
            return True
        return False

    def end_turn(self):
        if self.phase == "game_over":
            return
        self.current_index = 1 - self.current_index
        self.current_player().reset_rolls()
        self.phase = "roll"
        self.message = f"Turn → {self._prompt_roll()}"
