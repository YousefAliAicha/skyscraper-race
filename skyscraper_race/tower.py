"""Tower = linked list of Floor nodes.

DSA used here (3 of the 6):
  Linked list — insert / remove a floor at any height
  Recursion   — load_above() walks upward adding weight
  Stack       — collapse() removes a failed floor + everything above
"""

class Tower:
    def __init__(self):
        self.ground = None   # bottom floor
        self.top = None      # top floor
        self.size = 0        # how many floors
        self.height_m = 0.0  # total height in meters

    def is_empty(self):
        return self.ground is None

    def floor_count(self):
        return self.size

    def get_height(self):
        return self.height_m

    def floors_from_ground(self):
        """Normal Python list: [ground, ..., top]."""
        result = []
        floor = self.ground
        while floor is not None:
            result.append(floor)
            floor = floor.above
        return result

    def insert_at(self, position, new_floor):
        """Put new_floor at this index. 0 = ground, size = on top."""
        if position < 0 or position > self.size:
            raise IndexError("bad position")

        if self.is_empty():
            self.ground = new_floor
            self.top = new_floor
            new_floor.above = None
            new_floor.below = None

        elif position == 0:
            new_floor.above = self.ground
            new_floor.below = None
            self.ground.below = new_floor
            self.ground = new_floor

        elif position == self.size:
            new_floor.below = self.top
            new_floor.above = None
            self.top.above = new_floor
            self.top = new_floor

        else:
            floor_below = self.ground
            for _ in range(position - 1):
                floor_below = floor_below.above

            floor_above = floor_below.above
            floor_below.above = new_floor
            new_floor.below = floor_below
            new_floor.above = floor_above
            floor_above.below = new_floor

        self.size += 1
        self.height_m += new_floor.height

    def remove(self, floor):
        """Take one floor out of the linked list."""
        if floor.below is not None:
            floor.below.above = floor.above
        else:
            self.ground = floor.above

        if floor.above is not None:
            floor.above.below = floor.below
        else:
            self.top = floor.below

        self.height_m -= floor.height
        self.size -= 1
        floor.above = None
        floor.below = None

    # --- recursion: weight above a floor ---

    def load_above(self, floor):
        """Total weight of every floor above this one."""
        if floor.above is None:
            return 0.0

        next_floor = floor.above
        return next_floor.get_weight() + self.load_above(next_floor)

    def hold_ratio(self, floor):
        """max_load / load. Under 1.0 means the floor breaks."""
        load = self.load_above(floor)
        if load == 0:
            return 999.0
        return floor.get_max_load() / load

    def find_weakest_floor(self):
        """Check every floor; return the one closest to breaking."""
        floors = self.floors_from_ground()
        if not floors:
            return None

        weakest = floors[0]
        worst_ratio = self.hold_ratio(weakest)

        for floor in floors[1:]:
            ratio = self.hold_ratio(floor)
            if ratio < worst_ratio:
                worst_ratio = ratio
                weakest = floor

        return weakest

    def check_stable(self):
        """Return (ratio, weakest_floor). ratio < 1.0 means collapse."""
        if self.is_empty():
            return 999.0, None

        weakest = self.find_weakest_floor()
        return self.hold_ratio(weakest), weakest

    # --- stack: collapse ---

    def collapse(self, broken_floor=None):
        """Remove the broken floor and every floor above it.

        Returns (list of fallen floors, meters lost).
        """
        if broken_floor is None:
            ratio, broken_floor = self.check_stable()
            if broken_floor is None or ratio >= 1.0:
                return [], 0.0

        if self.is_empty():
            return [], 0.0

        if broken_floor not in self.floors_from_ground():
            return [], 0.0

        # Step 1: push broken floor → top onto a stack
        stack = []
        floor = broken_floor
        while floor is not None:
            stack.append(floor)
            floor = floor.above

        # Step 2: pop from the top first (last in, first out)
        fallen = []
        meters_lost = 0.0
        while stack:
            falling_floor = stack.pop()
            meters_lost += falling_floor.height
            self.remove(falling_floor)
            fallen.append(falling_floor)

        # Step 3: if another floor is now overloaded, collapse again
        ratio, weakest = self.check_stable()
        if weakest is not None and ratio < 1.0:
            more_fallen, more_meters = self.collapse(weakest)
            fallen.extend(more_fallen)
            meters_lost += more_meters

        return fallen, meters_lost
