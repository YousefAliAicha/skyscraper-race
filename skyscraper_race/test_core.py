"""Headless tests — run: python test_core.py"""

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
    assert get_material("common", 7)["name"] == "brick"
    assert get_material("strong", 0)["name"] == "steel"
    assert calculate_units(7) == 1050


def test_roll():
    r = decode_roll(47382)
    assert (r["tier"], r["amount"], r["material_digit"], r["height"]) == (
        "common", 7, 3, 10,
    )
    full = full_decode(47382)
    assert full["material_name"] == "wood" and full["units"] == 1050
    assert decode_roll(10000)["amount"] == 10
    assert decode_roll(21500)["height"] == 2
    for _ in range(100):
        n = generate_roll()
        assert 10000 <= n <= 99999


def test_floor():
    f = Floor(full_decode(47382))
    assert f.total_weight == 1050 and f.capacity == 1050
    f.take_damage(0.1)
    assert abs(f.integrity - 0.9) < 1e-9 and abs(f.capacity - 945) < 1e-9


def test_tower():
    t = Tower()
    a, b, c = [make_test_floor(n, h, 100, 200) for n, h in
               (("A", 10), ("B", 8), ("C", 12))]
    t.insert_at(0, a)
    t.insert_at(1, b)
    t.insert_at(0, c)  # C, A, B
    assert [f.material for f in t.traverse()] == ["C", "A", "B"]
    verify_chain(t)
    t.remove(a)
    assert [f.material for f in t.traverse()] == ["C", "B"]
    verify_chain(t)


def test_stability_collapse():
    t = Tower()
    f1 = make_test_floor("Steel", 10, 250, 2000)
    f2 = make_test_floor("Weak", 5, 50, 30)
    f3 = make_test_floor("Heavy", 12, 300, 900)
    t.insert_at(0, f1)
    t.insert_at(1, f2)
    t.insert_at(2, f3)
    assert t.load_above(f1) == 350
    fallen, lost = t.collapse(f2)
    assert t.floor_count() == 1 and lost == 17 and len(fallen) == 2
    verify_chain(t)


def test_game():
    from game import Game
    g = Game("A", "B")
    g.roll()
    g.place_floor(0)
    assert g.players[0].tower.floor_count() == 1
    while g.current_index == 0:
        if g.phase == "roll":
            g.roll()
        else:
            g.scrap_roll()
    assert g.current_player().name == "B"


if __name__ == "__main__":
    for fn in (test_materials, test_roll, test_floor, test_tower,
               test_stability_collapse, test_game):
        fn()
        print(f"OK  {fn.__name__}")
    print("\nAll core tests passed!")
