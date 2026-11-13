"""Console demo — auto-plays a short match (no GUI).

    python demo.py
"""

import random
from game import Game


def show(game):
    print(f"\n--- {game.message}")
    for i, p in enumerate(game.players):
        mats = " | ".join(
            f"{f.material}:{f.height}m" for f in p.tower.floors_bottom_up()
        ) or "(empty)"
        print(f"  {p.name}: {p.tower_height():.0f}m  [{mats}]")


def main():
    random.seed(42)  # reproducible demo
    g = Game("P1", "P2")
    show(g)
    turns = 0
    while g.phase != "game_over" and turns < 40:
        turns += 1
        if g.phase == "roll":
            g.roll()
            show(g)
        # Always place on top for a clean climb demo
        g.place_floor(g.current_player().tower.floor_count())
        show(g)
    print("\nDemo finished.")
    if g.winner:
        print(f"Winner: {g.winner.name}")


if __name__ == "__main__":
    main()
