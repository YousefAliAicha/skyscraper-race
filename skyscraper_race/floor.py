"""One floor = one node in the linked list.

Each floor knows:
  - its material and size
  - the floor above it
  - the floor below it
"""

from constants import CAPACITY_CONSTANT


class Floor:
    def __init__(self, roll_data):
        self.material_name = roll_data["material_name"]
        self.tier = roll_data["tier"]
        self.height = roll_data["height"]
        self.units = roll_data["units"]
        self.weight_per_unit = roll_data["weight_per_unit"]
        self.strength = roll_data["capacity_mult"]
        self.image = roll_data.get("image", self.material_name)

        # health starts at 1.0; challenges lower it
        self.health = 1.0

        # linked-list pointers
        self.above = None
        self.below = None

    def get_weight(self):
        """How heavy this floor is."""
        return self.units * self.weight_per_unit

    def get_max_load(self):
        """How much weight this floor can hold right now."""
        return (
            self.strength
            * self.height
            * CAPACITY_CONSTANT
            * self.health
        )

    def take_damage(self, percent):
        """Lower health. Example: 10% damage → health becomes 0.9."""
        self.health = max(0.0, self.health * (1.0 - percent))
