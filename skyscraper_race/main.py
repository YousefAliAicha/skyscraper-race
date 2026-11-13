"""game2dboard UI. Run: python main.py

Controls:
  ROLL / R     — roll a floor
  SCRAP / S    — discard roll
  Space / Enter — place on TOP of your tower
  click your tower column — place at that height
  0-9          — place at linked-list index
"""

from game2dboard import Board
from constants import (
    BOARD_COLS, BOARD_ROWS, CELL_SIZE, GROUND_ROW, TARGET_HEIGHT,
    P1_COLS, P2_COLS, TOWER_BOTTOM_ROW, TOWER_TOP_ROW,
)
from game import Game

game = Game("P1", "P2")
board = Board(BOARD_ROWS, BOARD_COLS)
board.cell_size = CELL_SIZE
board.title = "Skyscraper Race Lite"
board.create_output(font_size=13)


def clear_board():
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            board[r][c] = None


def active_cols():
    return P1_COLS if game.current_index == 0 else P2_COLS


def ratio_label(player, floor):
    r = player.tower.safety_ratio(floor)
    if r == float("inf"):
        return "ok"
    if r < 1.0:
        return "FAIL"
    if r < 1.5:
        return f"!{r:.1f}"
    return f"{r:.1f}"


def draw_tower(player, cols, is_active):
    floors = player.tower.floors_bottom_up()
    n = len(floors)
    max_slots = TOWER_BOTTOM_ROW - TOWER_TOP_ROW + 1

    for i, floor in enumerate(floors[:max_slots]):
        row = TOWER_BOTTOM_ROW - i
        board[row][cols[0]] = f"{floor.height}m"
        board[row][cols[1]] = floor.image
        board[row][cols[2]] = ratio_label(player, floor)

    # Placement hints on the active tower during place phase
    if is_active and game.phase == "place":
        # Slot above the top (= append)
        if n < max_slots:
            row = TOWER_BOTTOM_ROW - n
            board[row][cols[1]] = "TOP"
            board[row][cols[0]] = ">>>"
        # Mark ground slot if empty
        if n == 0:
            board[TOWER_BOTTOM_ROW][cols[1]] = "TOP"
            board[TOWER_BOTTOM_ROW][cols[0]] = ">>>"


def draw():
    clear_board()
    p1, p2 = game.players

    # HUD row 0
    board[0][0], board[0][1] = "p1", f"{p1.tower_height():.0f}m"
    board[0][2] = f"{p1.floor_count()}f"
    board[0][4] = f"/{TARGET_HEIGHT}"
    board[0][7], board[0][8] = "p2", f"{p2.tower_height():.0f}m"
    board[0][9] = f"{p2.floor_count()}f"

    # Action row 1
    board[1][4] = "ROLL"
    board[1][5] = "SCRAP"
    if game.current_index == 0:
        board[1][0] = "YOU"
        board[1][3] = ">>>"
    else:
        board[1][9] = "YOU"
        board[1][6] = "<<<"

    cur = game.current_player()
    board[1][2] = f"x{cur.rolls_remaining}"

    pending = cur.current_roll
    if pending and game.phase == "place":
        board[1][7] = pending["image"]
        board[1][8] = f"{pending['height']}m"

    for c in P1_COLS + P2_COLS:
        board[GROUND_ROW][c] = "===="

    draw_tower(p1, P1_COLS, game.current_index == 0)
    draw_tower(p2, P2_COLS, game.current_index == 1)
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
            cols = active_cols()
            other = P2_COLS if game.current_index == 0 else P1_COLS
            if col in other:
                board.print(f"Wrong tower — place on the {game.side_hint()} side")
                return
            if col in cols:
                pos = row_to_pos(game.current_player(), row)
                if pos is not None:
                    game.place_floor(pos)
                else:
                    board.print("Click a tower slot (>>> TOP) or press Space")
                    return
            else:
                board.print(f"Click your {game.side_hint()} tower, or Space for top")
                return
        elif game.phase == "roll":
            board.print(game.message)
            return
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
        elif key in ("space", "Return", " "):
            game.place_on_top()
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
