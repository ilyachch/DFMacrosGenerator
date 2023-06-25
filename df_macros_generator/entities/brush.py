import enum
from typing import Optional

from entities.matrix import Matrix, Pixel
from entities.point import Point


class Action(enum.Enum):
    SELECT = enum.auto()
    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()
    MOVE_UP_FAST = enum.auto()
    MOVE_DOWN_FAST = enum.auto()
    MOVE_LEFT_FAST = enum.auto()
    MOVE_RIGHT_FAST = enum.auto()


class DirectionX(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()


class DirectionY(enum.Enum):
    TOP = enum.auto()
    BOTTOM = enum.auto()


class Brush:
    def __init__(self, matrix: Matrix):
        self.matrix = matrix
        self.x: int = self.matrix.entrance_point.x
        self.y: int = self.matrix.entrance_point.y
        self.painting = False
        self.painted: set[Point] = set()
        self.painting_start: tuple[int, int] = (self.x, self.y)
        self.commands: list[Action] = []

    def __repr__(self) -> str:
        return f"Brush({self.x}, {self.y})"

    @property
    def current_position(self) -> Point:
        return Point(self.x, self.y)

    def move_up(self) -> None:
        self.y -= 1
        self.commands.append(Action.MOVE_UP)

    def move_down(self) -> None:
        self.y += 1
        self.commands.append(Action.MOVE_DOWN)

    def move_left(self) -> None:
        self.x -= 1
        self.commands.append(Action.MOVE_LEFT)

    def move_right(self) -> None:
        self.x += 1
        self.commands.append(Action.MOVE_RIGHT)

    def move_up_fast(self) -> None:
        self.y -= 10
        self.commands.append(Action.MOVE_UP_FAST)

    def move_down_fast(self) -> None:
        self.y += 10
        self.commands.append(Action.MOVE_DOWN_FAST)

    def move_left_fast(self) -> None:
        self.x -= 10
        self.commands.append(Action.MOVE_LEFT_FAST)

    def move_right_fast(self) -> None:
        self.x += 10
        self.commands.append(Action.MOVE_RIGHT_FAST)

    def start_painting(self) -> None:
        if self.painting:
            raise Exception("Already painting")
        self.painting = True
        self.painting_start = (self.x, self.y)
        self.commands.append(Action.SELECT)

    def stop_painting(self) -> None:
        if not self.painting:
            raise Exception("Not painting")
        self.painting = False
        current_position = (self.x, self.y)
        painted_area_coordinates = []
        x_distance = abs(self.painting_start[0] - current_position[0]) + 1
        y_distance = abs(self.painting_start[1] - current_position[1]) + 1
        for x in range(x_distance):
            for y in range(y_distance):
                x_direction = 1 if self.painting_start[0] < current_position[0] else -1
                y_direction = 1 if self.painting_start[1] < current_position[1] else -1
                painted_area_coordinates.append(
                    Point(
                        self.painting_start[0] + x * x_direction,
                        self.painting_start[1] + y * y_direction,
                    )
                )
        self.painted.update(painted_area_coordinates)
        self.commands.append(Action.SELECT)

    def move_to(self, target_point: Point) -> None:
        while self.current_position != target_point:
            if self.current_position.x < target_point.x:
                if target_point.x - self.current_position.x >= 10:
                    self.move_right_fast()
                else:
                    self.move_right()
            elif self.current_position.x > target_point.x:
                if self.current_position.x - target_point.x >= 10:
                    self.move_left_fast()
                else:
                    self.move_left()
            elif self.current_position.y < target_point.y:
                if target_point.y - self.current_position.y >= 10:
                    self.move_down_fast()
                else:
                    self.move_down()
            elif self.current_position.y > target_point.y:
                if self.current_position.y - target_point.y >= 10:
                    self.move_up_fast()
                else:
                    self.move_up()

    def tick(self) -> bool:
        if self.current_position in self.painted:
            closest_point = self.find_closest_not_painted_valuable_point()
        else:
            closest_point = self.current_position

        self.move_to(closest_point)
        self.start_painting()
        opposite_corner, _ = self.find_biggest_paintable_rectangle(self.current_position)
        self.move_to(opposite_corner)
        self.stop_painting()
        closest_point = self.find_closest_not_painted_valuable_point()
        return bool(closest_point)

    def find_closest_not_painted_valuable_point(self) -> Optional[Point]:
        """
        finds the closest point that is valuable and not painted
        """
        closest_point = None
        closest_distance = None
        for y in range(len(self.matrix.data)):
            for x in range(len(self.matrix.data[y])):
                if self.matrix.data[y][x] != Pixel.IGNORE and Point(x, y) not in self.painted:
                    distance = self.current_position.distance_in_moves(Point(x, y))
                    if closest_distance is None or distance < closest_distance:
                        closest_distance = distance
                        closest_point = Point(x, y)
        return closest_point

    def find_biggest_paintable_rectangle(self, start_point: Point) -> tuple[Point, int]:
        """
        finds the biggest paintable rectangle
        """
        found_rectangles = [
            self.find_biggest_rectangle_to_paint_for_direction(
                start_point, direction_x, direction_y
            )
            for direction_x in DirectionX
            for direction_y in DirectionY
        ]

        rectangles_by_size = {
            len(
                set(self.matrix.get_points_in_selection(self.current_position, rec)) - self.painted
            ): rec
            for rec in found_rectangles
        }
        maximum_size = max(rectangles_by_size.keys())

        return rectangles_by_size[maximum_size], maximum_size

    def find_biggest_rectangle_to_paint_for_direction(
        self, start_point: Point, direction_x: DirectionX, direction_y: DirectionY
    ) -> Point:
        x, y = start_point.x, start_point.y
        if direction_x == DirectionX.LEFT:

            def validation_x() -> bool:
                return (
                    x > 0
                    and self.matrix.data[y][x - 1] != Pixel.IGNORE
                    and bool(
                        set(
                            self.matrix.get_points_in_selection(
                                self.current_position, Point(x - 1, y)
                            )
                        )
                        - self.painted
                    )
                    and Pixel.IGNORE
                    not in self.matrix.get_values_in_selection(
                        self.current_position, Point(x - 1, y)
                    )
                )

        else:

            def validation_x() -> bool:
                return (
                    x < len(self.matrix.data[0]) - 1
                    and self.matrix.data[y][x + 1] != Pixel.IGNORE
                    and bool(
                        set(
                            self.matrix.get_points_in_selection(
                                self.current_position, Point(x + 1, y)
                            )
                        )
                        - self.painted
                    )
                    and Pixel.IGNORE
                    not in self.matrix.get_values_in_selection(
                        self.current_position, Point(x + 1, y)
                    )
                )

        if direction_y == DirectionY.TOP:

            def validation_y() -> bool:
                return (
                    y > 0
                    and self.matrix.data[y - 1][x] != Pixel.IGNORE
                    and bool(
                        set(
                            self.matrix.get_points_in_selection(
                                self.current_position, Point(x, y - 1)
                            )
                        )
                        - self.painted
                    )
                    and Pixel.IGNORE
                    not in self.matrix.get_values_in_selection(
                        self.current_position, Point(x, y - 1)
                    )
                )

        else:

            def validation_y() -> bool:
                return (
                    y < len(self.matrix.data) - 1
                    and self.matrix.data[y + 1][x] != Pixel.IGNORE
                    and bool(
                        set(
                            self.matrix.get_points_in_selection(
                                self.current_position, Point(x, y + 1)
                            )
                        )
                        - self.painted
                    )
                    and Pixel.IGNORE
                    not in self.matrix.get_values_in_selection(
                        self.current_position, Point(x, y + 1)
                    )
                )

        while validation_x():
            if direction_x == DirectionX.LEFT:
                x -= 1
            else:
                x += 1

        while validation_y():
            if direction_y == DirectionY.TOP:
                y -= 1
            else:
                y += 1

        return Point(x, y)
