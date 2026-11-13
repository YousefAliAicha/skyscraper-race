"""5-digit roll → tier / amount / material / height."""

import random
from constants import ROLL_MAX, ROLL_MIN
from materials import calculate_units, get_material, tier_for_digit


def generate_roll() -> int:
    return random.randint(ROLL_MIN, ROLL_MAX)


def decode_roll(roll: int) -> dict:
    s = str(roll)
    if len(s) != 5:
        raise ValueError(f"need 5 digits, got {roll}")
    d1, d2, d3, d4, d5 = (int(c) for c in s)
    return {
        "roll": roll,
        "tier": tier_for_digit(d1),
        "amount": 10 if d2 == 0 else d2,
        "material_digit": d3,
        "height": max(d4 + d5, 2),
    }


def full_decode(roll: int) -> dict:
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
