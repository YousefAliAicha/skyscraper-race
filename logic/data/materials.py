"""DATA STRUCTURE #1 — Hash table (dict).

MATERIALS[(tier, group)] → material stats.
Lookup is O(1) average — best for “given a roll, get stats.”
"""

from logic.data.constants import TIER_RANGES, UNITS_PER_AMOUNT

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
    return TIER_RANGES[digit]


def get_material(tier, material_digit):
    if material_digit <= 4:
        group = "a"
    else:
        group = "b"
    return MATERIALS[(tier, group)]


def units_from_amount(amount):
    return amount * UNITS_PER_AMOUNT
