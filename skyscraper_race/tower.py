"""Tower as a doubly linked list of Floor nodes.

DSA used here:
  Linked list  — insert / remove a floor at any height
  Recursion    — load_above() walks upward adding weight
  Linear scan  — find_weakest_floor()
  Stack        — collapse() removes failed floor + everything above (LIFO)
"""

from constants import CAPACITY_CONSTANT


class Floor:
    """One floor = one linked-list node (pointers: above / below)."""

    def __init__(self, roll_data: dict):
        self.material_name = roll_data["material_name"]
        self.tier = roll_data["tier"]
        self.height = roll_data["height"]
        self.units = roll_data["units"]
        self.weight_per_unit = roll_data["weight_per_unit"]
        self.capacity_mult = roll_data["capacity_mult"]
        self.image = roll_data.get("image", self.material_name)
        self.integrity = 1.0  # starts full; challenges multiply this down
        self.above = None
        self.below = None

    @property
    def material(self):
        return self.material_name

    @property
    def weight(self):
        return self.units * self.weight_per_unit

    # alias used by older tests / guide wording
    total_weight = weight

    @property
    def capacity(self):
        """How much weight this floor can hold right now."""
        return self.capacity_mult * self.height * CAPACITY_CONSTANT * self.integrity

    def take_damage(self, percent: float):
        """Multiplicative damage: 10% twice → 0.9 × 0.9 = 0.81."""
        self.integrity = max(0.0, self.integrity * (1.0 - percent))

    def __repr__(self):
        return (
            f"Floor({self.material_name}, {self.height}m, "
            f"w={self.weight:.0f}, cap={self.capacity:.0f})"
        )


class Tower:
    """Doubly linked list: ground ↔ … ↔ top."""

    def __init__(self):
        self.ground = None
        self.top = None
        self.size = 0
        self._total_height = 0.0

    def is_empty(self):
        return self.ground is None

    def floor_count(self):
        return self.size

    @property
    def total_height(self):
        return self._total_height

    def traverse(self):
        """Yield floors from ground to top."""
        cur = self.ground
        while cur:
            yield cur
            cur = cur.above

    def floors_bottom_up(self):
        return list(self.traverse())

    def insert_at(self, position: int, floor: Floor):
        """Insert so the new floor becomes index `position` (0 = ground)."""
        if position < 0 or position > self.size:
            raise IndexError(f"position {position} not in [0, {self.size}]")

        if self.is_empty():
            # Only floor
            self.ground = self.top = floor
            floor.above = floor.below = None
        elif position == 0:
            # New ground
            floor.above, floor.below = self.ground, None
            self.ground.below = floor
            self.ground = floor
        elif position == self.size:
            # New top
            floor.below, floor.above = self.top, None
            self.top.above = floor
            self.top = floor
        else:
            # Middle: sit above the floor currently at position-1
            cur = self.ground
            for _ in range(position - 1):
                cur = cur.above
            above = cur.above
            cur.above = floor
            floor.below = cur
            floor.above = above
            above.below = floor

        self.size += 1
        self._total_height += floor.height

    def remove(self, floor: Floor):
        """Unlink one floor and fix neighbor pointers."""
        if floor.below:
            floor.below.above = floor.above
        else:
            self.ground = floor.above

        if floor.above:
            floor.above.below = floor.below
        else:
            self.top = floor.below

        self._total_height -= floor.height
        self.size -= 1
        floor.above = floor.below = None

    # --- Stability (recursion + scan) ---

    def load_above(self, floor: Floor) -> float:
        """Total weight resting on this floor (recursive)."""
        if floor.above is None:          # base case: top floor
            return 0.0
        return floor.above.weight + self.load_above(floor.above)

    def safety_ratio(self, floor: Floor) -> float:
        """capacity / load. Below 1.0 means the floor fails."""
        load = self.load_above(floor)
        return float("inf") if load == 0 else floor.capacity / load

    def find_weakest_floor(self):
        """Linear scan for the lowest safety ratio."""
        floors = self.floors_bottom_up()
        if not floors:
            return None
        weakest = floors[0]
        worst = self.safety_ratio(weakest)
        for f in floors[1:]:
            r = self.safety_ratio(f)
            if r < worst:
                worst, weakest = r, f
        return weakest

    def check_stability(self):
        if self.is_empty():
            return float("inf"), None
        weakest = self.find_weakest_floor()
        return self.safety_ratio(weakest), weakest

    # --- Collapse (stack) ---

    def collapse(self, failed_floor: Floor = None):
        """Remove the failed floor and everything above it (stack / LIFO).

        Returns (list_of_fallen_floors, height_lost).
        """
        if failed_floor is None:
            ratio, failed_floor = self.check_stability()
            if failed_floor is None or ratio >= 1.0:
                return [], 0.0

        if self.is_empty() or failed_floor not in self.floors_bottom_up():
            return [], 0.0

        # 1) Push failed → top onto a stack
        stack = []
        cur = failed_floor
        while cur:
            stack.append(cur)
            cur = cur.above

        # 2) Pop top-first so we always remove the current top of the tower
        fallen, lost = [], 0.0
        while stack:
            f = stack.pop()
            lost += f.height
            self.remove(f)
            fallen.append(f)

        # 3) Rare cascade: another floor may now be overloaded
        ratio, weakest = self.check_stability()
        if weakest is not None and ratio < 1.0:
            more, extra = self.collapse(weakest)
            fallen.extend(more)
            lost += extra
        return fallen, lost
