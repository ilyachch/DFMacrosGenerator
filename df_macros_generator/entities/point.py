class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_in_moves(self, other: 'Point') -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
