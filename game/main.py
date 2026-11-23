"""App entry point: splash → menu → match → win → repeat.

Run from the repo root:
  python -m game.main
or:
  cd game && python main.py
"""

import sys
from pathlib import Path

# repo root on sys.path so `logic` and `game` imports work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# game2dboard loads sprites from ./img — run with this folder as cwd
import os

os.chdir(Path(__file__).resolve().parent)

import tkinter as tk

from game import assets, screens
from game.match import run_match

BG = "#0f1218"
GREEN = "#5ecf8a"


def run_menu():
    choice = {"action": "quit"}
    root = tk.Tk()
    root.title("Skyscraper Race")
    root.configure(bg=BG)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _event: root.destroy())

    def play():
        choice["action"] = "play"
        root.destroy()

    def quit_game():
        choice["action"] = "quit"
        root.destroy()

    def howto():
        screens.show_howto(
            root,
            on_back=lambda: screens.show_main_menu(
                root,
                play,
                howto,
                quit_game,
            ),
        )

    screens.show_title_card(
        root,
        title="Skyscraper Race",
        subtitle="Build to 150 meters",
        detail="Strong base · light top · don't collapse",
        on_continue=lambda: screens.show_main_menu(
            root,
            play,
            howto,
            quit_game,
        ),
        btn="Start",
        color=GREEN,
    )
    root.mainloop()
    return choice["action"]


def main():
    assets.ensure_assets()
    action = run_menu()

    while action == "play":
        action = run_match()
        if action == "menu":
            action = run_menu()
        elif action != "play":
            break


if __name__ == "__main__":
    main()
