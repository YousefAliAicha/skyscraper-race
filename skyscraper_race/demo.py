"""Console autoplay demo.  python demo.py"""

import random
from game import Game


def show(g):
    print(f"\n{g.message}")
    for p in g.players:
        stack = " | ".join(
            f"{f.material}:{f.height}m" for f in p.tower.floors_bottom_up()
        ) or "empty"
        nxt = p.next_challenge()
        print(f"  {p.name}: {p.tower_height():.0f}m  [{stack}]  next⚠={nxt}")


def main():
    random.seed(11)
    g = Game("P1", "P2", enable_challenges=True)
    show(g)
    for _ in range(50):
        if g.phase == "game_over":
            break
        if g.phase == "roll":
            g.roll()
        g.place_on_top()
        show(g)
    print("\nDone.", f"Winner: {g.winner.name}" if g.winner else "No winner yet.")


if __name__ == "__main__":
    main()
