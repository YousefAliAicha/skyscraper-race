"""Skyscraper Race Lite — polished game2dboard UI.  python main.py"""

from game2dboard import Board

import assets
from constants import (
    BOARD_COLS, BOARD_ROWS, CELL_SIZE, GROUND_ROW,
    P1_COLS, P2_COLS, TOWER_BOTTOM_ROW, TOWER_TOP_ROW,
)
from game import Game

assets.ensure_assets()

game = Game("P1", "P2")
board = Board(BOARD_ROWS, BOARD_COLS)
board.cell_size = CELL_SIZE
board.title = "Skyscraper Race Lite"
board.margin = 14
board.cell_spacing = 4
board.margin_color = "#0b1020"
board.cell_color = "#101a2b"
board.grid_color = "#18253a"
board.background_image = "bg"
board.create_output(font_size=13, background_color="#0b1020", color="#d7e2f5")


def clear():
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            board[r][c] = None


def status_for(player, floor):
    r = player.tower.safety_ratio(floor)
    if r < 1.0:
        return "fail"
    if r < 1.5:
        return "warn"
    return "ok"


def draw_tower(player, cols, active):
    floors = player.tower.floors_bottom_up()
    n = len(floors)
    slots = TOWER_BOTTOM_ROW - TOWER_TOP_ROW + 1
    for i, floor in enumerate(floors[:slots]):
        row = TOWER_BOTTOM_ROW - i
        board[row][cols[1]] = assets.floor_image(
            floor.material_name, floor.height, status_for(player, floor)
        )
    if active and game.phase == "place" and n < slots:
        board[TOWER_BOTTOM_ROW - n][cols[1]] = "slot_top"


def draw():
    clear()
    p1, p2 = game.players

    board[0][0] = "badge_p1"
    board[0][1] = assets.height_chip(int(p1.tower_height()), (80, 140, 220))
    board[0][2] = assets.rolls_chip(p1.rolls_remaining) if game.current_index == 0 else None
    board[0][4] = "badge_goal"
    board[0][7] = "badge_p2"
    board[0][8] = assets.height_chip(int(p2.tower_height()), (220, 140, 70))
    board[0][9] = assets.rolls_chip(p2.rolls_remaining) if game.current_index == 1 else None

    board[1][4] = "btn_roll"
    board[1][5] = "btn_scrap"
    if game.current_index == 0:
        board[1][0] = "badge_you"
    else:
        board[1][9] = "badge_you"

    cur = game.current_player()
    nxt = cur.next_challenge()
    if nxt:
        board[1][3] = "challenge"
        board[1][6] = assets.height_chip(int(nxt), (200, 70, 70))

    pending = cur.current_roll
    if pending and game.phase == "place":
        board[1][7] = assets.floor_image(
            pending["material_name"], pending["height"], "ok"
        )

    for c in P1_COLS + P2_COLS:
        board[GROUND_ROW][c] = "ground"

    draw_tower(p1, P1_COLS, game.current_index == 0)
    draw_tower(p2, P2_COLS, game.current_index == 1)
    board.print(game.message)


def row_to_pos(player, row):
    if row < TOWER_TOP_ROW or row > TOWER_BOTTOM_ROW:
        return None
    idx = TOWER_BOTTOM_ROW - row
    n = player.tower.floor_count()
    return n if idx >= n else idx


def on_click(_btn, row, col):
    if game.phase == "game_over":
        return draw()
    try:
        if row == 1 and col == 4:
            game.roll()
        elif row == 1 and col == 5:
            game.scrap_roll()
        elif game.phase == "place":
            cols = P1_COLS if game.current_index == 0 else P2_COLS
            other = P2_COLS if game.current_index == 0 else P1_COLS
            if col in other:
                board.print(f"Wrong side — place on the {game.side_hint()} tower")
                return
            if col in cols:
                pos = row_to_pos(game.current_player(), row)
                if pos is None:
                    board.print("Click the green TOP slot or press Space")
                    return
                game.place_floor(pos)
            else:
                board.print(f"Click {game.side_hint()} tower or press Space")
                return
        else:
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
