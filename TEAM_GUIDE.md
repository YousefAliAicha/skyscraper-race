# Skyscraper Race — Team Guide

Read this before the presentation. Know **your file** cold, and be able to explain every DSA topic in one minute.

---

## 1. What the game is

2 players race to **150 m**. Each turn you roll a floor, choose where to insert it in your tower (linked list), and hope it doesn’t collapse. Challenges damage the tower as you climb. First to 150 m wins.

**Run**
```bash
cd skyscraper_race
python test_core.py   # must pass
python main.py        # game
```

**Controls:** `R` roll · `↑↓` arrow · `Enter` place · `S` scrap · `Esc` menu

**Strategy tip:** steel/concrete at the **bottom**, junk on **top** (or scrap junk).

---

## 2. Who owns what

| Person | File(s) | What to say if asked |
|--------|---------|----------------------|
| A | `materials.py` | Hash table for O(1) material lookup |
| B | `tower.py` (list) | Doubly linked list insert/remove |
| C | `tower.py` (load) | Recursive `load_above` |
| D | `tower.py` (collapse) | Stack removes failed floor + above |
| E | `challenges.py` | Min-heap schedule + binary search |
| F | `game.py` / `main.py` | Turns, UI, wiring |

Everyone must still understand **all** topics (round-robin Q&A).

---

## 3. DSA cheat sheet (memorize)

### Hash table — `materials.py`
- **Problem:** Every roll needs material stats fast.
- **Why dict:** O(1) average lookup by `(tier, "low"|"high")`.
- **Why not if/elif:** Harder to maintain; grows into an O(n) branch chain.
- **Say:** “Data separate from logic — add a material by adding one dict entry.”

### Linked list — `Tower` in `tower.py`
- **Problem:** Insert a floor at any height every turn.
- **Nodes:** `Floor` with `.above` / `.below`.
- **Why list not array:** Insert in the middle is pointer changes (after O(n) walk). Matches a physical tower.
- **Ops:** `insert_at`, `remove`, `traverse`.
- **Complexity:** walk O(n), insert/remove O(1) once you have the node. n ≈ 10–15 floors.

### Recursion — `load_above`
```text
load_above(floor):
  if no floor above → 0
  else → weight(above) + load_above(above)
```
- **Problem:** Each floor must hold everything above it.
- **Safety:** `capacity / load_above` — fail if &lt; 1.
- **Why recursion:** The load above N depends on the load above N+1. Natural recursive structure.
- **If asked about O(n²):** “Checking every floor with recursion is O(n²); a top-down loop is O(n). n is tiny; we keep recursion because it’s a course topic.”

### Sequential search — `find_weakest_floor`
- Walk all floors, keep the minimum safety ratio. O(n). Fine for small n.

### Stack — `collapse`
- **Problem:** When a floor fails, everything above falls.
- **How:** Push failed→top onto a stack, then `pop` (LIFO) and `remove` top-first so pointers stay clean.
- **Why stack:** Last placed (top) falls first; always remove current top.
- **Cascade:** After removal, check stability again (rare).

### Min-heap — challenge heights
- **Problem:** “What’s the next challenge height my tower will hit?”
- **How:** `heapq` of heights. While `heap[0] <= tower_height`, pop and apply damage.
- **Why heap:** Repeated “get minimum + maybe insert” → O(log n) push/pop.
- **Why not sorted list:** Getting min is O(1), but re-insert is O(n). Heap is the right ADT.

### Binary search — `find_floor_at_height`
- Cumulative heights are sorted (each floor adds height).
- `bisect_right` finds which floor band contains height h.
- **Why:** O(log n) on a sorted cumulative array. Used when targeting the ground (drunk driver) / height lookups.

---

## 4. Call flow (one turn)

```text
roll() → full_decode → material hash lookup
place_floor(slot)
  → Tower.insert_at          (linked list)
  → process_challenges       (heap pop; may damage floors)
  → check_stability
       load_above            (recursion)
       find_weakest_floor    (linear scan)
  → maybe collapse           (stack)
  → win if height ≥ 150
```

---

## 5. What we cut (professor will ask)

| Cut | Why |
|-----|-----|
| Scaffolding / graph collapse | Too complex; stack collapse is enough without bridges |
| Challenge re-queue after collapse | Made the game nearly unwinnable |
| Fancy HUD / animations | Clarity &gt; chrome for the demo |

**Line:** “We simplified where the full design didn’t change the DSA we needed to show.”

---

## 6. Complexity table (slide)

| Structure / algo | Where | Time |
|------------------|--------|------|
| Hash table | materials | O(1) avg lookup |
| Linked list insert | tower | O(n) walk + O(1) link |
| Recursion load_above | tower | O(n) per floor |
| Weakest-floor scan | tower | O(n) |
| Stack collapse | tower | O(k) removals |
| Min-heap challenges | challenges | O(log n) pop/push |
| Binary search height | challenges | O(log n) |

---

## 7. Presentation checklist

1. Live demo: roll → move arrow → place → show a collapse if it happens → climb toward 150.
2. Each person explains **their** structure in ≤60 seconds (problem → structure → complexity → why not the alternative).
3. Practice round-robin: random questions to random people.
4. Run `python test_core.py` before presenting.

### Likely questions
- Why linked list not Python `list`?
- Show `load_above` base case and recursive case.
- Why stack for collapse?
- Why heap for challenges?
- What did you abandon and why?
- Is recursive stability optimal? (Mention O(n) alternative.)

---

## 8. File map (compact)

| File | Role |
|------|------|
| `constants.py` | Tunable numbers |
| `materials.py` | Hash table |
| `roll.py` | 5-digit decode |
| `tower.py` | Floor node + linked list + recursion + stack |
| `challenges.py` | Heap + bisect |
| `player.py` | Name, tower, rolls, challenge heap |
| `game.py` | Turn logic (no GUI) |
| `main.py` | game2dboard + sidebar UI |
| `screens.py` | Menu / how-to / win |
| `assets.py` | PNG generator |
| `test_core.py` | Headless tests |
| `demo.py` | Console autoplay |
