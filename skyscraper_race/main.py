"""Skyscraper Race Lite — simple fullscreen UI + place arrow.

Controls: R roll · ↑↓ move arrow · Enter place · S scrap · Esc menu
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

BG = "#111318"
PANEL = "#171a21"
FG = "#f2f2f2"
DIM = "#a0a4ae"
GREEN = "#6bcb8b"
RED = "#e07070"
LINE = "#2a2e38"


def run_menu():
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
        screens.show_howto(
            root, lambda: screens.show_main_menu(root, go_play, go_howto, go_quit)
        )

    screens.show_title_card(
        root,
        "SKYSCRAPER RACE",
        "Build to 150 meters",
        "Strong base. Light top. Don't collapse.",
        lambda: screens.show_main_menu(root, go_play, go_howto, go_quit),
        btn="START",
        color=GREEN,
    )
    root.mainloop()
    return result["action"]


def run_match():
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
        "info": None,  # one Text widget for the whole sidebar
    }

    def clamp_cursor():
        n = game.current_player().tower.floor_count()
        ui["cursor"] = max(0, min(ui["cursor"], n))

    def reset_cursor_to_top():
        ui["cursor"] = game.current_player().tower.floor_count()

    def sidebar_text():
        p1, p2 = game.players
        cur = game.current_player()
        f = game.feed
        nxt = cur.next_challenge()
        phase = {
            "roll": "Roll a floor (R)",
            "place": f"Place at slot {ui['cursor']}  (↑↓ then Enter)",
            "game_over": "Game over",
        }[game.phase]

        lines = [
            "SKYSCRAPER RACE",
            "",
            f"Turn:  {cur.name} ({game.side_hint()})",
            f"Do:    {phase}",
            f"Rolls: {cur.rolls_remaining} left",
            "",
            "——— last action ———",
            f["headline"],
            f["detail"],
            "",
            "——— result ———",
            f["result"],
        ]
        if f.get("events"):
            lines.append("")
            lines.append("——— challenge ———")
            lines.extend(f["events"])
        lines += [
            "",
            "——— height ———",
            f"P1   {p1.tower_height():.0f} / {TARGET_HEIGHT} m",
            f"P2   {p2.tower_height():.0f} / {TARGET_HEIGHT} m",
            "",
            "——— next challenge ———",
            f"{nxt} m" if nxt else "None left",
            "",
            "R roll   S scrap",
            "↑↓ arrow   Enter place",
            "Esc menu",
        ]
        return "\n".join(lines)

    def refresh_sidebar():
        if ui["info"] is None:
            return
        color = FG
        if not game.feed.get("result_ok", True):
            color = RED
        elif game.phase == "place":
            color = FG
        ui["info"].configure(text=sidebar_text(), fg=color)

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
        for i, floor in enumerate(floors[:MAX_VISIBLE_FLOORS]):
            row = TOWER_BOTTOM_ROW - i
            board[row][cols[1]] = assets.floor_image(
                floor.material_name, floor.height, status_for(player, floor)
            )
        if not (active and game.phase == "place"):
            return
        clamp_cursor()
        pos = ui["cursor"]
        row = max(TOWER_TOP_ROW, TOWER_BOTTOM_ROW - pos)
        board[row][cols[0]] = "arrow"
        if pos >= n:
            board[row][cols[1]] = "insert_here"
        else:
            board[row][cols[2]] = "insert_here"

    def draw():
        clear()
        p1, p2 = game.players
        board[0][0] = "badge_p1"
        board[0][1] = assets.height_chip(int(p1.tower_height()), (90, 140, 200))
        board[0][4] = "badge_goal"
        board[0][7] = "badge_p2"
        board[0][8] = assets.height_chip(int(p2.tower_height()), (200, 140, 80))
        board[1][4] = "btn_roll"
        board[1][5] = "btn_scrap"
        board[1][0 if game.current_index == 0 else 9] = "badge_you"

        cur = game.current_player()
        if cur.next_challenge():
            board[1][3] = "challenge"
            board[1][6] = assets.height_chip(int(cur.next_challenge()), (180, 70, 70))
        pending = cur.current_roll
        if pending and game.phase == "place":
            board[1][7] = assets.floor_image(
                pending["material_name"], pending["height"], "ok"
            )
        for c in P1_COLS + P2_COLS:
            board[GROUND_ROW][c] = "ground"
        draw_tower(p1, P1_COLS, game.current_index == 0)
        draw_tower(p2, P2_COLS, game.current_index == 1)
        refresh_sidebar()

    def finish_match():
        if ui["ended"]:
            return
        ui["ended"] = True
        winner = game.winner
        name = winner.name if winner else "?"
        height = winner.tower_height() if winner else 0

        def close(action):
            ui["result"] = action
            board._root.destroy()

        root = board._root
        for w in root.winfo_children():
            w.destroy()
        screens.show_win_card(
            root, name, height,
            on_again=lambda: close("play"),
            on_menu=lambda: close("menu"),
        )

    def after_action():
        draw()
        if game.phase == "game_over":
            board._root.after(400, finish_match)

    def row_to_pos(row):
        if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
            return None
        idx = TOWER_BOTTOM_ROW - row
        n = game.current_player().tower.floor_count()
        return n if idx >= n else idx

    def flash(msg):
        game.feed["result"] = msg
        game.feed["result_ok"] = False
        refresh_sidebar()

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
                    flash(f"Use the {game.side_hint()} tower")
                    return
                if col in cols:
                    pos = row_to_pos(row)
                    if pos is None:
                        return
                    ui["cursor"] = pos
                    draw()
                    return
            after_action()
        except RuntimeError as e:
            flash(str(e))

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
                if game.phase == "place":
                    clamp_cursor()
                    game.place_floor(ui["cursor"])
                    reset_cursor_to_top()
                else:
                    flash("Roll first (R)")
                    return
            after_action()
        except RuntimeError as e:
            flash(str(e))

    def on_start():
        root = board._root
        try:
            root.attributes("-fullscreen", True)
        except tk.TclError:
            root.geometry("1280x900")
        root.configure(bg=BG)

        # Detach canvas, then pack: sidebar | board (siblings under root)
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

        # Thin divider
        tk.Frame(root, bg=LINE, width=1).pack(side="left", fill="y")

        # Pack the game2dboard canvas next to the sidebar (same parent = root)
        board._canvas.configure(bg=BG, highlightthickness=0)
        board._canvas.pack(side="left", padx=24, pady=24)

        root.update_idletasks()
        draw()

    board.on_start = on_start
    board.on_mouse_click = on_click
    board.on_key_press = on_key
    board.show()
    return ui["result"]


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
