"""Tower as a doubly linked list of Floor nodes.

DSA:
  - Linked list: insert a floor at an arbitrary position
  - Recursion: load_above / safety
  - Stack: collapse failed floor and everything above it
"""


class Floor:
    """One floor node in the tower linked list."""

    def __init__(self, material: str, tier: str, units: int, height: float,
                 weight: float, capacity: float, image: str = None):
        self.material = material
        self.tier = tier
        self.units = units
        self.height = height
        self.weight = weight
        self.capacity = capacity
        self.image = image or material
        self.integrity = 1.0  # 1.0 = undamaged; challenges reduce this
        self.above = None  # Floor | None
        self.below = None  # Floor | None

    def __repr__(self) -> str:
        return (
            f"Floor({self.material}, h={self.height}, "
            f"w={self.weight:.1f}, cap={self.capacity:.1f}, "
            f"int={self.integrity:.2f})"
        )


class Tower:
    """Doubly linked list: ground <-> ... <-> top."""

    def __init__(self):
        self.ground = None  # bottom Floor
        self.top = None  # top Floor
        self.size = 0

    def is_empty(self) -> bool:
        return self.ground is None

    def total_height(self) -> float:
        total = 0.0
        node = self.ground
        while node is not None:
            total += node.height
            node = node.above
        return total

    def floors_bottom_up(self) -> list:
        """Return floors from ground to top (for display / tests)."""
        result = []
        node = self.ground
        while node is not None:
            result.append(node)
            node = node.above
        return result

    def insert_at(self, position: int, floor: Floor) -> None:
        """Insert floor so it becomes the node at `position` (0 = ground).

        TODO: implement linked-list relinking (head/middle/top cases).
        """
        raise NotImplementedError("Tower.insert_at — Step 4")

    def load_above(self, floor: Floor) -> float:
        """Recursive total weight resting on this floor (not including itself).

        TODO: implement recursion (base case: top floor -> 0).
        """
        raise NotImplementedError("Tower.load_above — Step 5")

    def safety_ratio(self, floor: Floor) -> float:
        """capacity / load_above; infinity if load is 0."""
        raise NotImplementedError("Tower.safety_ratio — Step 5")

    def find_weakest_floor(self):
        """Linear scan for the floor with the lowest safety ratio."""
        raise NotImplementedError("Tower.find_weakest_floor — Step 5")

    def collapse(self) -> list:
        """Stack-based removal of the weakest failing floor and all above it.

        Returns the list of removed floors (top-first).
        TODO: implement — Step 6.
        """
        raise NotImplementedError("Tower.collapse — Step 6")
