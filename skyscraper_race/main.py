"""Skyscraper Race Lite — fullscreen game with left info panel + place arrow.

Controls:
  R            roll
  S            scrap
  ↑ / ↓        move place arrow
  Enter/Space  place at arrow
  click tower  move arrow
  Esc          menu
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
PANEL = "#121a2c"
CARD = "#182338"
FG = "#e8eef8"
MUTED = "#8b9bb4"
ACCENT = "#3dd68c"
WARN = "#f0b429"
DANGER = "#e85d5d"
P1C = "#4d9fff"
P2C = "#f0a05a"


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


def _section(parent, title, fonts):
    box = tk.Frame(parent, bg=CARD, padx=14, pady=12)
    box.pack(fill="x", pady=(0, 12))
    tk.Label(
        box, text=title.upper(), font=fonts["label"], bg=CARD, fg=MUTED, anchor="w"
    ).pack(fill="x", pady=(0, 6))
    return box


def run_match():
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

    ui = {
        "cursor": 0,
        "result": "menu",
        "ended": False,
        # sidebar labels
        "turn": None,
        "phase": None,
        "headline": None,
        "detail": None,
        "outcome": None,
        "events": None,
        "p1_h": None,
        "p2_h": None,
        "p1_bar": None,
        "p2_bar": None,
        "rolls": None,
        "challenge": None,
        "slot": None,
        "bar_w": 200,
    }

    fonts = {}

    def clamp_cursor():
        n = game.current_player().tower.floor_count()
        ui["cursor"] = max(0, min(ui["cursor"], n))

    def reset_cursor_to_top():
        ui["cursor"] = game.current_player().tower.floor_count()

    def progress_fill(bar, ratio, color):
        bar.delete("all")
        w = ui["bar_w"]
        h = 14
        bar.create_rectangle(0, 0, w, h, fill="#0d1422", outline="#2a3a55")
        fill = max(0, min(w, int(w * ratio)))
        if fill:
            bar.create_rectangle(1, 1, fill, h - 1, fill=color, outline="")

    def refresh_sidebar():
        p1, p2 = game.players
        cur = game.current_player()
        feed = game.feed

        ui["turn"].configure(text=f"{cur.name}  ·  {game.side_hint()} tower")
        phase_txt = {
            "roll": "Your move: ROLL",
            "place": "Your move: PLACE",
            "game_over": "Match over",
        }[game.phase]
        ui["phase"].configure(
            text=phase_txt,
            fg=ACCENT if game.phase != "game_over" else MUTED,
        )

        ui["headline"].configure(text=feed["headline"])
        ui["detail"].configure(text=feed["detail"])
        ui["outcome"].configure(
            text=feed["result"],
            fg=ACCENT if feed["result_ok"] else DANGER,
        )
        ev = feed.get("events") or []
        ui["events"].configure(
            text="\n".join(ev) if ev else "No challenge this action",
            fg=WARN if ev else MUTED,
        )

        ui["p1_h"].configure(text=f"{p1.tower_height():.0f} m")
        ui["p2_h"].configure(text=f"{p2.tower_height():.0f} m")
        progress_fill(ui["p1_bar"], p1.tower_height() / TARGET_HEIGHT, P1C)
        progress_fill(ui["p2_bar"], p2.tower_height() / TARGET_HEIGHT, P2C)

        ui["rolls"].configure(text=f"{cur.rolls_remaining} left this turn")
        nxt = cur.next_challenge()
        ui["challenge"].configure(
            text=f"At {nxt} m" if nxt else "None remaining",
            fg=DANGER if nxt else MUTED,
        )

        if game.phase == "place":
            ui["slot"].configure(
                text=f"Arrow → slot {ui['cursor']}\n↑↓ move  ·  Enter place",
                fg=ACCENT,
            )
        else:
            ui["slot"].configure(text="Press R to roll", fg=MUTED)

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
        refresh_sidebar()

    def finish_match():
        if ui["ended"]:
            return
        ui["ended"] = True
        winner = game.winner
        height = winner.tower_height() if winner else 0
        name = winner.name if winner else "?"

        def close_board_and(action):
            ui["result"] = action
            board._root.destroy()

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
            board._root.after(400, finish_match)

    def row_to_pos(row):
        if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
            return None
        idx = TOWER_BOTTOM_ROW - row
        n = game.current_player().tower.floor_count()
        return n if idx >= n else idx

    def flash_error(msg):
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
                    flash_error(f"Use the {game.side_hint()} tower")
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
            flash_error(str(e))

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
                elif game.phase == "roll":
                    flash_error("Roll first (R)")
                    return
            after_action()
        except RuntimeError as e:
            flash_error(str(e))

    def on_start():
        root = board._root
        try:
            root.attributes("-fullscreen", True)
        except tk.TclError:
            root.geometry("1280x900")
        root.configure(bg=BG)

        fonts["title"] = tkfont.Font(family="DejaVu Sans", size=18, weight="bold")
        fonts["label"] = tkfont.Font(family="DejaVu Sans", size=10, weight="bold")
        fonts["body"] = tkfont.Font(family="DejaVu Sans", size=14)
        fonts["big"] = tkfont.Font(family="DejaVu Sans", size=20, weight="bold")
        fonts["huge"] = tkfont.Font(family="DejaVu Sans", size=26, weight="bold")
        fonts["small"] = tkfont.Font(family="DejaVu Sans", size=11)

        board._canvas.pack_forget()

        # --- body: left sidebar + board ---
        body = tk.Frame(root, bg=BG)
        body.pack(side="top", fill="both", expand=True)

        side = tk.Frame(body, bg=PANEL, width=320, padx=18, pady=18)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(
            side, text="SKYSCRAPER", font=fonts["title"], bg=PANEL, fg=ACCENT
        ).pack(anchor="w")
        tk.Label(
            side, text="RACE", font=fonts["title"], bg=PANEL, fg=FG
        ).pack(anchor="w", pady=(0, 16))

        # Turn
        box = _section(side, "Now playing", fonts)
        ui["turn"] = tk.Label(box, text="", font=fonts["big"], bg=CARD, fg=FG, anchor="w")
        ui["turn"].pack(fill="x")
        ui["phase"] = tk.Label(box, text="", font=fonts["body"], bg=CARD, fg=ACCENT, anchor="w")
        ui["phase"].pack(fill="x", pady=(4, 0))

        # Last action
        box = _section(side, "Last action", fonts)
        ui["headline"] = tk.Label(
            box, text="", font=fonts["big"], bg=CARD, fg=FG, anchor="w", wraplength=260, justify="left"
        )
        ui["headline"].pack(fill="x")
        ui["detail"] = tk.Label(
            box, text="", font=fonts["body"], bg=CARD, fg=MUTED, anchor="w", wraplength=260, justify="left"
        )
        ui["detail"].pack(fill="x", pady=(4, 0))

        # Outcome
        box = _section(side, "Result", fonts)
        ui["outcome"] = tk.Label(
            box, text="", font=fonts["big"], bg=CARD, fg=ACCENT, anchor="w", wraplength=260, justify="left"
        )
        ui["outcome"].pack(fill="x")
        ui["events"] = tk.Label(
            box, text="", font=fonts["small"], bg=CARD, fg=MUTED, anchor="w", wraplength=260, justify="left"
        )
        ui["events"].pack(fill="x", pady=(6, 0))

        # Heights
        box = _section(side, f"Height  /  {TARGET_HEIGHT} m", fonts)
        row1 = tk.Frame(box, bg=CARD)
        row1.pack(fill="x")
        tk.Label(row1, text="P1", font=fonts["body"], bg=CARD, fg=P1C).pack(side="left")
        ui["p1_h"] = tk.Label(row1, text="0 m", font=fonts["body"], bg=CARD, fg=FG)
        ui["p1_h"].pack(side="right")
        ui["p1_bar"] = tk.Canvas(box, width=ui["bar_w"], height=14, bg=CARD, highlightthickness=0)
        ui["p1_bar"].pack(fill="x", pady=(4, 10))

        row2 = tk.Frame(box, bg=CARD)
        row2.pack(fill="x")
        tk.Label(row2, text="P2", font=fonts["body"], bg=CARD, fg=P2C).pack(side="left")
        ui["p2_h"] = tk.Label(row2, text="0 m", font=fonts["body"], bg=CARD, fg=FG)
        ui["p2_h"].pack(side="right")
        ui["p2_bar"] = tk.Canvas(box, width=ui["bar_w"], height=14, bg=CARD, highlightthickness=0)
        ui["p2_bar"].pack(fill="x", pady=(4, 0))

        # Rolls + challenge
        box = _section(side, "Rolls", fonts)
        ui["rolls"] = tk.Label(box, text="", font=fonts["body"], bg=CARD, fg=FG, anchor="w")
        ui["rolls"].pack(fill="x")

        box = _section(side, "Next challenge", fonts)
        ui["challenge"] = tk.Label(box, text="", font=fonts["body"], bg=CARD, fg=DANGER, anchor="w")
        ui["challenge"].pack(fill="x")

        # Placement
        box = _section(side, "Placement", fonts)
        ui["slot"] = tk.Label(
            box, text="", font=fonts["body"], bg=CARD, fg=ACCENT, anchor="w", justify="left"
        )
        ui["slot"].pack(fill="x")

        tk.Label(
            side,
            text="R roll · S scrap · Esc menu",
            font=fonts["small"],
            bg=PANEL,
            fg=MUTED,
        ).pack(side="bottom", anchor="w", pady=(12, 0))

        # Board on the right
        board_wrap = tk.Frame(body, bg=BG)
        board_wrap.pack(side="left", fill="both", expand=True)
        board._canvas.pack(in_=board_wrap, expand=True)

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
