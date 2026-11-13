"""Headless tests for materials, roll, tower, stability, collapse."""

from materials import calculate_units, get_material
from roll import decode_roll, full_decode, generate_roll
from tower import Floor, Tower, make_test_floor


def verify_chain(tower: Tower) -> None:
    if tower.floor_count() == 0:
        assert tower.ground is None
        assert tower.top is None
        return
    current = tower.ground
    assert current.below is None
    count = 1
    while current.above is not None:
        nxt = current.above
        assert nxt.below is current
        current = nxt
        count += 1
    assert current is tower.top
    assert current.above is None
    assert count == tower.floor_count()


def test_materials():
    cases = [
        ("junk", 0, "toothpicks", 0.5, 0.3),
        ("junk", 4, "toothpicks", 0.5, 0.3),
        ("junk", 5, "rotten_wood", 0.8, 0.2),
        ("junk", 9, "rotten_wood", 0.8, 0.2),
        ("common", 0, "wood", 1.0, 1.0),
        ("common", 4, "wood", 1.0, 1.0),
        ("common", 5, "brick", 2.0, 1.6),
        ("common", 9, "brick", 2.0, 1.6),
        ("strong", 0, "steel", 2.5, 4.5),
        ("strong", 4, "steel", 2.5, 4.5),
        ("strong", 5, "concrete", 3.0, 3.0),
        ("strong", 9, "concrete", 3.0, 3.0),
    ]
    for tier, digit, name, weight, cap in cases:
        mat = get_material(tier, digit)
        assert mat["name"] == name
        assert mat["weight"] == weight
        assert mat["capacity"] == cap
    assert calculate_units(1) == 150
    assert calculate_units(10) == 1500
    assert calculate_units(5) == 750


def test_roll():
    r = decode_roll(47382)
    assert r == {
        "roll": 47382,
        "tier": "common",
        "amount": 7,
        "material_digit": 3,
        "height": 10,
    }
    full = full_decode(47382)
    assert full["material_name"] == "wood"
    assert full["units"] == 1050
    assert full["total_weight"] == 1050.0
    for _ in range(200):
        n = generate_roll()
        d = decode_roll(n)
        assert 10000 <= n <= 99999
        assert 1 <= d["amount"] <= 10
        assert 2 <= d["height"] <= 18


def test_floor():
    data = full_decode(47382)
    f = Floor(data)
    assert f.material_name == "wood"
    assert f.height == 10
    assert f.total_weight == 1050.0
    assert f.capacity == 1050.0
    f.take_damage(0.10)
    assert abs(f.integrity - 0.90) < 1e-9
    assert abs(f.capacity - 945.0) < 1e-9
    f.take_damage(0.10)
    assert abs(f.integrity - 0.81) < 1e-9


def test_tower_insert_remove():
    t = Tower()
    f1 = make_test_floor("Wood", 10, 100, 200)
    t.insert_at(0, f1)
    assert t.ground is f1 and t.top is f1
    assert t.floor_count() == 1 and t.total_height == 10
    verify_chain(t)

    f2 = make_test_floor("Steel", 8, 100, 200)
    t.insert_at(1, f2)
    assert t.ground is f1 and t.top is f2
    assert f1.above is f2 and f2.below is f1
    verify_chain(t)

    f0 = make_test_floor("Concrete", 12, 100, 200)
    t.insert_at(0, f0)
    assert t.ground is f0 and f0.above is f1 and f1.below is f0
    verify_chain(t)

    f_mid = make_test_floor("Brick", 6, 100, 200)
    t.insert_at(2, f_mid)
    assert [f.material for f in t.traverse()] == [
        "Concrete", "Wood", "Brick", "Steel"
    ]
    assert t.total_height == 36
    verify_chain(t)

    t.remove(f_mid)
    assert f1.above is f2 and f2.below is f1
    assert f_mid.above is None and f_mid.below is None
    verify_chain(t)

    t.remove(f0)
    assert t.ground is f1
    verify_chain(t)

    t.remove(f2)
    assert t.top is f1
    verify_chain(t)

    t.remove(f1)
    assert t.is_empty() and t.total_height == 0
    verify_chain(t)


def test_stability():
    t = Tower()
    f1 = make_test_floor("Steel", 10, weight=250, capacity=600)
    t.insert_at(0, f1)
    assert t.load_above(f1) == 0

    f2 = make_test_floor("Wood", 8, weight=100, capacity=200)
    t.insert_at(1, f2)
    assert t.load_above(f1) == 100
    assert t.load_above(f2) == 0

    f3 = make_test_floor("Brick", 6, weight=200, capacity=300)
    t.insert_at(2, f3)
    assert t.load_above(f1) == 300
    assert t.load_above(f2) == 200

    t2 = Tower()
    weak = make_test_floor("Toothpicks", 5, weight=50, capacity=80)
    heavy = make_test_floor("Concrete", 15, weight=450, capacity=900)
    t2.insert_at(0, weak)
    t2.insert_at(1, heavy)
    min_ratio, weakest = t2.check_stability()
    assert weakest is weak
    assert abs(min_ratio - 80 / 450) < 1e-9


def test_collapse():
    t = Tower()
    f1 = make_test_floor("Steel", 10, 250, 2000)
    f2 = make_test_floor("Toothpicks", 5, 50, 30)
    f3 = make_test_floor("Concrete", 12, 300, 900)
    t.insert_at(0, f1)
    t.insert_at(1, f2)
    t.insert_at(2, f3)
    fallen, lost = t.collapse(f2)
    assert t.floor_count() == 1
    assert t.top is f1 and t.ground is f1
    assert lost == 17
    assert len(fallen) == 2
    verify_chain(t)

    t2 = Tower()
    fa = make_test_floor("Rotten", 3, 80, 10)
    fb = make_test_floor("Wood", 8, 100, 200)
    t2.insert_at(0, fa)
    t2.insert_at(1, fb)
    fallen2, lost2 = t2.collapse(fa)
    assert t2.floor_count() == 0
    assert lost2 == 11

    t3 = Tower()
    fx = make_test_floor("Concrete", 15, 300, 2000)
    fy = make_test_floor("String", 2, 20, 5)
    t3.insert_at(0, fx)
    t3.insert_at(1, fy)
    fallen3, lost3 = t3.collapse(fy)
    assert t3.floor_count() == 1 and t3.top is fx
    assert lost3 == 2


def test_floor_from_roll_into_tower():
    t = Tower()
    for roll in (47382, 80199, 21500):
        t.insert_at(t.floor_count(), Floor(full_decode(roll)))
    assert t.floor_count() == 3
    assert t.total_height == 10 + 18 + 2
    verify_chain(t)
    # Auto-collapse if overloaded
    ratio, weakest = t.check_stability()
    if ratio < 1.0:
        t.collapse(weakest)
    verify_chain(t)


def test_game_turn_loop():
    from game import Game

    g = Game("A", "B")
    assert g.phase == "roll"
    decoded = g.roll()
    assert g.phase == "place"
    assert decoded["material_name"]
    g.place_floor(0)
    assert g.players[0].tower.floor_count() == 1
    # Still A's turn if rolls remain
    assert g.current_player().name == "A"
    assert g.phase == "roll"
    g.roll()
    g.scrap_roll()
    # Keep burning rolls until turn passes
    while g.current_index == 0 and g.phase != "game_over":
        if g.phase == "roll":
            g.roll()
        else:
            g.scrap_roll()
    assert g.current_player().name == "B"
    assert g.phase == "roll"


if __name__ == "__main__":
    test_materials()
    print("materials OK")
    test_roll()
    print("roll OK")
    test_floor()
    print("floor OK")
    test_tower_insert_remove()
    print("tower insert/remove OK")
    test_stability()
    print("stability OK")
    test_collapse()
    print("collapse OK")
    test_floor_from_roll_into_tower()
    print("roll->tower OK")
    test_game_turn_loop()
    print("game loop OK")
    print("\nAll core tests passed!")
