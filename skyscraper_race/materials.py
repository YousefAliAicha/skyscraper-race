"""Material table — a hash table (Python dict).

Why a dict?
  Looking up material stats by (tier, band) is O(1) on average.
  Adding a new material is one new entry — no if/elif chain to edit.
"""

from constants import TIER_RANGES, UNITS_PER_AMOUNT

# Key = (tier, band). Band comes from digit 3: 0–4 → "low", 5–9 → "high".
MATERIALS = {
    ("junk", "low"):   {"name": "toothpicks",  "weight": 0.5, "capacity": 0.3},
    ("junk", "high"):  {"name": "rotten_wood", "weight": 0.8, "capacity": 0.2},
    ("common", "low"): {"name": "wood",        "weight": 1.0, "capacity": 1.0},
    ("common", "high"):{"name": "brick",       "weight": 2.0, "capacity": 1.6},
    ("strong", "low"): {"name": "steel",       "weight": 2.5, "capacity": 4.5},
    ("strong", "high"):{"name": "concrete",    "weight": 3.0, "capacity": 3.0},
}


def tier_for_digit(digit: int) -> str:
    """Map digit 1 of the roll to junk / common / strong."""
    return TIER_RANGES[digit]


def get_material(tier: str, material_digit: int) -> dict:
    """Return {name, weight, capacity} for this tier + digit."""
    band = "low" if material_digit <= 4 else "high"
    return MATERIALS[(tier, band)]


def calculate_units(amount: int) -> int:
    """Convert amount digit (1–10) into material units."""
    return amount * UNITS_PER_AMOUNT
