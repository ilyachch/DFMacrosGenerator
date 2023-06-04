from pathlib import Path

import click
from application import DwarfFortressMacrosGenerator
from settings import settings


@click.command()
@click.argument(
    "files",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    nargs=-1,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-v",
    "--verbose",
    count=True,
)
@click.option(
    "--visualize",
    is_flag=True,
)
@click.pass_context
def main(ctx, **kwargs):
    settings.patch_with_params(ctx)
    exit_code = DwarfFortressMacrosGenerator(settings).run()

    exit(exit_code)


if __name__ == "__main__":
    main()
