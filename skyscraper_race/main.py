"""Entry point — game2dboard UI.

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


def _draw_tower(player, cols):
    """Render linked-list tower bottom-up into board rows."""
    floors = player.tower.floors_bottom_up()
    # Visible slots: GROUND_ROW-1 down toward TOWER_TOP_ROW
    visible = floors[: TOWER_BOTTOM_ROW - TOWER_TOP_ROW + 1]
    for i, floor in enumerate(visible):
        row = TOWER_BOTTOM_ROW - i
        ratio = player.tower.safety_ratio(floor)
        ratio_txt = "inf" if ratio == float("inf") else f"{ratio:.1f}"
        board[row][cols[0]] = f"{floor.height}m"
        board[row][cols[1]] = floor.image  # img/<name>.png if present
        board[row][cols[2]] = ratio_txt


def draw_hud():
    clear_board()

    board[0][P1_COLS[0]] = "p1"
    board[0][P1_COLS[1]] = "ht:"
    board[0][P1_COLS[2]] = f"{game.players[0].tower_height():.0f}m"

    board[0][P2_COLS[0]] = "p2"
    board[0][P2_COLS[1]] = "ht:"
    board[0][P2_COLS[2]] = f"{game.players[1].tower_height():.0f}m"

    board[1][4] = "ROLL"
    board[1][5] = "SCRAP"

    # Whose turn marker in center
    board[1][3] = ">>" if game.current_index == 0 else ""
    board[1][6] = "<<" if game.current_index == 1 else ""

    for c in P1_COLS + P2_COLS:
        board[GROUND_ROW][c] = "===="

    _draw_tower(game.players[0], P1_COLS)
    _draw_tower(game.players[1], P2_COLS)

    # Pending roll preview
    pending = game.current_player().current_roll
    if pending and game.phase == "place":
        board[1][7] = pending["image"]
        board[1][8] = f"{pending['height']}m"

    board.print(game.message)


def _row_to_insert_position(player, row: int):
    """Map a clicked tower row to a linked-list insert position."""
    if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
        return None
    # Clicking empty space above the tower appends at top
    n = player.tower.floor_count()
    # Row TOWER_BOTTOM_ROW is ground (pos 0 visual). Clicking a filled
    # row inserts *at that index* (replacing that slot upward).
    index_from_bottom = TOWER_BOTTOM_ROW - row
    if index_from_bottom >= n:
        return n  # append on top
    return index_from_bottom


def on_click(btn, row, col):
    if game.phase == "game_over":
        draw_hud()
        return

    try:
        if row == 1 and col == 4:
            game.roll()
            draw_hud()
            return
        if row == 1 and col == 5:
            game.scrap_roll()
            draw_hud()
            return

        player = game.current_player()
        cols = P1_COLS if game.current_index == 0 else P2_COLS
        if col in cols and game.phase == "place":
            pos = _row_to_insert_position(player, row)
            if pos is not None:
                game.place_floor(pos)
                draw_hud()
                return

        board.print(game.message)
    except RuntimeError as exc:
        board.print(str(exc))


def on_key(key):
    if game.phase == "game_over":
        draw_hud()
        return
    try:
        if key in ("r", "R"):
            game.roll()
        elif key in ("s", "S"):
            game.scrap_roll()
        elif key.isdigit() and game.phase == "place":
            # Number key = insert position
            game.place_floor(int(key))
        draw_hud()
    except RuntimeError as exc:
        board.print(str(exc))


def main():
    board.on_mouse_click = on_click
    board.on_key_press = on_key
    draw_hud()
    board.show()  # blocking


if __name__ == "__main__":
    main()
