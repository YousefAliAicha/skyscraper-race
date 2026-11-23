"""One match window: left text sidebar + right game board.

Controls:
  R / ROLL     roll a floor
  ↑ / ↓        move the place arrow
  Enter/Space  place at the arrow
  Click tower  move the arrow
  S / SCRAP    discard the roll
  Esc          back to menu
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tkinter as tk
from tkinter import font as tkfont

from game2dboard import Board

from game import assets, screens
from logic.algorithms.game import Game
from logic.data.constants import (
    BOARD_COLS,
    BOARD_ROWS,
    CELL_SIZE,
    GROUND_ROW,
    MAX_VISIBLE_FLOORS,
    P1_COLS,
    P2_COLS,
    TARGET_HEIGHT,
    TOWER_BOTTOM_ROW,
    TOWER_TOP_ROW,
)

BG = "#0f1218"
PANEL = "#171a21"
FG = "#f0f2f5"
RED = "#d96b6b"
LINE = "#2a2e38"


def run_match():
    """Play one game. Returns 'play', 'menu', or 'quit'."""
    assets.ensure_assets()
    game = Game("P1", "P2")

    board = Board(BOARD_ROWS, BOARD_COLS)
    board.cell_size = CELL_SIZE
    board.title = "Skyscraper Race"
    board.margin = 8
    board.cell_spacing = 2
    board.margin_color = BG
    board.cell_color = "#1c2030"
    board.grid_color = "#2a3144"
    board.background_image = "bg"

    ui = {
        "cursor": 0,
        "result": "menu",
        "ended": False,
        "info": None,
    }

    # --- cursor ---

    def clamp_cursor():
        max_slot = game.current_player().tower.floor_count()
        if ui["cursor"] < 0:
            ui["cursor"] = 0
        if ui["cursor"] > max_slot:
            ui["cursor"] = max_slot

    def reset_cursor_to_top():
        ui["cursor"] = game.current_player().tower.floor_count()

    # --- sidebar text ---

    def sidebar_text():
        player1 = game.players[0]
        player2 = game.players[1]
        current = game.current_player()
        feed = game.feed
        next_height = current.next_challenge()

        if game.phase == "roll":
            phase_line = "Press R to roll"
        elif game.phase == "place":
            phase_line = (
                f"Arrow at slot {ui['cursor']}"
                "  ·  Enter to place"
            )
        else:
            phase_line = "Game over"

        lines = [
            "SKYSCRAPER RACE",
            "",
            f"Turn   {current.name}  ({game.side_hint()})",
            f"Do     {phase_line}",
            f"Rolls  {current.rolls_left} left",
            "",
            "— last action —",
            feed["headline"],
            feed["detail"],
            "",
            "— result —",
            feed["result"],
        ]

        if feed.get("events"):
            lines.append("")
            lines.append("— challenge —")
            lines.extend(feed["events"])

        lines.append("")
        lines.append("— height —")
        lines.append(
            f"P1   {player1.tower_height():.0f} / {TARGET_HEIGHT} m"
        )
        lines.append(
            f"P2   {player2.tower_height():.0f} / {TARGET_HEIGHT} m"
        )
        lines.append("")
        lines.append("— next challenge —")
        if next_height:
            lines.append(f"{next_height} m")
        else:
            lines.append("None left")

        lines.append("")
        lines.append("R roll     S scrap")
        lines.append("↑↓ arrow   Enter place")
        lines.append("Esc menu")
        return "\n".join(lines)

    def refresh_sidebar():
        if ui["info"] is None:
            return
        if game.feed.get("result_ok", True):
            color = FG
        else:
            color = RED
        ui["info"].configure(text=sidebar_text(), fg=color)

    # --- drawing ---

    def floor_status(player, index):
        ratio = player.tower.hold_ratio(index)
        if ratio < 1.0:
            return "fail"
        if ratio < 1.5:
            return "warn"
        return "ok"

    def clear_board():
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                # None, not "" — empty string breaks PhotoImage
                board[row][col] = None

    def draw_tower(player, cols, active):
        floors = player.tower.floors_from_ground()

        for index, floor in enumerate(floors[:MAX_VISIBLE_FLOORS]):
            row = TOWER_BOTTOM_ROW - index
            board[row][cols[1]] = assets.floor_image(
                floor.material_name,
                floor.height,
                floor_status(player, index),
            )

        if not (active and game.phase == "place"):
            return

        clamp_cursor()
        slot = ui["cursor"]
        row = max(TOWER_TOP_ROW, TOWER_BOTTOM_ROW - slot)
        board[row][cols[0]] = "arrow"

        if slot >= len(floors):
            board[row][cols[1]] = "insert_here"
        else:
            board[row][cols[2]] = "insert_here"

    def draw():
        clear_board()
        player1 = game.players[0]
        player2 = game.players[1]

        board[0][0] = "badge_p1"
        board[0][1] = assets.height_chip(
            int(player1.tower_height()),
            (90, 140, 200),
        )
        board[0][4] = "badge_goal"
        board[0][7] = "badge_p2"
        board[0][8] = assets.height_chip(
            int(player2.tower_height()),
            (200, 140, 80),
        )

        board[1][4] = "btn_roll"
        board[1][5] = "btn_scrap"
        if game.current_index == 0:
            board[1][0] = "badge_you"
        else:
            board[1][9] = "badge_you"

        current = game.current_player()
        next_height = current.next_challenge()
        if next_height:
            board[1][3] = "challenge"
            board[1][6] = assets.height_chip(
                int(next_height),
                (180, 70, 70),
            )

        if current.pending_roll and game.phase == "place":
            recipe = current.pending_roll
            board[1][7] = assets.floor_image(
                recipe["material_name"],
                recipe["height"],
                "ok",
            )

        for col in P1_COLS + P2_COLS:
            board[GROUND_ROW][col] = "ground"

        draw_tower(player1, P1_COLS, active=(game.current_index == 0))
        draw_tower(player2, P2_COLS, active=(game.current_index == 1))
        refresh_sidebar()

    # --- win / errors ---

    def finish_match():
        if ui["ended"]:
            return
        ui["ended"] = True

        winner = game.winner
        if winner:
            name = winner.name
            height = winner.tower_height()
        else:
            name = "?"
            height = 0.0

        def close(action):
            ui["result"] = action
            board._root.destroy()

        root = board._root
        for child in root.winfo_children():
            child.destroy()

        screens.show_win_card(
            root,
            winner_name=name,
            height=height,
            on_again=lambda: close("play"),
            on_menu=lambda: close("menu"),
        )

    def after_action():
        draw()
        if game.phase == "game_over":
            board._root.after(400, finish_match)

    def flash(message):
        game.feed["result"] = message
        game.feed["result_ok"] = False
        refresh_sidebar()

    def row_to_slot(row):
        if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
            return None
        index = TOWER_BOTTOM_ROW - row
        floor_count = game.current_player().tower.floor_count()
        if index >= floor_count:
            return floor_count
        return index

    # --- input ---

    def on_click(_btn, row, col):
        if game.phase == "game_over":
            return
        try:
            if row == 1 and col == 4:
                game.roll()
                reset_cursor_to_top()
            elif row == 1 and col == 5:
                game.scrap_roll()
                reset_cursor_to_top()
            elif game.phase == "place":
                if game.current_index == 0:
                    my_cols = P1_COLS
                    their_cols = P2_COLS
                else:
                    my_cols = P2_COLS
                    their_cols = P1_COLS

                if col in their_cols:
                    flash(f"Use the {game.side_hint()} tower")
                    return

                if col in my_cols:
                    slot = row_to_slot(row)
                    if slot is None:
                        return
                    ui["cursor"] = slot
                    draw()
                    return

            after_action()
        except RuntimeError as error:
            flash(str(error))

    def on_key(key):
        if game.phase == "game_over":
            return
        try:
            if key in ("Escape", "Esc"):
                ui["result"] = "menu"
                board._root.destroy()
                return

            if key in ("r", "R"):
                game.roll()
                reset_cursor_to_top()
            elif key in ("s", "S"):
                game.scrap_roll()
                reset_cursor_to_top()
            elif key == "Up" and game.phase == "place":
                ui["cursor"] += 1
                clamp_cursor()
                draw()
                return
            elif key == "Down" and game.phase == "place":
                ui["cursor"] -= 1
                clamp_cursor()
                draw()
                return
            elif key in ("space", "Return", " ", "KP_Enter"):
                if game.phase != "place":
                    flash("Roll first (R)")
                    return
                clamp_cursor()
                game.place_floor(ui["cursor"])
                reset_cursor_to_top()

            after_action()
        except RuntimeError as error:
            flash(str(error))

    def on_start():
        root = board._root
        try:
            root.attributes("-fullscreen", True)
        except tk.TclError:
            root.geometry("1280x900")
        root.configure(bg=BG)

        # Pack canvas as a root sibling (packing into a frame blanks it)
        board._canvas.pack_forget()

        side = tk.Frame(root, bg=PANEL, width=300, padx=20, pady=24)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        mono = tkfont.Font(family="DejaVu Sans Mono", size=12)
        ui["info"] = tk.Label(
            side,
            text="",
            font=mono,
            bg=PANEL,
            fg=FG,
            justify="left",
            anchor="nw",
        )
        ui["info"].pack(fill="both", expand=True)

        tk.Frame(root, bg=LINE, width=1).pack(side="left", fill="y")

        board._canvas.configure(bg=BG, highlightthickness=0)
        board._canvas.pack(side="left", padx=24, pady=24)

        root.update_idletasks()
        draw()

    board.on_start = on_start
    board.on_mouse_click = on_click
    board.on_key_press = on_key
    board.show()
    return ui["result"]
