"""Tests — run from repo root: python test_core.py"""

from logic.algorithms.challenges import (
    make_challenge_heights,
    make_heap,
    run_challenges,
)
from logic.algorithms.roll import decode_roll, full_decode
from logic.algorithms.tower import Tower
from logic.data.floor import Floor
from logic.data.materials import get_material, units_from_amount


def make_test_floor(name, height, weight, max_load):
    from logic.data.constants import CAPACITY_CONSTANT

    units = 100
    return Floor({
        "material_name": name,
        "tier": "test",
        "height": height,
        "units": units,
        "weight_per_unit": weight / units,
        "capacity_mult": max_load / (height * CAPACITY_CONSTANT),
        "image": name,
    })


def test_materials():
    assert get_material("common", 3)["name"] == "wood"
    assert get_material("strong", 9)["name"] == "concrete"
    assert units_from_amount(7) == 1050


def test_roll():
    parts = decode_roll(47382)
    assert parts["tier"] == "common"
    assert parts["amount"] == 7
    assert parts["height"] == 10
    assert full_decode(47382)["material_name"] == "wood"
    assert decode_roll(10000)["amount"] == 10


def test_floor():
    from logic.data.constants import CAPACITY_CONSTANT

    floor = Floor(full_decode(47382))
    assert floor.get_weight() == 1050
    assert floor.get_max_load() == 1.0 * 10 * CAPACITY_CONSTANT
    floor.take_damage(0.1)
    assert abs(floor.health - 0.9) < 1e-9


def test_tower_list():
    tower = Tower()
    floor_a = make_test_floor("A", 10, 100, 200)
    floor_b = make_test_floor("B", 8, 100, 200)
    tower.insert_at(0, floor_a)
    tower.insert_at(1, floor_b)
    names = [f.material_name for f in tower.floors_from_ground()]
    assert names == ["A", "B"]
    tower.remove_at(0)
    assert tower.floors[0] is floor_b


def test_stability_collapse():
    tower = Tower()
    tower.insert_at(0, make_test_floor("Steel", 10, 250, 2000))
    tower.insert_at(1, make_test_floor("Weak", 5, 50, 30))
    tower.insert_at(2, make_test_floor("Heavy", 12, 300, 900))
    # weak is index 1 — collapse removes index 1 and above
    fallen, meters_lost = tower.collapse(1)
    assert tower.floor_count() == 1
    assert meters_lost == 17
    assert len(fallen) == 2


def test_challenges():
    from logic.data.constants import (
        CHALLENGE_MAX_HEIGHT,
        CHALLENGE_MIN_GAP,
        CHALLENGE_MIN_HEIGHT,
        NUM_CHALLENGES,
    )

    heights = make_challenge_heights()
    assert len(heights) == NUM_CHALLENGES
    for height in heights:
        assert CHALLENGE_MIN_HEIGHT <= height <= CHALLENGE_MAX_HEIGHT
    for i in range(len(heights)):
        for j in range(i + 1, len(heights)):
            assert abs(heights[i] - heights[j]) >= CHALLENGE_MIN_GAP

    heap = make_heap([10, 50, 90])
    tower = Tower()
    tower.insert_at(0, make_test_floor("G", 40, 50, 9000))
    _messages, fired = run_challenges(tower, heap)
    assert fired == [10]
    assert heap[0] == 50


def test_game():
    from logic.algorithms.game import Game

    game = Game("A", "B", enable_challenges=False)
    game.roll()
    game.place_on_top()
    assert game.players[0].tower.floor_count() == 1

    while game.current_index == 0:
        if game.phase == "roll":
            game.roll()
        else:
            game.scrap_roll()
    assert game.current_player().name == "B"


def test_recursion_and_scan():
    tower = Tower()
    tower.insert_at(0, make_test_floor("Base", 10, 100, 50000))
    tower.insert_at(1, make_test_floor("Mid", 10, 100, 50000))
    tower.insert_at(2, make_test_floor("Top", 10, 100, 50000))
    # load on ground = mid + top weights = 200
    assert tower.load_above(0) == 200
    assert tower.load_above(2) == 0
    assert tower.find_weakest_floor_index() is not None


if __name__ == "__main__":
    for test in (
        test_materials,
        test_roll,
        test_floor,
        test_tower_list,
        test_stability_collapse,
        test_challenges,
        test_game,
        test_recursion_and_scan,
    ):
        test()
        print(f"OK  {test.__name__}")
    print("\nAll core tests passed!")
