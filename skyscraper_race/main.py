"""Entry point — game2dboard UI shell.

Run from this folder:
    python main.py

The board is a *view*. Game state lives in Game / Tower (linked list).
"""

from game2dboard import Board

from constants import (
    BOARD_COLS,
    BOARD_ROWS,
    CELL_SIZE,
    GROUND_ROW,
    P1_COLS,
    P2_COLS,
    TOWER_BOTTOM_ROW,
    TOWER_TOP_ROW,
)
from game import Game

game = Game("P1", "P2")

board = Board(BOARD_ROWS, BOARD_COLS)
board.cell_size = CELL_SIZE
board.title = "Skyscraper Race Lite"
board.create_output(font_size=14)


def clear_board():
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            board[r][c] = None


def draw_hud():
    """Static labels + heights. Floor cells filled once Tower.insert_at works."""
    clear_board()

    # Row 0 — player HUD
    board[0][P1_COLS[0]] = "P1"
    board[0][P1_COLS[1]] = "ht:"
    board[0][P1_COLS[2]] = f"{game.players[0].tower_height():.0f}m"

    board[0][P2_COLS[0]] = "P2"
    board[0][P2_COLS[1]] = "ht:"
    board[0][P2_COLS[2]] = f"{game.players[1].tower_height():.0f}m"

    # Row 1 — actions (scaffold labels; wire clicks in Step 9/10)
    board[1][4] = "ROLL"
    board[1][5] = "SCRAP"

    # Ground row markers
    for c in P1_COLS + P2_COLS:
        board[GROUND_ROW][c] = "===="

    # Empty tower slots (visual guide)
    for r in range(TOWER_TOP_ROW, TOWER_BOTTOM_ROW + 1):
        board[r][P1_COLS[1]] = "·"
        board[r][P2_COLS[1]] = "·"

    board.print(game.message)


def on_click(btn, row, col):
    if game.phase == "game_over":
        board.print(game.message)
        return

    # Scaffold: announce the click; real handlers come in Step 9/10
    if row == 1 and col == 4:
        board.print(f"{game.current_player().name}: ROLL clicked (not wired yet)")
        return
    if row == 1 and col == 5:
        board.print(f"{game.current_player().name}: SCRAP clicked (not wired yet)")
        return

    board.print(f"Click ({row},{col}) btn={btn} — placement wiring comes later")


def on_key(key):
    if key in ("r", "R"):
        board.print("Key R — will call game.roll() once implemented")
    elif key in ("s", "S"):
        board.print("Key S — will call game.scrap_roll() once implemented")
    else:
        board.print(f"Key {key!r}")


def main():
    board.on_mouse_click = on_click
    board.on_key_press = on_key
    draw_hud()
    board.show()  # blocking


if __name__ == "__main__":
    main()
