"""Simple fullscreen screens: splash, menu, how-to, win."""

import tkinter as tk
from tkinter import font as tkfont

BG = "#111318"
FG = "#f2f2f2"
DIM = "#a0a4ae"
GREEN = "#6bcb8b"
RED = "#e07070"
BTN = "#2a2e38"


def _fonts():
    return {
        "hero": tkfont.Font(family="DejaVu Sans", size=36, weight="bold"),
        "title": tkfont.Font(family="DejaVu Sans", size=22, weight="bold"),
        "body": tkfont.Font(family="DejaVu Sans", size=14),
        "btn": tkfont.Font(family="DejaVu Sans", size=14, weight="bold"),
    }


def _clear(root):
    for w in root.winfo_children():
        w.destroy()


def _btn(parent, text, command, fonts, bg=GREEN, fg="#111318"):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=fonts["btn"],
        bg=bg,
        fg=fg,
        activebackground=FG,
        activeforeground=BG,
        relief="flat",
        padx=24,
        pady=12,
        cursor="hand2",
    )


def show_main_menu(root, on_play, on_howto, on_quit):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text="Skyscraper Race", font=fonts["hero"], bg=BG, fg=FG).pack()
    tk.Label(
        wrap, text="First to 150 m wins", font=fonts["body"], bg=BG, fg=DIM
    ).pack(pady=(8, 28))

    _btn(wrap, "Play", on_play, fonts).pack(fill="x", pady=5)
    _btn(wrap, "How to play", on_howto, fonts, bg=BTN, fg=FG).pack(fill="x", pady=5)
    _btn(wrap, "Quit", on_quit, fonts, bg=RED, fg=FG).pack(fill="x", pady=5)


def show_howto(root, on_back):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text="How to play", font=fonts["title"], bg=BG, fg=FG).pack(
        pady=(0, 16)
    )
    steps = [
        "1. Press R to roll a floor",
        "2. Move the green arrow with ↑ and ↓",
        "3. Press Enter to place it there",
        "4. Press S to scrap a bad roll",
        "5. Put strong materials at the bottom",
        "6. Put junk on top (or scrap it)",
        "7. First to 150 m wins",
    ]
    for s in steps:
        tk.Label(wrap, text=s, font=fonts["body"], bg=BG, fg=FG, anchor="w").pack(
            fill="x", pady=3
        )
    _btn(wrap, "Back", on_back, fonts, bg=BTN, fg=FG).pack(pady=(24, 0))


def show_title_card(root, title, subtitle, detail, on_continue, btn="Continue", color=GREEN):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(wrap, text=title, font=fonts["hero"], bg=BG, fg=FG).pack()
    tk.Label(wrap, text=subtitle, font=fonts["title"], bg=BG, fg=color).pack(pady=(10, 6))
    if detail:
        tk.Label(wrap, text=detail, font=fonts["body"], bg=BG, fg=DIM).pack(pady=(0, 24))
    _btn(wrap, btn, on_continue, fonts, bg=color).pack()


def show_win_card(root, winner_name, height, on_again, on_menu):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")
    tk.Label(wrap, text="Winner", font=fonts["hero"], bg=BG, fg=GREEN).pack()
    tk.Label(
        wrap,
        text=f"{winner_name} — {height:.0f} m",
        font=fonts["title"],
        bg=BG,
        fg=FG,
    ).pack(pady=(12, 28))
    _btn(wrap, "Play again", on_again, fonts).pack(fill="x", pady=5)
    _btn(wrap, "Main menu", on_menu, fonts, bg=BTN, fg=FG).pack(fill="x", pady=5)
