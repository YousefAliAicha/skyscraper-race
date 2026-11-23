# Skyscraper Race

A 2-player race to build a skyscraper to **150 meters**.

Roll materials, choose **where** each floor goes, keep the tower stable, survive height challenges. First to 150 m wins.

**Focus of this project:** 3 data structures + 3 algorithms in `logic/`.  
The desktop UI in `game/` and GitHub docs were assisted by AI — they are not the graded core.

---

## The 6 graded pieces

### Data structures
1. **Hash table** (`logic/data/materials.py`) — material stats lookup  
2. **List / array** (`logic/algorithms/tower.py`) — tower floors (`[0]` = ground)  
3. **Min-heap** (`logic/algorithms/challenges.py`) — next challenge height  

### Algorithms
1. **Recursion** — `Tower.load_above(index)` weight above a floor  
2. **Heap peek / pop** — fire challenges when height catches up  
3. **Sequential search** — `find_weakest_floor_index()` worst safety ratio  

---

## Folder layout

```
logic/                  # graded DSA + game rules
  data/
    constants.py
    materials.py        # hash table
    floor.py
  algorithms/
    tower.py            # list + recursion + sequential search
    challenges.py       # min-heap
    roll.py
    player.py
    game.py             # turns (no GUI)

game/                   # UI only (AI-assisted)
  main.py
  match.py
  screens.py
  assets.py
  img/

test_core.py
demo.py
Skyscraper_Race_Play.ipynb
README.md
```

---

## Install

```bash
git clone https://github.com/YousefAliAicha/skyscraper-race.git
cd skyscraper-race
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Check Tk (desktop GUI only):

```bash
python3 -c "import tkinter; print('tk ok', tkinter.TkVersion)"
```

### macOS
```bash
brew install python
# if import tkinter fails:
brew install python-tk
```
Recreate the venv with that Homebrew Python, then `pip install -r requirements.txt`.

### Ubuntu / Debian
```bash
sudo apt install python3-tk
```

---

## Run

From the **repo root**:

```bash
python test_core.py      # unit tests
python demo.py           # console autoplay
python -m game.main      # desktop GUI
```

### Notebook
Download [`Skyscraper_Race_Play.ipynb`](Skyscraper_Race_Play.ipynb) and Run All (stdlib only for the demo cells).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YousefAliAicha/skyscraper-race/blob/main/Skyscraper_Race_Play.ipynb)

---

## How to play (GUI)

| Control | Action |
|---------|--------|
| `R` / ROLL | Roll a floor |
| `↑` `↓` | Move place arrow |
| Enter / Space | Place |
| `S` / SCRAP | Discard roll |
| Esc | Menu |

P1 left, P2 right. 3 rolls per turn. Strong materials at the bottom.

---

## Why these 6 (short)

| Piece | Game problem | Why this tool |
|-------|--------------|---------------|
| Hash table | Roll → material stats | O(1) lookup |
| List | Floors in order; insert at a slot | Natural index = height slot |
| Min-heap | Next challenge = smallest height | Peek O(1), pop O(log n) |
| Recursion | Weight above floor *i* | Defined as weight(i+1) + load(i+1) |
| Heap peek/pop | Did we hit the next event? | Priority = minimum height |
| Sequential search | Which floor is weakest? | Must check each floor’s ratio |

---

## AI note

AI was used to help build the **UI** (`game/`) and **GitHub / README** documentation. The **logic/** package is the course focus: data structures, algorithms, and turn rules.
