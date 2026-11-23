"""One floor of the tower (plain data — not a linked-list node)."""

from logic.data.constants import CAPACITY_CONSTANT


class Floor:
    def __init__(self, roll_data):
        self.material_name = roll_data["material_name"]
        self.tier = roll_data["tier"]
        self.height = roll_data["height"]
        self.units = roll_data["units"]
        self.weight_per_unit = roll_data["weight_per_unit"]
        self.strength = roll_data["capacity_mult"]
        self.image = roll_data.get("image", self.material_name)
        self.health = 1.0  # challenges lower this

    def get_weight(self):
        return self.units * self.weight_per_unit

    def get_max_load(self):
        return (
            self.strength
            * self.height
            * CAPACITY_CONSTANT
            * self.health
        )

    def take_damage(self, percent):
        self.health = max(0.0, self.health * (1.0 - percent))

    def label(self):
        return f"{self.material_name}:{self.height}m"
