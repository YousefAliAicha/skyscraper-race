"""Fullscreen title cards: main menu, how-to-play, win / collapse splash."""

import tkinter as tk
from tkinter import font as tkfont

BG = "#0b1020"
FG = "#e8eef8"
ACCENT = "#3dd68c"
ACCENT2 = "#f0b429"
DANGER = "#e85d5d"
MUTED = "#8b9bb4"


def _fonts(root):
    return {
        "hero": tkfont.Font(family="DejaVu Sans", size=42, weight="bold"),
        "title": tkfont.Font(family="DejaVu Sans", size=28, weight="bold"),
        "sub": tkfont.Font(family="DejaVu Sans", size=16),
        "body": tkfont.Font(family="DejaVu Sans", size=14),
        "btn": tkfont.Font(family="DejaVu Sans", size=16, weight="bold"),
    }


def _clear(root):
    for w in root.winfo_children():
        w.destroy()


def _button(parent, text, command, fonts, fill=ACCENT, fg="#0b1020"):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=fonts["btn"],
        bg=fill,
        fg=fg,
        activebackground=fg,
        activeforeground=fill,
        relief="flat",
        padx=28,
        pady=14,
        cursor="hand2",
        borderwidth=0,
    )
    return btn


def show_main_menu(root, on_play, on_howto, on_quit):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts(root)

    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text="SKYSCRAPER", font=fonts["hero"], bg=BG, fg=FG).pack()
    tk.Label(wrap, text="RACE", font=fonts["hero"], bg=BG, fg=ACCENT).pack()
    tk.Label(
        wrap,
        text="First to 150 m  ·  Build smart or collapse",
        font=fonts["sub"],
        bg=BG,
        fg=MUTED,
    ).pack(pady=(8, 36))

    _button(wrap, "PLAY", on_play, fonts).pack(fill="x", pady=6)
    _button(wrap, "HOW TO PLAY", on_howto, fonts, fill="#243044", fg=FG).pack(
        fill="x", pady=6
    )
    _button(wrap, "QUIT", on_quit, fonts, fill=DANGER, fg=FG).pack(fill="x", pady=6)

    tk.Label(
        wrap,
        text="Arrow keys move the place cursor  ·  Enter confirms",
        font=fonts["body"],
        bg=BG,
        fg=MUTED,
    ).pack(pady=(28, 0))


def show_howto(root, on_back):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts(root)
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text="HOW TO PLAY", font=fonts["title"], bg=BG, fg=ACCENT2).pack(
        pady=(0, 20)
    )

    lines = [
        "1. ROLL (or press R) to get a floor material",
        "2. Move the green ARROW with ↑ / ↓ to choose height",
        "3. Press ENTER or SPACE to place at the arrow",
        "4. SCRAP (S) discards a bad roll",
        "5. Strong materials (steel/concrete) belong at the BASE",
        "6. Junk belongs on TOP — or scrap it",
        "7. Challenges hit as you climb — keep the tower stable",
        "8. First tower to 150 m wins",
    ]
    for line in lines:
        tk.Label(wrap, text=line, font=fonts["body"], bg=BG, fg=FG, anchor="w").pack(
            fill="x", pady=4
        )

    _button(wrap, "BACK", on_back, fonts, fill="#243044", fg=FG).pack(pady=(28, 0))


def show_title_card(root, title, subtitle, detail, on_continue, btn="CONTINUE", color=ACCENT):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts(root)
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text=title, font=fonts["hero"], bg=BG, fg=color).pack()
    tk.Label(wrap, text=subtitle, font=fonts["title"], bg=BG, fg=FG).pack(pady=(12, 8))
    if detail:
        tk.Label(wrap, text=detail, font=fonts["sub"], bg=BG, fg=MUTED).pack(pady=(0, 28))
    _button(wrap, btn, on_continue, fonts, fill=color, fg="#0b1020").pack()


def show_win_card(root, winner_name, height, on_again, on_menu):
    _clear(root)
    root.configure(bg=BG)
    fonts = _fonts(root)
    wrap = tk.Frame(root, bg=BG)
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(wrap, text="VICTORY", font=fonts["hero"], bg=BG, fg=ACCENT).pack()
    tk.Label(
        wrap,
        text=f"{winner_name} reaches {height:.0f} m",
        font=fonts["title"],
        bg=BG,
        fg=FG,
    ).pack(pady=(16, 8))
    tk.Label(
        wrap,
        text="The skyscraper stands.",
        font=fonts["sub"],
        bg=BG,
        fg=MUTED,
    ).pack(pady=(0, 32))

    _button(wrap, "PLAY AGAIN", on_again, fonts).pack(fill="x", pady=6)
    _button(wrap, "MAIN MENU", on_menu, fonts, fill="#243044", fg=FG).pack(
        fill="x", pady=6
    )
