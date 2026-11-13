# Skyscraper Race Lite

DSA group project: a 2-player race to build a skyscraper to **150 m**, built in Python with [`game2dboard`](https://pypi.org/project/game2dboard/).

## Game (short)

Each turn you roll a 5-digit number that becomes a floor (material, amount, height). You choose where to insert it in your tower. Heavy floors on a weak base can collapse. First tower to 150 m wins.

## DSA map

| Topic | Module | Role |
|-------|--------|------|
| Hash table | `materials.py` | Material / tier lookup |
| Linked list | `tower.py` | Tower + insert / remove |
| Recursion | `tower.py` | `load_above` / safety |
| Stack | `tower.py` | Collapse failed floors |
| Sequential search | `tower.py` | `find_weakest_floor` |
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
  test_core.py     # Headless tests
  img/             # PNG assets for cells
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd skyscraper_race
python test_core.py   # should print All core tests passed
python main.py        # opens the board
```

### Controls
- **ROLL** cell or key `R` — roll
- **SCRAP** cell or key `S` — discard roll
- Click your tower column / row — place floor at that height
- Number keys `0`–`9` — place at that linked-list index

## Status

**Done**
- Material hash table + roll / full_decode (guide test cases)
- `Floor` with multiplicative damage + capacity property
- `Tower` doubly linked list: insert, remove, traverse
- Recursive `load_above`, safety ratio, weakest-floor scan
- Stack-based `collapse` with cascade
- `Game` turn loop: roll / scrap / place / win
- Board UI wired to game logic
- Headless tests in `test_core.py`

**Still optional**
- Challenge system (`challenges.py` — heap + binary search)
- Nicer art than placeholder PNGs
- Presentation Q&A cards per teammate

## Course notes

- Delivery: **23 Nov**; presentations **30 Nov / 1 Dec**
- Every teammate must be able to answer DSA questions (round-robin)
- Prefer implementing and understanding the code yourselves; use AI to validate
