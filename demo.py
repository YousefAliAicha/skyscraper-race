"""Console autoplay — run from repo root: python demo.py"""

import random

from logic.algorithms.game import Game


def show(game):
    print(f"\n{game.message}")
    for player in game.players:
        parts = []
        for floor in player.tower.floors_from_ground():
            parts.append(floor.label())
        stack_text = " | ".join(parts) if parts else "empty"
        next_height = player.next_challenge()
        print(
            f"  {player.name}: {player.tower_height():.0f}m  "
            f"[{stack_text}]  next challenge={next_height}"
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
