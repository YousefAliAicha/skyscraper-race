# Skyscraper Race Lite

2-player race to **150 m**. Python + `game2dboard`.

| DSA | Where |
|-----|--------|
| Hash table | `materials.py` |
| Linked list | `tower.py` |
| Recursion | `load_above` |
| Stack | `collapse` |

```bash
git clone -b cursor/project-scaffold-a034 https://github.com/YousefAliAicha/skyscraper-race.git
cd skyscraper-race
pip install -r requirements.txt
cd skyscraper_race
python test_core.py
python demo.py
python main.py
```

## How to play (GUI)

1. **ROLL** (or `R`) — get a floor  
2. **Place it**
   - **`Space` / Enter** — put on **TOP** (easiest)
   - Or click the **>>> TOP** cell on *your* side (LEFT=P1, RIGHT=P2)
   - Or click an existing floor row to insert there  
3. **SCRAP** / `S` — discard the roll  
4. 3 rolls each turn → first to 150 m wins  

Safety column: `ok` / `1.2` / `!0.8` (risky) / `FAIL`
