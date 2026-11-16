"""Material stats live in a dict (hash table / lookup table).

DSA #1 — Hash table:
  MATERIALS[(tier, group)] → {name, weight, strength}
"""

from constants import TIER_RANGES, UNITS_PER_AMOUNT

# digit 3 of the roll:
#   0-4 → group "a" (first material in the tier)
#   5-9 → group "b" (second material in the tier)
MATERIALS = {
    ("junk", "a"): {
        "name": "toothpicks",
        "weight": 0.5,
        "strength": 0.3,
    },
    ("junk", "b"): {
        "name": "rotten_wood",
        "weight": 0.8,
        "strength": 0.2,
    },
    ("common", "a"): {
        "name": "wood",
        "weight": 1.0,
        "strength": 1.0,
    },
    ("common", "b"): {
        "name": "brick",
        "weight": 2.0,
        "strength": 1.6,
    },
    ("strong", "a"): {
        "name": "steel",
        "weight": 2.5,
        "strength": 4.5,
    },
    ("strong", "b"): {
        "name": "concrete",
        "weight": 3.0,
        "strength": 3.0,
    },
}


def tier_for_digit(digit):
    """Digit 1 of the roll → junk / common / strong."""
    return TIER_RANGES[digit]


def get_material(tier, material_digit):
    """Look up one material from the dict."""
    if material_digit <= 4:
        group = "a"
    else:
        group = "b"
    return MATERIALS[(tier, group)]


def units_from_amount(amount):
    """Digit 2 (1-10) → how many material units the floor uses."""
    return amount * UNITS_PER_AMOUNT
