import sys
from PIL import Image
import enum
from pathlib import Path

image_file = Path(sys.argv[1])
image = Image.open(image_file)
pixels = image.load()


class Action(enum.Enum):
    SELECT = enum.auto()
    MOVE_UP = enum.auto()
    MOVE_DOWN = enum.auto()
    MOVE_LEFT = enum.auto()
    MOVE_RIGHT = enum.auto()


def generate_matrix(image_file):
    image = Image.open(image_file)
    pixels = image.load()

    width, height = image.size

    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = pixels[x, y]
            pixel = pixel[:3]
            if pixel == (255, 255, 255):
                # White pixel
                value = 1
            elif pixel == (0, 0, 0):
                # Black pixel
                value = 0
            elif pixel == (255, 0, 0):
                # Red pixel
                value = 2
            else:
                raise Exception("Invalid pixel color", pixel)
            row.append(value)
        matrix.append(row)

    return matrix


def find_red_pixel(matrix):
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            if matrix[y][x] == 2:
                return (x, y)
    return None


def find_corners(
    matrix,
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]:
    top_left = None
    top_right = None
    bottom_left = None
    bottom_right = None
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            if matrix[y][x] == 1:
                if top_left is None:
                    top_left = (x, y)
                if bottom_right is None:
                    bottom_right = (x, y)
                if x < top_left[0]:
                    top_left = (x, y)
                if x > bottom_right[0]:
                    bottom_right = (x, y)
                if y < top_left[1]:
                    top_left = (x, y)
                if y > bottom_right[1]:
                    bottom_right = (x, y)
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            if matrix[y][x] == 1:
                if top_right is None:
                    top_right = (x, y)
                if bottom_left is None:
                    bottom_left = (x, y)
                if x > top_right[0]:
                    top_right = (x, y)
                if x < bottom_left[0]:
                    bottom_left = (x, y)
                if y < top_right[1]:
                    top_right = (x, y)
                if y > bottom_left[1]:
                    bottom_left = (x, y)
    return top_left, top_right, bottom_left, bottom_right


def cut_matrix(matrix):
    top_left, top_right, bottom_left, bottom_right = find_corners(matrix)
    return [
        row[top_left[0] : bottom_right[0] + 1]
        for row in matrix[top_left[1] : bottom_right[1] + 1]
    ]


def move_to(matrix, x_from, y_from, x_end, y_end):
    commands = []
    if x_from > x_end:
        while x_from > x_end:
            x_from -= 1
            commands.append(Action.MOVE_LEFT)
    elif x_from < x_end:
        while x_from < x_end:
            x_from += 1
            commands.append(Action.MOVE_RIGHT)
    if y_from > y_end:
        while y_from > y_end:
            y_from -= 1
            commands.append(Action.MOVE_UP)
    elif y_from < y_end:
        while y_from < y_end:
            y_from += 1
            commands.append(Action.MOVE_DOWN)
    return commands


def process_row(row, direction):
    commands = []

    select = False

    for cell_number, value in enumerate(row):
        if value == 1 or value == 2:
            if not select:
                commands.append(Action.SELECT)
                select = True
        next_value = row[cell_number + 1] if cell_number < len(row) - 1 else None
        if next_value is None or next_value == 0:
            if select:
                commands.append(Action.SELECT)
                select = False
        if next_value is not None:
            commands.append(direction)

    return commands


matrix = generate_matrix(image_file)
matrix = cut_matrix(matrix)

x_start_point, y_start_point = find_red_pixel(matrix)
commands = move_to(matrix, x_start_point, y_start_point, 0, 0)
for idx, row in enumerate(matrix):
    if idx % 2 == 0:
        commands += process_row(row, Action.MOVE_RIGHT)
    else:
        commands += process_row(list(reversed(row)), Action.MOVE_LEFT)
    if idx < len(matrix) - 1:
        commands.append(Action.MOVE_DOWN)
commands += move_to(
    matrix, len(matrix[0]) - 1, len(matrix) - 1, x_start_point, y_start_point
)


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


render_macros(commands, image_file, True)
