# Skyscraper Race

A 2-player race to build a skyscraper to **150 meters**.  
Python 3 + [game2dboard](https://pypi.org/project/game2dboard/).

Roll materials, choose where each floor goes, keep the tower stable, and beat challenges on the way up.

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
| Click your tower | Place at that height |
| `S` or **SCRAP** | Discard the roll |
| `Esc` | Leave to menu |

**P1** builds on the left, **P2** on the right.  
Three rolls per turn. First to **150 m** wins.

**Tip:** put steel/concrete at the bottom. Keep junk on top — or scrap it.

## Project layout

```
skyscraper_race/
  constants.py    game numbers
  materials.py    material lookup (hash table)
  roll.py         5-digit roll decode
  tower.py        linked-list tower, load, collapse
  challenges.py   challenge heap + height search
  player.py       player state
  game.py         turn logic
  main.py         UI entry point
  screens.py      menu / how-to / win screens
  assets.py       image generator
  test_core.py    tests
  demo.py         headless autoplay
  img/            board sprites
```

## Data structures

| Structure | File | Role |
|-----------|------|------|
| Hash table | `materials.py` | Material stats by tier |
| Linked list | `tower.py` | Tower floors |
| Recursion | `tower.py` | Weight above a floor |
| Stack | `tower.py` | Collapse removal |
| Min-heap | `challenges.py` | Next challenge height |
| Binary search | `challenges.py` | Floor at a given height |

## Learning the code

Read in this order — each file is short and commented:

1. `constants.py` — tune numbers here
2. `materials.py` — dict lookup
3. `roll.py` — decode a 5-digit roll
4. `tower.py` — linked list, load, collapse
5. `challenges.py` — heap + height search
6. `game.py` — turn flow (no GUI)
7. `main.py` — board UI

Run `python test_core.py` after any change.
