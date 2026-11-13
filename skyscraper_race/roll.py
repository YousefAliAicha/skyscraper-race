"""Roll generation and decoding.

A roll is a 5-digit int (10000–99999):
  d1: tier, d2: amount (0 -> 10), d3: material digit, d4+d5: height (min 2)
"""

import random

from constants import ROLL_MAX, ROLL_MIN
from materials import calculate_units, get_material, tier_for_digit


def generate_roll() -> int:
    """Return a random 5-digit roll."""
    return random.randint(ROLL_MIN, ROLL_MAX)


def digits_of(number: int) -> tuple:
    """Split a 5-digit number into five ints (d1..d5)."""
    s = str(number)
    if len(s) != 5:
        raise ValueError(f"Roll must be 5 digits, got {number}")
    return tuple(int(ch) for ch in s)


def decode_roll(roll: int) -> dict:
    """Decode a roll into tier / amount / material_digit / height."""
    d1, d2, d3, d4, d5 = digits_of(roll)
    amount = 10 if d2 == 0 else d2
    height = max(d4 + d5, 2)
    return {
        "roll": roll,
        "tier": tier_for_digit(d1),
        "amount": amount,
        "material_digit": d3,
        "height": height,
    }


def full_decode(roll: int) -> dict:
    """Decode a roll and look up material properties for Floor creation."""
    base = decode_roll(roll)
    mat = get_material(base["tier"], base["material_digit"])
    units = calculate_units(base["amount"])
    return {
        "roll": roll,
        "tier": base["tier"],
        "material_name": mat["name"],
        "weight_per_unit": mat["weight"],
        "capacity_mult": mat["capacity"],
        "units": units,
        "height": base["height"],
        "total_weight": units * mat["weight"],
        "image": mat["name"],
    }


if __name__ == "__main__":
    result = decode_roll(47382)
    assert result["tier"] == "common"
    assert result["amount"] == 7
    assert result["material_digit"] == 3
    assert result["height"] == 10
    print("Test 1 passed: 47382")

    result = decode_roll(21500)
    assert result["tier"] == "junk"
    assert result["amount"] == 1
    assert result["material_digit"] == 5
    assert result["height"] == 2
    print("Test 2 passed: 21500")

    result = decode_roll(80199)
    assert result["tier"] == "strong"
    assert result["amount"] == 10
    assert result["height"] == 18
    print("Test 3 passed: 80199")

    result = decode_roll(10000)
    assert result["tier"] == "junk"
    assert result["amount"] == 10
    assert result["height"] == 2
    print("Test 4 passed: 10000")

    result = decode_roll(99999)
    assert result["tier"] == "strong"
    assert result["amount"] == 9
    assert result["height"] == 18
    print("Test 5 passed: 99999")

    for _ in range(1000):
        r = generate_roll()
        d = decode_roll(r)
        assert ROLL_MIN <= r <= ROLL_MAX
        assert d["tier"] in ("junk", "common", "strong")
        assert 1 <= d["amount"] <= 10
        assert 2 <= d["height"] <= 18
    print("Test 6 passed: 1000 random rolls")

    full = full_decode(47382)
    assert full["material_name"] == "wood"
    assert full["units"] == 1050
    assert full["total_weight"] == 1050.0
    print("Test 7 passed: full_decode(47382)")

    print("\nAll roll decoder tests passed!")
