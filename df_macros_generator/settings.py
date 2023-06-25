import json
import os
from pathlib import Path
from typing import Any

import click
from click.core import ParameterSource


class Settings:
    _instance = None

    _CONFIG_FILE = Path(click.get_app_dir("df_macros_generator")) / "config.json"
    _CONFIG_PARAMS = {
        "OUTPUT": "output",
        "VISUALIZATION": "visualize",
    }

    def __new__(cls, *args: Any, **kwargs: Any) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._files: list[Path] = []
        self._verbose: int = 0
        self._output: Path = Path(os.getcwd())
        self._visualize: bool = False
        self.__update_with_config()

    def __update_with_config(self):
        if self._CONFIG_FILE.exists():
            config = json.loads(self._CONFIG_FILE.read_text())
            for config_option, settings_option in self._CONFIG_PARAMS.items():
                if config_option in config:
                    self.set_option(settings_option, config[config_option])

    def patch_with_params(self, ctx: click.Context) -> None:
        for param in ctx.params:
            if ctx.get_parameter_source(param) != ParameterSource.DEFAULT:
                self.set_option(param, ctx.params[param])

    def set_option(self, option_name: str, value: Any) -> None:
        setattr(self, f"_{option_name}", value)

    @property
    def files(self) -> list[Path]:
        return self._files

    @property
    def verbose(self) -> int:
        return self._verbose

    @property
    def output(self) -> Path:
        return self._output

    @property
    def visualize(self) -> bool:
        return self._visualize


settings = Settings()
