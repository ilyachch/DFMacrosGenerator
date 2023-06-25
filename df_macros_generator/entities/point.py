class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def distance_in_moves(self, other: "Point") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            raise ValueError(f"Cannot compare Point with {type(other)}")
        return self.x == other.x and self.y == other.y
