"""Fullscreen screens: splash, menu, how-to, win."""

import tkinter as tk
from tkinter import font as tkfont

BG = "#0f1218"
FG = "#f0f2f5"
DIM = "#9aa3b2"
ACCENT = "#5ecf8a"
DANGER = "#d96b6b"
BTN = "#252a36"


def _fonts():
    return {
        "hero": tkfont.Font(family="DejaVu Sans", size=34, weight="bold"),
        "title": tkfont.Font(family="DejaVu Sans", size=20, weight="bold"),
        "body": tkfont.Font(family="DejaVu Sans", size=14),
        "btn": tkfont.Font(family="DejaVu Sans", size=14, weight="bold"),
    }


def _clear(root):
    for child in root.winfo_children():
        child.destroy()


def _button(parent, text, command, fonts, bg=ACCENT, fg=BG):
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
        padx=28,
        pady=12,
        cursor="hand2",
    )


def show_title_card(root, title, subtitle, detail, on_continue, btn="Continue", color=ACCENT):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    box = tk.Frame(root, bg=BG)
    box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(box, text=title, font=fonts["hero"], bg=BG, fg=FG).pack()
    tk.Label(box, text=subtitle, font=fonts["title"], bg=BG, fg=color).pack(pady=(10, 6))
    if detail:
        tk.Label(box, text=detail, font=fonts["body"], bg=BG, fg=DIM).pack(pady=(0, 24))
    _button(box, btn, on_continue, fonts, bg=color).pack()


def show_main_menu(root, on_play, on_howto, on_quit):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    box = tk.Frame(root, bg=BG)
    box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(box, text="Skyscraper Race", font=fonts["hero"], bg=BG, fg=FG).pack()
    tk.Label(box, text="First to 150 m wins", font=fonts["body"], bg=BG, fg=DIM).pack(
        pady=(8, 28)
    )
    _button(box, "Play", on_play, fonts).pack(fill="x", pady=5)
    _button(box, "How to play", on_howto, fonts, bg=BTN, fg=FG).pack(fill="x", pady=5)
    _button(box, "Quit", on_quit, fonts, bg=DANGER, fg=FG).pack(fill="x", pady=5)


def show_howto(root, on_back):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    box = tk.Frame(root, bg=BG)
    box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(box, text="How to play", font=fonts["title"], bg=BG, fg=FG).pack(
        pady=(0, 16)
    )
    for line in (
        "1. Press R to roll a floor",
        "2. Move the arrow with ↑ and ↓",
        "3. Press Enter (or click the tower) to place",
        "4. Press S to scrap a bad roll",
        "5. Put strong materials at the bottom",
        "6. Put junk on top — or scrap it",
        "7. First tower to 150 m wins",
    ):
        tk.Label(box, text=line, font=fonts["body"], bg=BG, fg=FG, anchor="w").pack(
            fill="x", pady=3
        )
    _button(box, "Back", on_back, fonts, bg=BTN, fg=FG).pack(pady=(24, 0))


def show_win_card(root, winner_name, height, on_again, on_menu):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts()
    box = tk.Frame(root, bg=BG)
    box.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(box, text="Winner", font=fonts["hero"], bg=BG, fg=ACCENT).pack()
    tk.Label(
        box,
        text=f"{winner_name}  ·  {height:.0f} m",
        font=fonts["title"],
        bg=BG,
        fg=FG,
    ).pack(pady=(12, 28))
    _button(box, "Play again", on_again, fonts).pack(fill="x", pady=5)
    _button(box, "Main menu", on_menu, fonts, bg=BTN, fg=FG).pack(fill="x", pady=5)
