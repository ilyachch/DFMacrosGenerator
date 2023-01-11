from pathlib import Path
from typing import Optional

from PIL import Image

from entities.point import Point
import enum


class Pixel(enum.Enum):
    IGNORE = enum.auto()
    PROCESS = enum.auto()
    ENTER = enum.auto()
    EXIT = enum.auto()

    @classmethod
    def from_color(cls, color: tuple[int, int, int]) -> "Pixel":
        if color == (0, 0, 0):  # black
            return cls.IGNORE
        elif color == (255, 255, 255):  # white
            return cls.PROCESS
        elif color == (255, 0, 0):  # red
            return cls.ENTER
        elif color == (0, 255, 0):  # green
            return cls.EXIT
        else:
            raise ValueError(f"Unknown color: {color}")

    def __bool__(self):
        return self != self.IGNORE


class Matrix:
    def __init__(self, data: list[list[Pixel]]) -> None:
        self.data = data
        center = Point(len(data[0]) // 2, len(data) // 2)
        self.entrance_point = self.find_pixel_by_type(Pixel.ENTER) or center
        self.exit_point = self.find_pixel_by_type(Pixel.EXIT) or center

    @classmethod
    def from_image(cls, image: Path) -> "Matrix":
        image = Image.open(image)
        pixels = image.load()

        width, height = image.size

        matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[x, y]
                pixel = pixel[:3]
                row.append(Pixel.from_color(pixel))
            matrix.append(row)
        field: list[list[Pixel]] = cls.find_valuable_rectangle(matrix)

        return cls(field)

    def find_pixel_by_type(self, point_type: Pixel) -> Optional[Point]:
        for y, row in enumerate(self.data):
            for x, pixel in enumerate(row):
                if pixel == point_type:
                    return Point(x, y)
        return None

    @staticmethod
    def find_valuable_rectangle(matrix: list[list[Pixel]]) -> list[list[Pixel]]:
        first_row = None
        for y in range(len(matrix)):
            if any(matrix[y]):
                first_row = y
                break
        if first_row is None:
            raise Exception("Matrix is empty")
        last_row = None
        for y in range(len(matrix) - 1, -1, -1):
            if any(matrix[y]):
                last_row = y
                break
        if last_row is None:
            raise Exception("Matrix is empty")

        first_column = None
        for x in range(len(matrix[0])):
            if any(row[x] for row in matrix):
                first_column = x
                break
        if first_column is None:
            raise Exception("Matrix is empty")
        last_column = None
        for x in range(len(matrix[0]) - 1, -1, -1):
            if any(row[x] for row in matrix):
                last_column = x
                break
        if last_column is None:
            raise Exception("Matrix is empty")

        return [row[first_column : last_column + 1] for row in matrix[first_row : last_row + 1]]

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

    def get_values_in_selection(self, selection_start: Point, selection_end: Point) -> list[Pixel]:
        points = self.get_points_in_selection(selection_start, selection_end)
        return [self.data[point.y][point.x] for point in points]
