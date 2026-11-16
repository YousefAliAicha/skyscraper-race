# Skyscraper Race

A 2-player race to build a skyscraper to **150 meters**.  
Python 3 + [game2dboard](https://pypi.org/project/game2dboard/).

Roll materials, choose where each floor goes, keep the tower stable, and survive challenges on the way up.

## Install

```bash
git clone https://github.com/YousefAliAicha/skyscraper-race.git
cd skyscraper-race
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

On Ubuntu/Debian you also need Tk:

```bash
sudo apt install python3-tk
```

## Run

```bash
cd skyscraper_race
python test_core.py   # unit tests
python main.py        # game
```

## How to play

| Control | Action |
|---------|--------|
| `R` or **ROLL** | Get a new floor |
| `↑` / `↓` | Move the place arrow |
| `Enter` / `Space` | Place at the arrow |
| Click your tower | Move the arrow to that height |
| `S` or **SCRAP** | Discard the roll |
| `Esc` | Leave to menu |

**P1** builds on the left, **P2** on the right.  
Three rolls per turn. First to **150 m** wins.

**Tip:** put steel/concrete at the bottom. Keep junk on top — or scrap it.

## Project layout

```
skyscraper_race/
  constants.py    game numbers
  materials.py    material dict (hash table)
  roll.py         5-digit roll decode
  floor.py        one floor / linked-list node
  tower.py        linked list, recursion, stack
  challenges.py   min-heap + binary search
  player.py       one player's state
  game.py         turn logic (no GUI)
  screens.py      menu / how-to / win screens
  match.py        match board + sidebar
  main.py         app entry (menu loop)
  assets.py       image generator
  test_core.py    tests
  demo.py         headless autoplay
  img/            board sprites
```

## Data structures (6)

| # | Structure | File | Role |
|---|-----------|------|------|
| 1 | Hash table (dict) | `materials.py` | Material stats by tier |
| 2 | Linked list | `floor.py` + `tower.py` | Tower floors |
| 3 | Recursion | `tower.py` → `load_above` | Weight above a floor |
| 4 | Stack | `tower.py` → `collapse` | Remove failed floors |
| 5 | Min-heap | `challenges.py` | Next challenge height |
| 6 | Binary search | `challenges.py` | Floor at a given height |

## Learning the code

Read in this order — each file is short:

1. `constants.py`
2. `materials.py` — dict lookup
3. `roll.py` — decode a roll
4. `floor.py` — one node
5. `tower.py` — list + recursion + stack
6. `challenges.py` — heap + binary search
7. `game.py` — turn flow
8. `match.py` / `main.py` — UI

Run `python test_core.py` after any change.
