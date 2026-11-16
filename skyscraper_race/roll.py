"""Roll a 5-digit number and decode it into a floor recipe.

  digit 1 → tier (junk / common / strong)
  digit 2 → amount (0 counts as 10)
  digit 3 → which material inside the tier
  digits 4+5 → height in meters (minimum 2)
"""

import random

from constants import ROLL_MAX, ROLL_MIN
from materials import calculate_units, get_material, tier_for_digit


def generate_roll() -> int:
    return random.randint(ROLL_MIN, ROLL_MAX)


def decode_roll(roll: int) -> dict:
    """Split a 5-digit roll into tier / amount / material digit / height."""
    text = str(roll)
    if len(text) != 5:
        raise ValueError(f"roll must be 5 digits, got {roll}")

    d1, d2, d3, d4, d5 = (int(ch) for ch in text)
    return {
        "roll": roll,
        "tier": tier_for_digit(d1),
        "amount": 10 if d2 == 0 else d2,
        "material_digit": d3,
        "height": max(d4 + d5, 2),
    }


def full_decode(roll: int) -> dict:
    """Decode the roll and attach material stats ready for Floor(...)."""
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
