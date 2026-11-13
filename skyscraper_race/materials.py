"""Material table — hash table (dict) lookup by (tier, band).

DSA: Hash table for O(1) material property lookup on every roll.
"""

from constants import TIER_RANGES, UNITS_PER_AMOUNT

# Key: (tier, "low"|"high")  digit 0-4 -> low, 5-9 -> high
MATERIALS = {
    ("junk", "low"): {"name": "toothpicks", "weight": 0.5, "capacity": 0.3},
    ("junk", "high"): {"name": "rotten_wood", "weight": 0.8, "capacity": 0.2},
    ("common", "low"): {"name": "wood", "weight": 1.0, "capacity": 1.0},
    ("common", "high"): {"name": "brick", "weight": 2.0, "capacity": 1.6},
    ("strong", "low"): {"name": "steel", "weight": 2.5, "capacity": 4.5},
    ("strong", "high"): {"name": "concrete", "weight": 3.0, "capacity": 3.0},
}


def tier_for_digit(digit: int) -> str:
    """Map roll digit 1 (1-9) to a tier name."""
    if digit not in TIER_RANGES:
        raise ValueError(f"Invalid tier digit: {digit}")
    return TIER_RANGES[digit]


def _band_for_digit(material_digit: int) -> str:
    if not 0 <= material_digit <= 9:
        raise ValueError(f"material_digit must be 0-9, got {material_digit}")
    return "low" if material_digit <= 4 else "high"


def get_material(tier: str, material_digit: int) -> dict:
    """O(1) hash-table lookup. Returns name, weight, capacity."""
    key = (tier, _band_for_digit(material_digit))
    if key not in MATERIALS:
        raise KeyError(f"Unknown material key: {key}")
    return MATERIALS[key]


def calculate_units(amount: int) -> int:
    """Amount digit (1-10) -> material units."""
    return amount * UNITS_PER_AMOUNT
