# Skyscraper Race Lite

Fullscreen 2-player race to **150 m**. Python + `game2dboard`.

## DSA

| Topic | Where |
|-------|--------|
| Hash table | `materials.py` |
| Linked list | `tower.py` |
| Recursion | `load_above` |
| Stack | `collapse` |
| Min-heap + binary search | `challenges.py` |

## Run

```bash
git clone -b cursor/project-scaffold-a034 https://github.com/YousefAliAicha/skyscraper-race.git
cd skyscraper-race
pip install -r requirements.txt
# Ubuntu: sudo apt install python3-tk
cd skyscraper_race
python test_core.py
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| `R` | Roll |
| `↑` `↓` | Move place **arrow** (any height) |
| `Enter` / `Space` | Place at the arrow |
| Click tower row | Move arrow there |
| `S` | Scrap roll |
| `Esc` | Back to menu |

**Tip:** steel/concrete at the **base**, junk on **top** (or scrap). First to 150 m wins.

## Team / presentation

See **[TEAM_GUIDE.md](TEAM_GUIDE.md)** — DSA cheat sheet, file ownership, Q&A practice, what we cut.
