"""Console autoplay — no GUI. Run: python demo.py

Useful to see turn flow and collapses without opening the window.
"""

import random

from game import Game


def show(game):
    print(f"\n{game.message}")
    for player in game.players:
        stack = " | ".join(
            f"{f.material}:{f.height}m" for f in player.tower.floors_bottom_up()
        ) or "empty"
        nxt = player.next_challenge()
        print(
            f"  {player.name}: {player.tower_height():.0f}m  "
            f"[{stack}]  next challenge={nxt}"
        )


def main():
    random.seed(11)
    game = Game("P1", "P2", enable_challenges=True)
    show(game)

    for _ in range(50):
        if game.phase == "game_over":
            break
        if game.phase == "roll":
            game.roll()
        game.place_on_top()
        show(game)

    if game.winner:
        print(f"\nDone. Winner: {game.winner.name}")
    else:
        print("\nDone. No winner yet.")


if __name__ == "__main__":
    main()
