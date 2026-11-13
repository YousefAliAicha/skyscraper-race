# Skyscraper Race Lite

DSA group project: a 2-player race to build a skyscraper to **150 m**, built in Python with [`game2dboard`](https://pypi.org/project/game2dboard/).

## Game (short)

Each turn you roll a 5-digit number that becomes a floor (material, amount, height). You choose where to insert it in your tower. Heavy floors on a weak base can collapse. First tower to 150 m wins.

## DSA map

| Topic | Module | Role |
|-------|--------|------|
| Hash table | `materials.py` | Material / tier lookup |
| Linked list | `tower.py` | Tower + insert at position |
| Recursion | `tower.py` | `load_above` / safety |
| Stack | `tower.py` | Collapse failed floors |
| Min-heap + binary search | `challenges.py` | **Phase 2 / optional** |

## Layout

```
skyscraper_race/
  constants.py     # Tunable numbers
  materials.py     # Material hash table
  roll.py          # Roll generate + decode
  tower.py         # Floor node + Tower linked list
  challenges.py    # Heap / bisect (deferred OK)
  player.py        # Player state
  game.py          # Turn logic (no GUI)
  main.py          # game2dboard UI
  img/             # PNG assets for cells
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd skyscraper_race
python main.py
```

## Scaffold status

**Done**
- Folder layout, constants, material table, roll interface
- `Floor` / `Tower` / `Player` / `Game` shells
- Board HUD shell (click/key stubs)
- Placeholder PNGs in `img/`

**Not implemented yet** (raise `NotImplementedError` until filled in)
- `Tower.insert_at`, `load_above`, `safety_ratio`, `find_weakest_floor`, `collapse`
- `Game.roll` / `scrap_roll` / `place_floor`
- Challenge generation + processing
- Wiring UI actions to game logic

Build order: tower mechanics → game loop → UI wiring → (optional) challenges.

## Course notes

- Delivery: **23 Nov**; presentations **30 Nov / 1 Dec**
- Every teammate must be able to answer DSA questions (round-robin)
- Prefer implementing and understanding the code yourselves; use AI to validate
