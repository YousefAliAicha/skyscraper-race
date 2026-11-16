"""Tests — run: python test_core.py

Read these to see how each module is meant to be used.
"""

from challenges import (
    find_floor_at_height,
    make_challenge_heights,
    make_heap,
    run_challenges,
)
from materials import get_material, units_from_amount
from roll import decode_roll, full_decode
from floor import Floor
from tower import Tower


def make_test_floor(name, height, weight, max_load):
    """Build a Floor with exact weight / max_load for tests."""
    from constants import CAPACITY_CONSTANT

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


def check_links(tower):
    """Make sure above/below pointers still match."""
    if tower.floor_count() == 0:
        assert tower.ground is None and tower.top is None
        return

    floor = tower.ground
    count = 1
    assert floor.below is None
    while floor.above is not None:
        assert floor.above.below is floor
        floor = floor.above
        count += 1
    assert floor is tower.top
    assert floor.above is None
    assert count == tower.floor_count()


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
    from constants import CAPACITY_CONSTANT

    floor = Floor(full_decode(47382))  # wood, height 10, units 1050
    assert floor.get_weight() == 1050
    assert floor.get_max_load() == 1.0 * 10 * CAPACITY_CONSTANT
    floor.take_damage(0.1)
    assert abs(floor.health - 0.9) < 1e-9
    assert abs(floor.get_max_load() - 0.9 * 10 * CAPACITY_CONSTANT) < 1e-9


def test_tower():
    tower = Tower()
    floor_a = make_test_floor("A", 10, 100, 200)
    floor_b = make_test_floor("B", 8, 100, 200)
    tower.insert_at(0, floor_a)
    tower.insert_at(1, floor_b)
    names = [floor.material_name for floor in tower.floors_from_ground()]
    assert names == ["A", "B"]
    check_links(tower)
    tower.remove(floor_a)
    assert tower.ground is floor_b
    check_links(tower)


def test_stability_collapse():
    tower = Tower()
    steel = make_test_floor("Steel", 10, 250, 2000)
    weak = make_test_floor("Weak", 5, 50, 30)
    heavy = make_test_floor("Heavy", 12, 300, 900)
    tower.insert_at(0, steel)
    tower.insert_at(1, weak)
    tower.insert_at(2, heavy)
    fallen, meters_lost = tower.collapse(weak)
    assert tower.floor_count() == 1
    assert meters_lost == 17
    assert len(fallen) == 2


def test_challenges():
    from constants import (
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

    # binary search
    tower = Tower()
    tower.insert_at(0, make_test_floor("A", 20, 100, 5000))
    tower.insert_at(1, make_test_floor("B", 20, 100, 5000))
    assert find_floor_at_height(tower, 5) is tower.ground
    assert find_floor_at_height(tower, 25) is tower.top

    # min-heap: tower at 40m should fire only the 10m challenge
    heap = make_heap([10, 50, 90])
    tower2 = Tower()
    tower2.insert_at(0, make_test_floor("G", 40, 50, 9000))
    _messages, fired = run_challenges(tower2, heap)
    assert fired == [10]
    assert heap[0] == 50


def test_game():
    from game import Game

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


if __name__ == "__main__":
    for test in (
        test_materials,
        test_roll,
        test_floor,
        test_tower,
        test_stability_collapse,
        test_challenges,
        test_game,
    ):
        test()
        print(f"OK  {test.__name__}")
    print("\nAll core tests passed!")
