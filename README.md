# Skyscraper Race Lite

2-player race to **150 m**. Python + `game2dboard`.

## DSA

| Topic | Where |
|-------|--------|
| Hash table | `materials.py` |
| Linked list | `tower.py` insert/remove |
| Recursion | `tower.load_above` |
| Stack | `tower.collapse` |
| Min-heap | `challenges.py` schedule |
| Binary search | `find_floor_at_height` |

## Run

```bash
git clone -b cursor/project-scaffold-a034 https://github.com/YousefAliAicha/skyscraper-race.git
cd skyscraper-race
pip install -r requirements.txt
# GUI needs tkinter:  sudo apt install python3-tk
cd skyscraper_race
python test_core.py
python demo.py
python main.py
```

## Controls

| Action | How |
|--------|-----|
| Roll | green **ROLL** or `R` |
| Place on top | **Space** / Enter (easiest) |
| Place elsewhere | click your tower / green **TOP** |
| Scrap | red **SCRAP** or `S` |

P1 = left tower, P2 = right. First to 150 m wins.  
Yellow **!** chip = next challenge height (earthquake / windstorm / drunk driver).
