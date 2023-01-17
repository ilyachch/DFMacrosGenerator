import enum
import os
import sys
import time
from pathlib import Path
from typing import Optional

from PIL import Image


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


class Matrix:
    def __init__(self, data: list[list[int]], entrance_point: Point):
        self.data = data
        self.entrance_point = entrance_point

    @classmethod
    def from_image(cls, image: Path) -> 'Matrix':
        image = Image.open(image)
        pixels = image.convert('RGB')
        width, height = image.size

        matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b = pixels.getpixel((x, y))
                if (r, g, b) == (255, 255, 255):
                    # White pixel
                    value = 1
                elif (r, g, b) == (0, 0, 0):
                    # Black pixel
                    value = 0
                elif (r, g, b) == (255, 0, 0):
                    # Red pixel
                    value = 2
                else:
                    raise Exception("Invalid pixel color", (r, g, b))
                row.append(value)
            matrix.append(row)
        matrix = cls.find_valuable_rectangle(matrix)

        center_coordinates = cls.find_red_pixel(matrix) or cls.find_center(matrix)

        return cls(matrix, Point(*center_coordinates))

    @staticmethod
    def find_red_pixel(matrix) -> Optional[tuple[int, int]]:
        for y in range(len(matrix)):
            for x in range(len(matrix[y])):
                if matrix[y][x] == 2:
                    return (x, y)
        return None

    @staticmethod
    def find_center(matrix) -> tuple[int, int]:
        width = len(matrix[0])
        height = len(matrix)
        return (width // 2, height // 2)

    @staticmethod
    def find_valuable_rectangle(matrix: list[list[int]]) -> list[list[int]]:
        # extract submatrix from matrix that contains not only 0
        # [[0, 1, 1, 0], [0, 0, 1, 0], [0, 1, 1, 0]] -> [[1, 1], [0, 1], [1, 1]]

        # find first row with not only 0
        first_row = None
        for y in range(len(matrix)):
            if any(matrix[y]):
                first_row = y
                break
        if first_row is None:
            raise Exception("Matrix is empty")
        # find last row with not only 0
        last_row = None
        for y in range(len(matrix) - 1, -1, -1):
            if any(matrix[y]):
                last_row = y
                break
        if last_row is None:
            raise Exception("Matrix is empty")

        # find first column with not only 0
        first_column = None
        for x in range(len(matrix[0])):
            if any(row[x] for row in matrix):
                first_column = x
                break
        if first_column is None:
            raise Exception("Matrix is empty")
        # find last column with not only 0
        last_column = None
        for x in range(len(matrix[0]) - 1, -1, -1):
            if any(row[x] for row in matrix):
                last_column = x
                break
        if last_column is None:
            raise Exception("Matrix is empty")

        return [row[first_column:last_column + 1] for row in matrix[first_row:last_row + 1]]






    def get_points_in_selection(self, selection_start: Point, selection_end: Point) -> list[Point]:
        points = []
        if selection_start.x < selection_end.x:
            x_start = selection_start.x
            x_end = selection_end.x
        else:
            x_start = selection_end.x
            x_end = selection_start.x
        if selection_start.y < selection_end.y:
            y_start = selection_start.y
            y_end = selection_end.y
        else:
            y_start = selection_end.y
            y_end = selection_start.y
        for y in range(y_start, y_end + 1):
            for x in range(x_start, x_end + 1):
                points.append(Point(x, y))
        return points

    def get_values_in_selection(self, selection_start: Point, selection_end: Point) -> list[int]:
        points = self.get_points_in_selection(selection_start, selection_end)
        return [self.data[point.y][point.x] for point in points]


class Brush:
    def __init__(self, initial_point: Point):
        self.x = initial_point.x
        self.y = initial_point.y
        self.painting = False
        self.painted = set()
        self.painting_start = None
        self.commands = []

    def __repr__(self):
        return f"Brush({self.x}, {self.y})"

    @property
    def current_position(self) -> Point:
        return Point(self.x, self.y)

    def move_up(self):
        self.y -= 1
        self.commands.append(Action.MOVE_UP)

    def move_down(self):
        self.y += 1
        self.commands.append(Action.MOVE_DOWN)

    def move_left(self):
        self.x -= 1
        self.commands.append(Action.MOVE_LEFT)

    def move_right(self):
        self.x += 1
        self.commands.append(Action.MOVE_RIGHT)

    def move_up_fast(self):
        self.y -= 10
        self.commands.append(Action.MOVE_UP_FAST)

    def move_down_fast(self):
        self.y += 10
        self.commands.append(Action.MOVE_DOWN_FAST)

    def move_left_fast(self):
        self.x -= 10
        self.commands.append(Action.MOVE_LEFT_FAST)

    def move_right_fast(self):
        self.x += 10
        self.commands.append(Action.MOVE_RIGHT_FAST)

    def start_painting(self):
        if self.painting:
            raise Exception("Already painting")
        self.painting = True
        self.painting_start = (self.x, self.y)
        self.commands.append(Action.SELECT)

    def stop_painting(self):
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

    def move_to(self, target_point: Point):
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


def find_closest_not_painted_valuable_point(matrix: Matrix, brush: Brush) -> Optional[Point]:
    """
    finds the closest point that is valuable and not painted
    """
    closest_point = None
    closest_distance = None
    for y in range(len(matrix.data)):
        for x in range(len(matrix.data[y])):
            if matrix.data[y][x] != 0 and Point(x, y) not in brush.painted:
                distance = brush.current_position.distance_in_moves(Point(x, y))
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_point = Point(x, y)
    return closest_point


class RectangleDirectionX(enum.Enum):
    LEFT = 1
    RIGHT = 2


class RectangleDirectionY(enum.Enum):
    UP = 1
    DOWN = 2


def find_biggest_paintable_rectangle(matrix: Matrix, brush: Brush) -> Point:
    """
    finds the biggest paintable rectangle
    """
    x = brush.x
    y = brush.y

    found_rectangles = [
        find_biggest_rectangle_to_paint_bottom_left(matrix, brush),
        find_biggest_rectangle_to_paint_bottom_right(matrix, brush),
        find_biggest_rectangle_to_paint_top_left(matrix, brush),
        find_biggest_rectangle_to_paint_top_right(matrix, brush),
    ]

    rectangles_by_size = {
        len(set(matrix.get_points_in_selection(brush.current_position, rec)) - brush.painted): rec
        for rec in found_rectangles
    }
    maximum_size = max(rectangles_by_size.keys())

    return rectangles_by_size[maximum_size]


def find_biggest_rectangle_to_paint_top_right(
    matrix: Matrix,
    brush: Brush,
) -> Point:
    x, y = brush.x, brush.y
    while (
        x < len(matrix.data[0]) - 1
        and matrix.data[y][x + 1] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x + 1, y)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x + 1, y))
    ):
        x += 1

    while (
        y > 0
        and matrix.data[y - 1][x] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x, y - 1)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x, y - 1))
    ):
        y -= 1
    return Point(x, y)


def find_biggest_rectangle_to_paint_bottom_right(
    matrix: Matrix,
    brush: Brush,
) -> Point:
    x, y = brush.x, brush.y

    while (
        x < len(matrix.data[0]) - 1
        and matrix.data[y][x + 1] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x + 1, y)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x + 1, y))
    ):
        x += 1
    while (
        y < len(matrix.data) - 1
        and matrix.data[y + 1][x] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x, y + 1)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x, y + 1))
    ):
        y += 1
    return Point(x, y)


def find_biggest_rectangle_to_paint_bottom_left(
    matrix: Matrix,
    brush: Brush,
) -> Point:
    x, y = brush.x, brush.y

    while (
        x > 0
        and matrix.data[y][x - 1] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x - 1, y)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x - 1, y))
    ):
        x -= 1

    while (
        y < len(matrix.data) - 1
        and matrix.data[y + 1][x] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x, y + 1)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x, y + 1))
    ):
        y += 1
    return Point(x, y)


def find_biggest_rectangle_to_paint_top_left(
    matrix: Matrix,
    brush: Brush,
) -> Point:
    x, y = brush.x, brush.y
    while (
        x > 0
        and matrix.data[y][x - 1] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x - 1, y)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x - 1, y))
    ):
        x -= 1
    while (
        y > 0
        and matrix.data[y - 1][x] != 0
        and set(matrix.get_points_in_selection(brush.current_position, Point(x, y - 1)))
        - brush.painted
        and 0 not in matrix.get_values_in_selection(brush.current_position, Point(x, y - 1))
    ):
        y -= 1
    return Point(x, y)


def generate_commands(brush: Brush, matrix: Matrix, verbose: bool) -> None:
    if brush.current_position in brush.painted:
        closest_point = find_closest_not_painted_valuable_point(matrix, brush)
    else:
        closest_point = brush.current_position
    while closest_point is not None:
        brush.move_to(closest_point)
        brush.start_painting()
        opposite_corner = find_biggest_paintable_rectangle(matrix, brush)
        brush.move_to(opposite_corner)
        brush.stop_painting()
        closest_point = find_closest_not_painted_valuable_point(matrix, brush)
        if verbose:
            render_state_in_cli(matrix, brush)

    brush.move_to(matrix.entrance_point)
    if verbose:
        render_state_in_cli(matrix, brush)


def render_macros(commands, file_name: Path, to_file=True):
    new_file_name = file_name.with_suffix(".mak")
    lines = []
    lines.append(f"{file_name.stem}\n")
    values_map = {
        Action.SELECT: "\t\tSELECT\n\tEnd of group\n",
        Action.MOVE_UP: "\t\tKEYBOARD_CURSOR_UP\n\tEnd of group\n",
        Action.MOVE_DOWN: "\t\tKEYBOARD_CURSOR_DOWN\n\tEnd of group\n",
        Action.MOVE_LEFT: "\t\tKEYBOARD_CURSOR_LEFT\n\tEnd of group\n",
        Action.MOVE_RIGHT: "\t\tKEYBOARD_CURSOR_RIGHT\n\tEnd of group\n",
        Action.MOVE_UP_FAST: "\t\tKEYBOARD_CURSOR_UP_FAST\n\tEnd of group\n",
        Action.MOVE_DOWN_FAST: "\t\tKEYBOARD_CURSOR_DOWN_FAST\n\tEnd of group\n",
        Action.MOVE_LEFT_FAST: "\t\tKEYBOARD_CURSOR_LEFT_FAST\n\tEnd of group\n",
        Action.MOVE_RIGHT_FAST: "\t\tKEYBOARD_CURSOR_RIGHT_FAST\n\tEnd of group\n",
    }
    for command in commands:
        lines.append(values_map[command])
    lines.append("End of macro\n")
    data = "".join(lines)
    if to_file:
        with open(new_file_name, "w") as f:
            f.write(data)
    else:
        print(data)


def render_state_in_cli(matrix: Matrix, brush: Brush) -> None:
    data_to_print = ['   ' + ''.join(f'{i:3}' for i in range(len(matrix.data[0]))) + '\n']
    for y in range(len(matrix.data)):
        data_to_print.append(f'{y:3}')
        # draw coordinates on the left and top sides
        for x in range(len(matrix.data[y])):
            if Point(x, y) == brush.current_position:
                # color the current position with yellow

                data_to_print.append("\033[33m■■■\033[0m")
            elif Point(x, y) in brush.painted:
                # color the painted area with green

                data_to_print.append("\033[32m███\033[0m")
            else:
                value = matrix.data[y][x]
                if value == 0:
                    # color the rest with dark gray
                    data_to_print.append("\033[90m███\033[0m")
                else:
                    # color the rest with white
                    data_to_print.append("███")
        data_to_print.append("\n")
    os.system("clear")
    print("".join(data_to_print))
    time.sleep(0.2)


if __name__ == "__main__":
    image_file = Path(sys.argv[1])
    if '-v' in sys.argv:
        verbose = True
    else:
        verbose = False
    matrix = Matrix.from_image(image_file)
    brush = Brush(matrix.entrance_point)
    generate_commands(brush, matrix, verbose)
    render_macros(brush.commands, image_file, True)
