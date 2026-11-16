"""UI entry point — fullscreen menu, match board, win screen.

Controls during a match:
  R / ROLL button   → roll a floor
  ↑ / ↓             → move the place arrow
  Enter / Space     → place at the arrow
  Click your tower  → move the arrow to that height
  S / SCRAP button  → discard the current roll
  Esc               → back to menu

Layout:
  left  = text sidebar (turn, last action, heights)
  right = game2dboard grid (towers + buttons)
"""

import tkinter as tk
from tkinter import font as tkfont

from game2dboard import Board

import assets
import screens
from constants import (
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
from game import Game

# Colors shared with screens.py
BG = "#0f1218"
PANEL = "#171a21"
FG = "#f0f2f5"
DIM = "#9aa3b2"
GREEN = "#5ecf8a"
RED = "#d96b6b"
LINE = "#2a2e38"


# ---------------------------------------------------------------------------
# Menu loop
# ---------------------------------------------------------------------------

def run_menu():
    """Fullscreen splash → main menu. Returns 'play' or 'quit'."""
    choice = {"action": "quit"}
    root = tk.Tk()
    root.title("Skyscraper Race")
    root.configure(bg=BG)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _e: root.destroy())

    def play():
        choice["action"] = "play"
        root.destroy()

    def quit_game():
        choice["action"] = "quit"
        root.destroy()

    def howto():
        screens.show_howto(
            root,
            on_back=lambda: screens.show_main_menu(root, play, howto, quit_game),
        )

    screens.show_title_card(
        root,
        title="Skyscraper Race",
        subtitle="Build to 150 meters",
        detail="Strong base · light top · don't collapse",
        on_continue=lambda: screens.show_main_menu(root, play, howto, quit_game),
        btn="Start",
        color=GREEN,
    )
    root.mainloop()
    return choice["action"]


# ---------------------------------------------------------------------------
# Match
# ---------------------------------------------------------------------------

def run_match():
    """One full game. Returns 'play' (again), 'menu', or 'quit'."""
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

    # Mutable UI state (closures below read/write this)
    ui = {
        "cursor": 0,       # insert slot: 0 = ground, N = on top
        "result": "menu",  # what to do when the match window closes
        "ended": False,
        "info": None,      # sidebar Label, set in on_start
    }

    # --- cursor helpers ---

    def clamp_cursor():
        n = game.current_player().tower.floor_count()
        ui["cursor"] = max(0, min(ui["cursor"], n))

    def reset_cursor_to_top():
        ui["cursor"] = game.current_player().tower.floor_count()

    # --- sidebar text ---

    def sidebar_text():
        p1, p2 = game.players
        cur = game.current_player()
        feed = game.feed
        nxt = cur.next_challenge()

        if game.phase == "roll":
            phase = "Press R to roll"
        elif game.phase == "place":
            phase = f"Arrow at slot {ui['cursor']}  ·  Enter to place"
        else:
            phase = "Game over"

        lines = [
            "SKYSCRAPER RACE",
            "",
            f"Turn   {cur.name}  ({game.side_hint()})",
            f"Do     {phase}",
            f"Rolls  {cur.rolls_remaining} left",
            "",
            "— last action —",
            feed["headline"],
            feed["detail"],
            "",
            "— result —",
            feed["result"],
        ]
        if feed.get("events"):
            lines += ["", "— challenge —"] + list(feed["events"])

        lines += [
            "",
            "— height —",
            f"P1   {p1.tower_height():.0f} / {TARGET_HEIGHT} m",
            f"P2   {p2.tower_height():.0f} / {TARGET_HEIGHT} m",
            "",
            "— next challenge —",
            f"{nxt} m" if nxt else "None left",
            "",
            "R roll     S scrap",
            "↑↓ arrow   Enter place",
            "Esc menu",
        ]
        return "\n".join(lines)

    def refresh_sidebar():
        if ui["info"] is None:
            return
        color = RED if not game.feed.get("result_ok", True) else FG
        ui["info"].configure(text=sidebar_text(), fg=color)

    # --- drawing ---

    def status_for(player, floor):
        """ok / warn / fail based on safety ratio."""
        ratio = player.tower.safety_ratio(floor)
        if ratio < 1.0:
            return "fail"
        if ratio < 1.5:
            return "warn"
        return "ok"

    def clear_board():
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                board[r][c] = None  # None, not "" — empty string breaks PhotoImage

    def draw_tower(player, cols, active):
        """Paint floors bottom→top; show place arrow when this player is active."""
        floors = player.tower.floors_bottom_up()
        for i, floor in enumerate(floors[:MAX_VISIBLE_FLOORS]):
            row = TOWER_BOTTOM_ROW - i
            board[row][cols[1]] = assets.floor_image(
                floor.material_name,
                floor.height,
                status_for(player, floor),
            )

        if not (active and game.phase == "place"):
            return

        clamp_cursor()
        pos = ui["cursor"]
        row = max(TOWER_TOP_ROW, TOWER_BOTTOM_ROW - pos)
        board[row][cols[0]] = "arrow"
        # Ghost marks the insert slot
        if pos >= len(floors):
            board[row][cols[1]] = "insert_here"
        else:
            board[row][cols[2]] = "insert_here"

    def draw():
        clear_board()
        p1, p2 = game.players

        # Top HUD chips
        board[0][0] = "badge_p1"
        board[0][1] = assets.height_chip(int(p1.tower_height()), (90, 140, 200))
        board[0][4] = "badge_goal"
        board[0][7] = "badge_p2"
        board[0][8] = assets.height_chip(int(p2.tower_height()), (200, 140, 80))

        # Buttons + whose turn
        board[1][4] = "btn_roll"
        board[1][5] = "btn_scrap"
        board[1][0 if game.current_index == 0 else 9] = "badge_you"

        cur = game.current_player()
        if cur.next_challenge():
            board[1][3] = "challenge"
            board[1][6] = assets.height_chip(int(cur.next_challenge()), (180, 70, 70))

        # Preview of the rolled floor waiting to be placed
        if cur.current_roll and game.phase == "place":
            pending = cur.current_roll
            board[1][7] = assets.floor_image(
                pending["material_name"], pending["height"], "ok"
            )

        for c in P1_COLS + P2_COLS:
            board[GROUND_ROW][c] = "ground"

        draw_tower(p1, P1_COLS, active=(game.current_index == 0))
        draw_tower(p2, P2_COLS, active=(game.current_index == 1))
        refresh_sidebar()

    # --- win / feedback ---

    def finish_match():
        if ui["ended"]:
            return
        ui["ended"] = True
        winner = game.winner
        name = winner.name if winner else "?"
        height = winner.tower_height() if winner else 0.0

        def close(action):
            ui["result"] = action
            board._root.destroy()

        # Replace the whole window with the win card
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

    def flash(msg):
        """Show a short error in the sidebar without changing game state."""
        game.feed["result"] = msg
        game.feed["result_ok"] = False
        refresh_sidebar()

    def row_to_pos(row):
        """Board row → insert slot index (None if outside the tower area)."""
        if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
            return None
        idx = TOWER_BOTTOM_ROW - row
        n = game.current_player().tower.floor_count()
        return n if idx >= n else idx

    # --- input ---

    def on_click(_btn, row, col):
        if game.phase == "game_over":
            return
        try:
            if row == 1 and col == 4:          # ROLL
                game.roll()
                reset_cursor_to_top()
            elif row == 1 and col == 5:        # SCRAP
                game.scrap_roll()
                reset_cursor_to_top()
            elif game.phase == "place":
                my_cols = P1_COLS if game.current_index == 0 else P2_COLS
                their_cols = P2_COLS if game.current_index == 0 else P1_COLS
                if col in their_cols:
                    flash(f"Use the {game.side_hint()} tower")
                    return
                if col in my_cols:
                    pos = row_to_pos(row)
                    if pos is None:
                        return
                    ui["cursor"] = pos
                    draw()
                    return
            after_action()
        except RuntimeError as err:
            flash(str(err))

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
        except RuntimeError as err:
            flash(str(err))

    def on_start():
        """Build the left sidebar next to the board canvas."""
        root = board._root
        try:
            root.attributes("-fullscreen", True)
        except tk.TclError:
            root.geometry("1280x900")
        root.configure(bg=BG)

        # Pack canvas as a root sibling (packing into a frame blanks game2dboard)
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


# ---------------------------------------------------------------------------
# App loop
# ---------------------------------------------------------------------------

def main():
    assets.ensure_assets()
    action = run_menu()
    while action == "play":
        action = run_match()
        if action == "menu":
            action = run_menu()
        elif action != "play":
            break


if __name__ == "__main__":
    main()
