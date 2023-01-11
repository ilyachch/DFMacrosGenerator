import logging
import os
import time
from pathlib import Path

import click

from entities.brush import Brush, Action
from entities.matrix import Matrix, Pixel
from entities.point import Point
from settings import Settings


class DwarfFortressMacrosGenerator:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._logger = logging.getLogger(__name__)

    def run(self):
        self._set_logging_level()
        for file in self._settings.files:
            commands = self.generate_commands(file)
            macros_text = self.render_macros(commands, file)
            file_to_write = self.get_macros_file(file)
            file_to_write.write_text(macros_text)

    def get_macros_file(self, file: Path) -> Path:
        folder = self._settings.output
        file = file.with_suffix(".mak")
        return folder / file

    def _set_logging_level(self) -> None:
        if self._settings.verbose == 0:
            logging.basicConfig(level=logging.WARNING)
        elif self._settings.verbose == 1:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def generate_commands(self, file: Path) -> list[Action]:
        matrix = Matrix.from_image(file)
        brush = Brush(matrix)

        while True:
            more_moves = brush.paint()
            if not more_moves:
                break
            if self._settings.visualize:
                self.render_state_in_cli(matrix, brush)

        brush.move_to(matrix.exit_point)
        if self._settings.visualize:
            self.render_state_in_cli(matrix, brush)
        return brush.commands

    def render_macros(self, commands: list[Action], file_name: Path) -> str:
        lines = [f"{file_name.stem}\n"]
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
        return "".join(lines)

    def render_state_in_cli(self, matrix: Matrix, brush: Brush) -> None:
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
                    if value == Pixel.IGNORE:
                        # color the rest with dark gray
                        data_to_print.append("\033[90m███\033[0m")
                    else:
                        # color the rest with white
                        data_to_print.append("███")
            data_to_print.append("\n")
        click.clear()
        click.echo("".join(data_to_print), color=True)
        click.echo(f"Movements: {len(brush.commands)}")
        time.sleep(0.2)
