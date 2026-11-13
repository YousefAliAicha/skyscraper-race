"""Skyscraper Race Lite — fullscreen game with menu + place arrow.

Controls in match:
  R            roll
  S            scrap
  ↑ / ↓        move place arrow
  Enter/Space  place at arrow
  click tower  move arrow to that row
  Esc          quit to menu
"""

import tkinter as tk
from tkinter import font as tkfont

from game2dboard import Board

import assets
import screens
from constants import (
    BOARD_COLS, BOARD_ROWS, CELL_SIZE, GROUND_ROW, TARGET_HEIGHT,
    P1_COLS, P2_COLS, TOWER_BOTTOM_ROW, TOWER_TOP_ROW, MAX_VISIBLE_FLOORS,
)
from game import Game

BG = "#0b1020"
FG = "#e8eef8"
ACCENT = "#3dd68c"


def run_menu():
    """Fullscreen menu. Returns 'play' or 'quit'."""
    result = {"action": "quit"}
    root = tk.Tk()
    root.title("Skyscraper Race")
    root.configure(bg=BG)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.destroy())

    def go_play():
        result["action"] = "play"
        root.destroy()

    def go_quit():
        result["action"] = "quit"
        root.destroy()

    def go_howto():
        screens.show_howto(root, lambda: screens.show_main_menu(
            root, go_play, go_howto, go_quit
        ))

    def after_splash():
        screens.show_main_menu(root, go_play, go_howto, go_quit)

    screens.show_title_card(
        root,
        "SKYSCRAPER RACE",
        "Lite Edition",
        "A DSA board game  ·  Linked lists, heaps, recursion",
        after_splash,
        btn="PRESS START",
        color=ACCENT,
    )
    root.mainloop()
    return result["action"]


def run_match():
    """Play one match on game2dboard. Returns 'menu' or 'quit'."""
    assets.ensure_assets()
    game = Game("P1", "P2")
    board = Board(BOARD_ROWS, BOARD_COLS)
    board.cell_size = CELL_SIZE
    board.title = "Skyscraper Race Lite"
    board.margin = 10
    board.cell_spacing = 3
    board.margin_color = BG
    board.cell_color = "#101a2b"
    board.grid_color = "#18253a"
    board.background_image = "bg"
    # No create_output — we use a real HUD instead

    state = {
        "cursor": 0,          # insert index 0..n
        "status": None,       # tk Label
        "meta": None,         # tk Label (heights)
        "result": "menu",
        "ended": False,
    }

    def clamp_cursor():
        n = game.current_player().tower.floor_count()
        max_pos = min(n, MAX_VISIBLE_FLOORS - 1) if n >= MAX_VISIBLE_FLOORS else n
        # allow 0..n inclusive (n = place on top)
        state["cursor"] = max(0, min(state["cursor"], n))

    def reset_cursor_to_top():
        state["cursor"] = game.current_player().tower.floor_count()

    def set_status(text, color=FG):
        if state["status"] is not None:
            state["status"].configure(text=text, fg=color)

    def set_meta():
        if state["meta"] is None:
            return
        p1, p2 = game.players
        cur = game.current_player()
        nxt = cur.next_challenge()
        ch = f"   next challenge {nxt}m" if nxt else ""
        phase = {
            "roll": "ROLL a floor",
            "place": f"PLACE with ↑↓ then Enter  (slot {state['cursor']})",
            "game_over": "MATCH OVER",
        }.get(game.phase, "")
        state["meta"].configure(
            text=(
                f"P1  {p1.tower_height():.0f}m/{TARGET_HEIGHT}m    "
                f"P2  {p2.tower_height():.0f}m/{TARGET_HEIGHT}m    "
                f"Turn {cur.name}  rolls×{cur.rolls_remaining}    "
                f"{phase}{ch}"
            )
        )

    def status_for(player, floor):
        r = player.tower.safety_ratio(floor)
        if r < 1.0:
            return "fail"
        if r < 1.5:
            return "warn"
        return "ok"

    def clear():
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                board[r][c] = None

    def draw_tower(player, cols, active):
        floors = player.tower.floors_bottom_up()
        n = len(floors)
        slots = MAX_VISIBLE_FLOORS
        for i, floor in enumerate(floors[:slots]):
            row = TOWER_BOTTOM_ROW - i
            board[row][cols[1]] = assets.floor_image(
                floor.material_name, floor.height, status_for(player, floor)
            )

        if not (active and game.phase == "place"):
            return

        clamp_cursor()
        pos = state["cursor"]
        row = TOWER_BOTTOM_ROW - pos
        if row < TOWER_TOP_ROW:
            row = TOWER_TOP_ROW
        # Arrow in the outer column, ghost on the insert cell
        board[row][cols[0]] = "arrow"
        if pos >= n:
            board[row][cols[1]] = "insert_here"
        else:
            # inserting into existing band — mark center as HERE overlay feel
            board[row][cols[2]] = "insert_here"

    def draw():
        clear()
        p1, p2 = game.players
        board[0][0] = "badge_p1"
        board[0][1] = assets.height_chip(int(p1.tower_height()), (80, 140, 220))
        board[0][4] = "badge_goal"
        board[0][7] = "badge_p2"
        board[0][8] = assets.height_chip(int(p2.tower_height()), (220, 140, 70))
        board[1][4] = "btn_roll"
        board[1][5] = "btn_scrap"
        if game.current_index == 0:
            board[1][0] = "badge_you"
        else:
            board[1][9] = "badge_you"

        cur = game.current_player()
        if cur.next_challenge():
            board[1][3] = "challenge"
            board[1][6] = assets.height_chip(int(cur.next_challenge()), (200, 70, 70))

        pending = cur.current_roll
        if pending and game.phase == "place":
            board[1][7] = assets.floor_image(
                pending["material_name"], pending["height"], "ok"
            )

        for c in P1_COLS + P2_COLS:
            board[GROUND_ROW][c] = "ground"

        draw_tower(p1, P1_COLS, game.current_index == 0)
        draw_tower(p2, P2_COLS, game.current_index == 1)

        color = FG
        msg = game.message
        if "COLLAPSE" in msg:
            color = "#e85d5d"
        elif "WINS" in msg:
            color = ACCENT
        elif game.phase == "place":
            color = ACCENT
        set_status(msg, color)
        set_meta()

    def finish_match():
        if state["ended"]:
            return
        state["ended"] = True
        winner = game.winner
        height = winner.tower_height() if winner else 0
        name = winner.name if winner else "?"

        def close_board_and(action):
            state["result"] = action
            board._root.destroy()

        # Replace board UI with victory card on same root
        root = board._root
        for w in root.winfo_children():
            w.destroy()
        screens.show_win_card(
            root,
            name,
            height,
            on_again=lambda: close_board_and("play"),
            on_menu=lambda: close_board_and("menu"),
        )

    def after_action():
        draw()
        if game.phase == "game_over":
            board._root.after(350, finish_match)

    def row_to_pos(row):
        if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
            return None
        idx = TOWER_BOTTOM_ROW - row
        n = game.current_player().tower.floor_count()
        return n if idx >= n else idx

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
                cols = P1_COLS if game.current_index == 0 else P2_COLS
                other = P2_COLS if game.current_index == 0 else P1_COLS
                if col in other:
                    set_status(f"Wrong tower — use the {game.side_hint()} side", "#e85d5d")
                    return
                if col in cols:
                    pos = row_to_pos(row)
                    if pos is None:
                        return
                    # Click moves the arrow to that row (does not place yet)
                    state["cursor"] = pos
                    set_status(
                        f"Arrow at slot {pos} — press Enter to place",
                        ACCENT,
                    )
                    draw()
                    return
            after_action()
        except RuntimeError as e:
            set_status(str(e), "#e85d5d")

    def on_key(key):
        if game.phase == "game_over":
            return
        try:
            if key in ("Escape", "Esc"):
                state["result"] = "menu"
                board._root.destroy()
                return

            if key in ("r", "R"):
                game.roll()
                reset_cursor_to_top()
            elif key in ("s", "S"):
                game.scrap_roll()
                reset_cursor_to_top()
            elif key in ("Up",):
                if game.phase == "place":
                    state["cursor"] += 1
                    clamp_cursor()
                    draw()
                    return
            elif key in ("Down",):
                if game.phase == "place":
                    state["cursor"] -= 1
                    clamp_cursor()
                    draw()
                    return
            elif key in ("space", "Return", " ", "KP_Enter"):
                if game.phase == "place":
                    clamp_cursor()
                    game.place_floor(state["cursor"])
                    reset_cursor_to_top()
                elif game.phase == "roll":
                    set_status("Roll first (R)", "#f0b429")
                    return
            after_action()
        except RuntimeError as e:
            set_status(str(e), "#e85d5d")

    def on_start():
        root = board._root
        try:
            root.attributes("-fullscreen", True)
        except tk.TclError:
            root.geometry("1100x900")
        root.configure(bg=BG)

        # Rebuild layout: HUD on top, board, help bar
        board._canvas.pack_forget()

        top = tk.Frame(root, bg=BG)
        top.pack(side="top", fill="x")

        title_font = tkfont.Font(family="DejaVu Sans", size=18, weight="bold")
        body_font = tkfont.Font(family="DejaVu Sans", size=15)
        small = tkfont.Font(family="DejaVu Sans", size=12)

        tk.Label(
            top,
            text="SKYSCRAPER RACE",
            font=title_font,
            bg=BG,
            fg=ACCENT,
            pady=6,
        ).pack()

        state["meta"] = tk.Label(
            top, text="", font=small, bg="#121a2c", fg="#9eb0c8", pady=8
        )
        state["meta"].pack(fill="x")

        state["status"] = tk.Label(
            top,
            text=game.message,
            font=body_font,
            bg="#162033",
            fg=FG,
            pady=14,
            wraplength=1000,
            justify="center",
        )
        state["status"].pack(fill="x", padx=0, pady=(0, 4))

        board._canvas.pack(side="top", expand=True)

        tk.Label(
            root,
            text="↑↓ move arrow   ·   Enter / Space place   ·   R roll   ·   S scrap   ·   Esc menu",
            font=small,
            bg=BG,
            fg="#7f8ea3",
            pady=10,
        ).pack(side="bottom", fill="x")

        draw()

    board.on_start = on_start
    board.on_mouse_click = on_click
    board.on_key_press = on_key
    # Pre-draw values before show so cells exist after setup
    # (actual draw runs in on_start)
    board.show()
    return state["result"]


def main():
    assets.ensure_assets()
    action = run_menu()
    while action == "play":
        action = run_match()
        if action == "play":
            continue
        if action == "menu":
            action = run_menu()
        else:
            break


if __name__ == "__main__":
    main()
