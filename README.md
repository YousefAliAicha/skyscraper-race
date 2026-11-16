# Skyscraper Race

A 2-player race to build a skyscraper to **150 meters**.  
Python 3 + [game2dboard](https://pypi.org/project/game2dboard/).

You roll materials, choose **where** each floor goes in the tower, keep the structure stable under its own weight, and survive height-triggered challenges. First tower to 150 m wins.

This project is also a DSA showcase: six structures/algorithms are used because they match the game rules, not because a checklist said so. The sections below explain **what** the game does and **why** the code is shaped this way.

---

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
python test_core.py   # unit tests (no window)
python demo.py        # console autoplay (no window)
python main.py        # full game (needs Tk + game2dboard)
```

### Playable Jupyter notebook (one file)

Download **[`Skyscraper_Race_Play.ipynb`](Skyscraper_Race_Play.ipynb)** alone — it embeds the whole game + all 6 DSAs. No other project files required.

```bash
pip install notebook          # or: pip install jupyterlab
jupyter notebook Skyscraper_Race_Play.ipynb
```

Or open the file in VS Code / Google Colab → **Run all**.

- **Auto demo** cell plays by itself (no typing).
- Uncomment `play()` for keyboard turns (`r` / `p` / `i N` / `s`).
- Optional: `pip install ipywidgets` then uncomment `play_widgets()` for buttons.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YousefAliAicha/skyscraper-race/blob/main/Skyscraper_Race_Play.ipynb)

---

## How to play

| Control | Action |
|---------|--------|
| `R` or **ROLL** | Get a new floor |
| `↑` / `↓` | Move the place arrow |
| `Enter` / `Space` | Place at the arrow |
| Click your tower | Move the arrow to that height |
| `S` or **SCRAP** | Discard the roll |
| `Esc` | Leave to menu |

- **P1** builds on the left, **P2** on the right.
- Each turn gives **3 rolls**. You may place or scrap each one.
- First player whose tower reaches **150 m** wins.

**Strategy tip:** strong materials (steel / concrete) belong near the ground — they carry everything above them. Junk (toothpicks / rotten wood) belongs on top, or should be scrapped. Placing junk under a heavy floor is how towers collapse.

---

## How a turn works

Logic lives in `game.py` with **no GUI**. The UI (`match.py`) only calls these methods and draws the result. That split exists so you can test and demo the game without opening a window (`test_core.py`, `demo.py`).

```
roll  →  place or scrap  →  challenges  →  stability check  →  win check
```

1. **Roll** — decode a 5-digit number into a floor recipe (material + height).
2. **Place** — insert that floor at a chosen slot (0 = ground, N = on top), **or scrap** it.
3. **Challenges** — if the tower just crossed a challenge height, apply damage.
4. **Stability** — if any floor cannot hold the weight above it, **collapse** that floor and everything above.
5. **Win** — if height ≥ 150 m, the game ends.

---

## Rolls and materials

A roll is a random integer from `10000` to `99999` (`roll.py`). Digits map to:

| Digits | Meaning |
|--------|---------|
| 1 | Tier: junk / common / strong (see `TIER_RANGES` in `constants.py`) |
| 2 | Amount of material (0 counts as 10) |
| 3 | Which material inside that tier |
| 4 + 5 | Height in meters (minimum 2) |

**Why a 5-digit roll?** It keeps “random loot” as one number you can print, test, and replay, instead of generating four separate random values that are hard to reproduce in tests.

**Why a dict for materials?** Stats are looked up by `(tier, group)`. A dict is the natural hash table: one key → one material, O(1) lookup, and adding a new material is one new table entry — not a growing `if/elif` chain. See `materials.py`.

Material **strength** and **weight** feed the capacity formula below. Junk is light but weak; steel is heavy but very strong.

---

## Stability (why towers fall)

Every floor has:

- **weight** — `units × weight_per_unit`
- **max load** — how much weight it can support right now:

```
max_load = strength × height × CAPACITY_CONSTANT × health
```

`CAPACITY_CONSTANT` (1200) is a balance knob in `constants.py`. Height is in the formula so taller floors of the same material can hold more — a short strong slab still matters less than a tall one of the same type.

`health` starts at `1.0`. Challenges multiply it down (10% damage twice → `0.9 × 0.9`).

For each floor we compute the **load above** it (sum of weights of every floor higher up). If `max_load / load < 1.0`, that floor fails.

---

## The six DSA choices (and why)

Each structure maps to a real rule of the game.

### 1. Hash table — `materials.py`

**What:** Python `dict` keyed by `(tier, group)`.

**Why:** Material lookup is “given a roll, what are the stats?” That is a dictionary problem. We did **not** hard-code materials inside `roll.py`, so balance tweaks stay in one table.

### 2. Doubly linked list — `floor.py` + `tower.py`

**What:** Each `Floor` has `above` and `below` pointers. The `Tower` tracks `ground` and `top`.

**Why not a Python list?** You can place a floor **anywhere** in the tower (not only on top). A linked list makes insert/remove at an arbitrary height a pointer rewrite, and the “neighbor” idea matches the physical stack of floors. A dynamic array would also work, but the project uses a list because insert-in-the-middle and collapse are the operations students are meant to implement and explain.

`insert_at(position, floor)`:

- `0` → new ground  
- `size` → new top  
- otherwise → splice between two existing floors  

### 3. Recursion — `tower.load_above`

**What:** Weight resting on a floor = weight of the floor above + `load_above(that floor)`. Base case: nothing above the top → `0`.

**Why recursion?** The definition is recursive (“load on me = that floor’s weight + load on that floor”). A loop would also work; recursion is used because it matches the definition and walks the linked list naturally.

### 4. Stack — `tower.collapse`

**What:** When a floor breaks, remove it and **everything above** it.

**Why a stack?** We first walk upward pushing floors onto a list (`append`), then `pop` so we always remove from the **current top** downward. That last-in-first-out order keeps the linked-list pointers valid (never delete a floor while something is still linked above it in a messy order). After the main collapse, we check again in case a lower floor is now overloaded (cascade).

### 5. Min-heap — `challenges.py`

**What:** Each player gets a few challenge heights. They live in a min-heap (`heapq`).

**Why a heap?** Challenges must fire in **height order** — the next event is always the smallest remaining height. A min-heap gives “peek next” and “pop next” cheaply (`heap[0]` / `heappop`). A sorted list would also work for three events; the heap is here so the “next event by priority” idea is explicit and still correct if you add more challenges later.

Heights are spaced (`CHALLENGE_MIN_GAP`) so you do not get three disasters in the same few meters.

### 6. Binary search — `challenges.find_floor_at_height`

**What:** Build a cumulative height list from ground up (sorted by construction), then `bisect_right` to find which floor contains a given meter mark.

**Why binary search?** “Which floor is at 0.1 m / 55 m / …?” is a search on a sorted cumulative array. Linear scan would work for tiny towers; bisect shows the standard approach and is used when the drunk-driver event targets the ground floor by height.

---

## Project layout

```
Skyscraper_Race_Play.ipynb   self-contained playable notebook
skyscraper_race/
  constants.py    all balance numbers in one place
  materials.py    material dict (hash table)
  roll.py         5-digit roll → floor recipe
  floor.py        one floor / linked-list node
  tower.py        linked list, load_above, collapse
  challenges.py   challenge heap + height search
  player.py       name, tower, rolls, challenge heap
  game.py         turn logic only (no GUI)
  screens.py      splash / menu / how-to / win
  match.py        board + sidebar for one match
  main.py         app loop (menu ↔ match)
  assets.py       generates PNGs into img/
  test_core.py    unit tests
  demo.py         headless autoplay
  img/            sprites used by game2dboard
```

**Why so many small files?** So each DSA lives in a place you can open and finish reading. UI is separated (`screens.py`, `match.py`, `main.py`) so learning `tower.py` does not require reading fullscreen Tk code.

**Why `constants.py`?** Every magic number (win height, damage %, board size) is named and tunable without hunting through algorithms.

---

## UI notes

- **Fullscreen** menu and match so the board is readable.
- **Left sidebar** shows turn, last action, result, heights, and next challenge — the board alone cannot show that text clearly.
- **Place arrow** (`↑↓` + Enter) exists so you can insert in the middle of the tower, not only on top. That is what makes the linked-list insert meaningful in play.
- Empty board cells use `None`, not `""`. game2dboard treats `""` as an image filename and breaks if `img/` has leftover files.

---

## Learning path

Read in this order:

1. `constants.py` — what you can tune  
2. `materials.py` — hash table  
3. `roll.py` — how a floor is born  
4. `floor.py` — one node  
5. `tower.py` — linked list + recursion + stack  
6. `challenges.py` — heap + binary search  
7. `game.py` — how the pieces connect  
8. `match.py` / `main.py` — UI only after the logic makes sense  

After any logic change:

```bash
python test_core.py
```

---

## Balancing knobs

| Constant | Effect if you raise it |
|----------|-------------------------|
| `TARGET_HEIGHT` | Longer games |
| `CAPACITY_CONSTANT` | Towers hold more → fewer collapses |
| `ROLLS_PER_TURN` | Faster building per turn |
| `EARTHQUAKE_DAMAGE` etc. | Harsher challenges |
| `NUM_CHALLENGES` | More heap events per player |

Change one value at a time, then run `demo.py` or play a match to feel the difference.
