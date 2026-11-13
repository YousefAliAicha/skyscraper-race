# Skyscraper Race Lite

2-player race to **150 m**. Python + `game2dboard`.

| DSA | Where |
|-----|--------|
| Hash table | `materials.py` |
| Linked list | `tower.py` insert/remove |
| Recursion | `tower.load_above` |
| Stack | `tower.collapse` |
| Heap + bisect | `challenges.py` (optional, not wired) |

```bash
pip install -r requirements.txt
cd skyscraper_race
python test_core.py   # unit tests
python demo.py        # console autoplay
python main.py        # GUI
```

**GUI:** ROLL / `R`, SCRAP / `S`, click your tower column to place, or digit keys.
