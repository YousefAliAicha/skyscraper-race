"""Material table — hash table (dict) lookup by name / tier.

DSA: Hash table for O(1) material property lookup on every roll.
"""

from constants import TIER_RANGES

# name -> {tier, weight_per_unit, capacity_mult, image}
MATERIALS = {
    "toothpicks": {
        "tier": "junk",
        "weight_per_unit": 0.5,
        "capacity_mult": 0.3,
        "image": "toothpicks",
    },
    "rotten_wood": {
        "tier": "junk",
        "weight_per_unit": 0.8,
        "capacity_mult": 0.2,
        "image": "rotten_wood",
    },
    "wood": {
        "tier": "common",
        "weight_per_unit": 1.0,
        "capacity_mult": 1.0,
        "image": "wood",
    },
    "brick": {
        "tier": "common",
        "weight_per_unit": 2.0,
        "capacity_mult": 1.6,
        "image": "brick",
    },
    "steel": {
        "tier": "strong",
        "weight_per_unit": 2.5,
        "capacity_mult": 4.5,
        "image": "steel",
    },
    "concrete": {
        "tier": "strong",
        "weight_per_unit": 3.0,
        "capacity_mult": 3.0,
        "image": "concrete",
    },
}

# tier -> ordered list of material names in that tier
MATERIALS_BY_TIER = {
    "junk": ["toothpicks", "rotten_wood"],
    "common": ["wood", "brick"],
    "strong": ["steel", "concrete"],
}


def tier_for_digit(digit: int) -> str:
    """Map roll digit 1 to a tier name. Digit 0 should not appear as digit 1."""
    if digit not in TIER_RANGES:
        raise ValueError(f"Invalid tier digit: {digit}")
    return TIER_RANGES[digit]


def get_material(name: str) -> dict:
    """O(1) hash-table lookup for material properties."""
    if name not in MATERIALS:
        raise KeyError(f"Unknown material: {name}")
    return MATERIALS[name]


def materials_in_tier(tier: str) -> list:
    if tier not in MATERIALS_BY_TIER:
        raise KeyError(f"Unknown tier: {tier}")
    return list(MATERIALS_BY_TIER[tier])
