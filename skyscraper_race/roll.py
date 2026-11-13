"""Roll generation and decoding.

A roll is a 5-digit int (10000–99999). Digits map to:
  1: tier, 2: material index in tier (0 -> 10), 3-4: amount, 5: height factor
Exact decode formulas are filled in when we implement Step 1 of the build guide.
"""

import random

from constants import ROLL_MAX, ROLL_MIN
from materials import MATERIALS_BY_TIER, get_material, tier_for_digit


def generate_roll() -> int:
    """Return a random 5-digit roll."""
    return random.randint(ROLL_MIN, ROLL_MAX)


def digits_of(number: int) -> tuple:
    """Split a 5-digit number into five ints (d1..d5)."""
    s = f"{number:05d}"
    if len(s) != 5:
        raise ValueError(f"Roll must be 5 digits, got {number}")
    return tuple(int(ch) for ch in s)


def decode_roll(number: int) -> dict:
    """Decode a roll into material, tier, amount, height.

    Returns dict keys: roll, tier, material, amount, height, weight, capacity

    TODO: lock exact digit formulas from the build guide and team agreement.
    Current scaffold uses a simple, readable mapping so the rest of the
    project can wire up against a stable interface.
    """
    d1, d2, d3, d4, d5 = digits_of(number)
    # Digit 1 never starts a 5-digit number as 0; still guard tier lookup.
    tier_digit = d1 if d1 != 0 else 1
    tier = tier_for_digit(tier_digit)

    options = MATERIALS_BY_TIER[tier]
    # Digit 2: 0 means 10 → last option; otherwise 1-based index into tier list.
    idx = (10 if d2 == 0 else d2) - 1
    idx = idx % len(options)
    material_name = options[idx]
    props = get_material(material_name)

    amount = d3 * 10 + d4
    if amount == 0:
        amount = 10
    # Height in meters — scaffold formula (tune later)
    height = max(1, d5 if d5 != 0 else 10)

    weight = amount * props["weight_per_unit"]
    capacity = amount * props["capacity_mult"] * 100  # scale placeholder

    return {
        "roll": number,
        "tier": tier,
        "material": material_name,
        "amount": amount,
        "height": height,
        "weight": weight,
        "capacity": capacity,
        "image": props["image"],
    }
