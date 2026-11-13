"""Console demo — auto-plays a short match (no GUI).  python demo.py"""

import random
from game import Game


def show(g):
    print(f"\n{g.message}")
    for p in g.players:
        stack = " | ".join(
            f"{f.material}:{f.height}m" for f in p.tower.floors_bottom_up()
        ) or "empty"
        print(f"  {p.name}: {p.tower_height():.0f}m  [{stack}]")


def main():
    random.seed(7)
    g = Game("P1", "P2")
    show(g)
    for _ in range(36):
        if g.phase == "game_over":
            break
        if g.phase == "roll":
            g.roll()
            show(g)
        # Prefer strong-ish placements: always on top for climb demo
        g.place_on_top()
        show(g)
    print("\nDone.", f"Winner: {g.winner.name}" if g.winner else "No winner yet.")


if __name__ == "__main__":
    main()
