"""Tower as a doubly linked list of Floor nodes.

DSA:
  - Linked list: insert / remove at arbitrary position
  - Recursion: load_above
  - Sequential search: find_weakest_floor
  - Stack: collapse failed floor and everything above it
"""


class Floor:
    """One floor node in the tower linked list."""

    def __init__(self, roll_data: dict):
        self.material_name = roll_data["material_name"]
        self.tier = roll_data["tier"]
        self.height = roll_data["height"]
        self.units = roll_data["units"]
        self.weight_per_unit = roll_data["weight_per_unit"]
        self.capacity_mult = roll_data["capacity_mult"]
        self.image = roll_data.get("image", self.material_name)
        self.integrity = 1.0
        self.above = None  # Floor | None
        self.below = None  # Floor | None

    @property
    def material(self) -> str:
        """Alias used by display / older guide snippets."""
        return self.material_name

    @property
    def total_weight(self) -> float:
        return self.units * self.weight_per_unit

    @property
    def weight(self) -> float:
        """Alias for load_above recursion (guide uses .weight)."""
        return self.total_weight

    @property
    def capacity(self) -> float:
        # capacity_mult * units * integrity (Step 3 guide tests)
        return self.capacity_mult * self.units * self.integrity

    def take_damage(self, percent: float) -> None:
        """Multiplicative integrity damage: integrity *= (1 - percent)."""
        self.integrity = max(0.0, self.integrity * (1.0 - percent))

    def is_destroyed(self) -> bool:
        return self.integrity < 0.01

    def __repr__(self) -> str:
        return (
            f"Floor({self.material_name}, {self.height}m, "
            f"integrity={self.integrity:.2f}, "
            f"weight={self.total_weight:.1f}, capacity={self.capacity:.1f})"
        )

    __str__ = __repr__


def make_test_floor(material_name: str, height: float, weight: float, capacity: float) -> Floor:
    """Build a Floor with fixed weight/capacity for unit tests (bypasses rolls)."""
    # Derive units/weight_per_unit so total_weight == weight and capacity matches
    # at integrity 1.0 with capacity_mult chosen accordingly.
    units = 100
    weight_per_unit = weight / units
    capacity_mult = capacity / units  # capacity property = mult * units * integrity
    data = {
        "material_name": material_name,
        "tier": "test",
        "height": height,
        "units": units,
        "weight_per_unit": weight_per_unit,
        "capacity_mult": capacity_mult,
        "image": material_name,
    }
    return Floor(data)


class Tower:
    """Doubly linked list: ground <-> ... <-> top."""

    def __init__(self):
        self.ground = None
        self.top = None
        self.size = 0
        self._total_height = 0.0

    def is_empty(self) -> bool:
        return self.ground is None

    def floor_count(self) -> int:
        return self.size

    @property
    def total_height(self) -> float:
        return self._total_height

    def total_height_sum(self) -> float:
        """Walk and sum heights (source of truth check)."""
        total = 0.0
        node = self.ground
        while node is not None:
            total += node.height
            node = node.above
        return total

    def traverse(self):
        """Yield each floor from bottom to top."""
        current = self.ground
        while current is not None:
            yield current
            current = current.above

    def floors_bottom_up(self) -> list:
        return list(self.traverse())

    def get_floor_at(self, index: int):
        if index < 0 or index >= self.size:
            return None
        current = self.ground
        for _ in range(index):
            current = current.above
        return current

    def insert_at(self, position: int, floor: Floor) -> None:
        """Insert floor at position (0 = ground, size = new top)."""
        if position < 0 or position > self.size:
            raise IndexError(
                f"insert_at position {position} out of range [0, {self.size}]"
            )

        if self.is_empty():
            self.ground = floor
            self.top = floor
            floor.above = None
            floor.below = None
        elif position == 0:
            floor.above = self.ground
            floor.below = None
            self.ground.below = floor
            self.ground = floor
        elif position == self.size:
            floor.below = self.top
            floor.above = None
            self.top.above = floor
            self.top = floor
        else:
            # Insert above the floor currently at position - 1
            current = self.ground
            for _ in range(position - 1):
                current = current.above
            above = current.above
            current.above = floor
            floor.below = current
            floor.above = above
            above.below = floor

        self.size += 1
        self._total_height += floor.height

    def remove(self, floor: Floor) -> None:
        """Remove a floor and relink neighbors. Detach its pointers."""
        if floor.below is not None:
            floor.below.above = floor.above
        else:
            # Removing ground
            self.ground = floor.above

        if floor.above is not None:
            floor.above.below = floor.below
        else:
            # Removing top
            self.top = floor.below

        self._total_height -= floor.height
        self.size -= 1
        floor.above = None
        floor.below = None

    # --- Stability (recursion + linear scan) ---

    def load_above(self, floor: Floor) -> float:
        """Recursive total weight resting on this floor (excluding itself)."""
        if floor.above is None:
            return 0.0
        return floor.above.weight + self.load_above(floor.above)

    def safety_ratio(self, floor: Floor) -> float:
        load = self.load_above(floor)
        if load == 0:
            return float("inf")
        return floor.capacity / load

    def find_weakest_floor(self):
        """Linear scan for the floor with the lowest safety ratio."""
        if self.is_empty():
            return None
        floors = self.floors_bottom_up()
        weakest = floors[0]
        worst = self.safety_ratio(weakest)
        for floor in floors[1:]:
            ratio = self.safety_ratio(floor)
            if ratio < worst:
                worst = ratio
                weakest = floor
        return weakest

    def check_stability(self):
        """Return (min_ratio, weakest_floor). Empty tower -> (inf, None)."""
        if self.is_empty():
            return float("inf"), None
        weakest = self.find_weakest_floor()
        return self.safety_ratio(weakest), weakest

    # --- Collapse (stack) ---

    def collapse(self, failed_floor: Floor = None) -> tuple:
        """Remove failed floor and everything above it using a stack (LIFO).

        If failed_floor is None, finds the weakest failing floor first.
        Cascades if another floor fails after removal.
        Returns (fallen_floors, height_lost).
        """
        if failed_floor is None:
            ratio, failed_floor = self.check_stability()
            if failed_floor is None or ratio >= 1.0:
                return [], 0.0

        # Guard: floor already detached / not in this tower
        if self.is_empty() or failed_floor not in self.floors_bottom_up():
            return [], 0.0

        # Push failed floor -> top onto stack
        to_remove = []
        current = failed_floor
        while current is not None:
            to_remove.append(current)
            current = current.above

        height_lost = 0.0
        fallen = []
        while to_remove:
            floor = to_remove.pop()  # LIFO: top first
            height_lost += floor.height
            self.remove(floor)
            fallen.append(floor)

        # Cascade: another floor may now be overloaded
        min_ratio, weakest = self.check_stability()
        if weakest is not None and min_ratio < 1.0:
            more_fallen, more_height = self.collapse(weakest)
            fallen.extend(more_fallen)
            height_lost += more_height

        return fallen, height_lost

    def __str__(self) -> str:
        floors = self.floors_bottom_up()
        if not floors:
            return "Tower(empty)"
        lines = []
        for i, f in enumerate(reversed(floors), start=1):
            idx = len(floors) - i + 1
            lines.append(
                f"  [{idx}] {f.material_name:12} | {f.height:2}m | "
                f"integrity: {f.integrity:.0%}"
            )
        lines.append(f"  Total: {self.total_height}m | Floors: {self.size}")
        return "\n".join(lines)
