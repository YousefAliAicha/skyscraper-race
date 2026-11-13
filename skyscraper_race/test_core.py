"""Headless tests — run: python test_core.py"""

from challenges import (
    find_floor_at_height,
    generate_challenge_heights,
    make_heap,
    process_challenges,
)
from materials import calculate_units, get_material
from roll import decode_roll, full_decode, generate_roll
from tower import Floor, Tower


def make_test_floor(name, height, weight, capacity):
    units = 100
    return Floor({
        "material_name": name,
        "tier": "test",
        "height": height,
        "units": units,
        "weight_per_unit": weight / units,
        "capacity_mult": capacity / units,
        "image": name,
    })


def verify_chain(t):
    if t.floor_count() == 0:
        assert t.ground is None and t.top is None
        return
    cur, n = t.ground, 1
    assert cur.below is None
    while cur.above:
        assert cur.above.below is cur
        cur = cur.above
        n += 1
    assert cur is t.top and cur.above is None and n == t.floor_count()


def test_materials():
    assert get_material("common", 3)["name"] == "wood"
    assert get_material("strong", 9)["name"] == "concrete"
    assert calculate_units(7) == 1050


def test_roll():
    r = decode_roll(47382)
    assert (r["tier"], r["amount"], r["height"]) == ("common", 7, 10)
    assert full_decode(47382)["material_name"] == "wood"
    assert decode_roll(10000)["amount"] == 10


def test_floor():
    f = Floor(full_decode(47382))
    assert f.total_weight == 1050 and f.capacity == 1050
    f.take_damage(0.1)
    assert abs(f.integrity - 0.9) < 1e-9


def test_tower():
    t = Tower()
    a = make_test_floor("A", 10, 100, 200)
    b = make_test_floor("B", 8, 100, 200)
    t.insert_at(0, a)
    t.insert_at(1, b)
    assert [f.material for f in t.traverse()] == ["A", "B"]
    verify_chain(t)
    t.remove(a)
    assert t.ground is b
    verify_chain(t)


def test_stability_collapse():
    t = Tower()
    f1 = make_test_floor("Steel", 10, 250, 2000)
    f2 = make_test_floor("Weak", 5, 50, 30)
    f3 = make_test_floor("Heavy", 12, 300, 900)
    t.insert_at(0, f1)
    t.insert_at(1, f2)
    t.insert_at(2, f3)
    fallen, lost = t.collapse(f2)
    assert t.floor_count() == 1 and lost == 17 and len(fallen) == 2


def test_challenges():
    hs = generate_challenge_heights()
    assert len(hs) == 4
    assert all(30 <= h <= 140 for h in hs)
    for i in range(len(hs)):
        for j in range(i + 1, len(hs)):
            assert abs(hs[i] - hs[j]) >= 15

    t = Tower()
    t.insert_at(0, make_test_floor("A", 20, 100, 5000))
    t.insert_at(1, make_test_floor("B", 20, 100, 5000))
    assert find_floor_at_height(t, 5) is t.ground
    assert find_floor_at_height(t, 25) is t.top

    heap = make_heap([10, 50, 90])
    # tower at 40m should trigger 10 only
    t2 = Tower()
    t2.insert_at(0, make_test_floor("G", 40, 50, 9000))
    events, trig = process_challenges(t2, heap)
    assert trig == [10]
    assert heap[0] == 50


def test_game():
    from game import Game
    g = Game("A", "B", enable_challenges=False)
    g.roll()
    g.place_on_top()
    assert g.players[0].tower.floor_count() == 1
    while g.current_index == 0:
        if g.phase == "roll":
            g.roll()
        else:
            g.scrap_roll()
    assert g.current_player().name == "B"


if __name__ == "__main__":
    for fn in (
        test_materials, test_roll, test_floor, test_tower,
        test_stability_collapse, test_challenges, test_game,
    ):
        fn()
        print(f"OK  {fn.__name__}")
    print("\nAll core tests passed!")
