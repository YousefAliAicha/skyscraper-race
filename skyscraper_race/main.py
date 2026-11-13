"""game2dboard UI. Run: python main.py"""

from game2dboard import Board
from constants import (
    BOARD_COLS, BOARD_ROWS, CELL_SIZE, GROUND_ROW,
    P1_COLS, P2_COLS, TOWER_BOTTOM_ROW, TOWER_TOP_ROW,
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


def draw_tower(player, cols):
    floors = player.tower.floors_bottom_up()
    for i, floor in enumerate(floors[: TOWER_BOTTOM_ROW - TOWER_TOP_ROW + 1]):
        row = TOWER_BOTTOM_ROW - i
        ratio = player.tower.safety_ratio(floor)
        board[row][cols[0]] = f"{floor.height}m"
        board[row][cols[1]] = floor.image
        board[row][cols[2]] = "∞" if ratio == float("inf") else f"{ratio:.1f}"


def draw():
    clear_board()
    board[0][P1_COLS[0]], board[0][P1_COLS[1]] = "p1", "ht:"
    board[0][P1_COLS[2]] = f"{game.players[0].tower_height():.0f}m"
    board[0][P2_COLS[0]], board[0][P2_COLS[1]] = "p2", "ht:"
    board[0][P2_COLS[2]] = f"{game.players[1].tower_height():.0f}m"
    board[1][4], board[1][5] = "ROLL", "SCRAP"
    board[1][3] = ">>" if game.current_index == 0 else None
    board[1][6] = "<<" if game.current_index == 1 else None
    for c in P1_COLS + P2_COLS:
        board[GROUND_ROW][c] = "===="
    draw_tower(game.players[0], P1_COLS)
    draw_tower(game.players[1], P2_COLS)
    pending = game.current_player().current_roll
    if pending and game.phase == "place":
        board[1][7] = pending["image"]
        board[1][8] = f"{pending['height']}m"
    board.print(game.message)


def row_to_pos(player, row):
    if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
        return None
    idx = TOWER_BOTTOM_ROW - row
    n = player.tower.floor_count()
    return n if idx >= n else idx


def on_click(btn, row, col):
    if game.phase == "game_over":
        return draw()
    try:
        if row == 1 and col == 4:
            game.roll()
        elif row == 1 and col == 5:
            game.scrap_roll()
        elif game.phase == "place":
            cols = P1_COLS if game.current_index == 0 else P2_COLS
            if col in cols:
                pos = row_to_pos(game.current_player(), row)
                if pos is not None:
                    game.place_floor(pos)
        draw()
    except RuntimeError as e:
        board.print(str(e))


def on_key(key):
    if game.phase == "game_over":
        return draw()
    try:
        if key in ("r", "R"):
            game.roll()
        elif key in ("s", "S"):
            game.scrap_roll()
        elif key.isdigit() and game.phase == "place":
            game.place_floor(int(key))
        draw()
    except RuntimeError as e:
        board.print(str(e))


if __name__ == "__main__":
    board.on_mouse_click = on_click
    board.on_key_press = on_key
    draw()
    board.show()
