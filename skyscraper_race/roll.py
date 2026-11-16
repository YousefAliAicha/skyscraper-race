"""Make a 5-digit roll and turn it into a floor recipe.

  digit 1      → tier (junk / common / strong)
  digit 2      → amount (0 means 10)
  digit 3      → which material in that tier
  digits 4 + 5 → height in meters (at least 2)
"""

import random

from constants import ROLL_MAX, ROLL_MIN
from materials import (
    get_material,
    tier_for_digit,
    units_from_amount,
)


def generate_roll():
    return random.randint(ROLL_MIN, ROLL_MAX)


def decode_roll(roll):
    """Split the number into plain fields."""
    text = str(roll)
    if len(text) != 5:
        raise ValueError("roll must be 5 digits")

    digit1 = int(text[0])
    digit2 = int(text[1])
    digit3 = int(text[2])
    digit4 = int(text[3])
    digit5 = int(text[4])

    if digit2 == 0:
        amount = 10
    else:
        amount = digit2

    height = digit4 + digit5
    if height < 2:
        height = 2

    return {
        "roll": roll,
        "tier": tier_for_digit(digit1),
        "amount": amount,
        "material_digit": digit3,
        "height": height,
    }


def full_decode(roll):
    """Decode the roll and attach material stats for Floor(...)."""
    parts = decode_roll(roll)
    material = get_material(parts["tier"], parts["material_digit"])
    units = units_from_amount(parts["amount"])

    return {
        "roll": roll,
        "tier": parts["tier"],
        "material_name": material["name"],
        "weight_per_unit": material["weight"],
        "capacity_mult": material["strength"],
        "units": units,
        "height": parts["height"],
        "image": material["name"],
    }
