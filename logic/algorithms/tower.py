"""DATA STRUCTURE #2 — Python list (array) of floors.
  index 0 = ground, last index = top

ALGORITHMS:
  #1 Recursion         — load_above(index)
  #3 Sequential search — find_weakest_floor()
"""

from logic.data.floor import Floor  # noqa: F401


class Tower:
    def __init__(self):
        # list of Floor objects; [0] is ground
        self.floors = []

    def is_empty(self):
        return len(self.floors) == 0

    def floor_count(self):
        return len(self.floors)

    def get_height(self):
        total = 0.0
        for floor in self.floors:
            total += floor.height
        return total

    def floors_from_ground(self):
        """Copy of the list ground → top (for UI / tests)."""
        return list(self.floors)

    def insert_at(self, position, new_floor):
        """Place a floor at this index (0 = ground, len = on top)."""
        if position < 0 or position > len(self.floors):
            raise IndexError("bad position")
        self.floors.insert(position, new_floor)

    def remove_at(self, index):
        """Delete the floor at this index."""
        return self.floors.pop(index)

    # --- ALGORITHM #1: recursion ---

    def load_above(self, index):
        """Total weight of every floor above this index.

        load_above(i) = weight(i+1) + load_above(i+1)
        base case: top floor → 0
        """
        if index >= len(self.floors) - 1:
            return 0.0

        next_index = index + 1
        next_floor = self.floors[next_index]
        return next_floor.get_weight() + self.load_above(next_index)

    def hold_ratio(self, index):
        """max_load / load. Under 1.0 means this floor breaks."""
        load = self.load_above(index)
        if load == 0:
            return 999.0
        return self.floors[index].get_max_load() / load

    # --- ALGORITHM #3: sequential search ---

    def find_weakest_floor_index(self):
        """Scan every floor; return index with the worst hold_ratio.

        Sequential search: check items one by one, remember the worst.
        """
        if self.is_empty():
            return None

        weakest_index = 0
        worst_ratio = self.hold_ratio(0)

        index = 1
        while index < len(self.floors):
            ratio = self.hold_ratio(index)
            if ratio < worst_ratio:
                worst_ratio = ratio
                weakest_index = index
            index += 1

        return weakest_index

    def check_stable(self):
        """Return (ratio, weakest_index). ratio < 1.0 → collapse."""
        if self.is_empty():
            return 999.0, None

        weakest_index = self.find_weakest_floor_index()
        return self.hold_ratio(weakest_index), weakest_index

    def collapse(self, broken_index=None):
        """Remove the broken floor and every floor above it.

        List slice: keep floors[0:broken_index], drop the rest.
        """
        if broken_index is None:
            ratio, broken_index = self.check_stable()
            if broken_index is None or ratio >= 1.0:
                return [], 0.0

        if broken_index < 0 or broken_index >= len(self.floors):
            return [], 0.0

        fallen = self.floors[broken_index:]
        self.floors = self.floors[:broken_index]

        meters_lost = 0.0
        for floor in fallen:
            meters_lost += floor.height

        # if another floor is now overloaded, collapse again
        ratio, weakest_index = self.check_stable()
        if weakest_index is not None and ratio < 1.0:
            more_fallen, more_meters = self.collapse(weakest_index)
            fallen.extend(more_fallen)
            meters_lost += more_meters

        return fallen, meters_lost
