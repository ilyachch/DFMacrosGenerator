# DFMacrosGenerator

Generates Mining macros for Dwarf fortress from an image.

## Usage

Source image should be an image with a black background and white pixels for mining.

Start point is red pixel, end point is green pixel. If there is no green pixel, the end point is the same as the start point.

| Color | Code      | Meaning      |
|-------|-----------|--------------|
| White | `#FFFFFF` | Mining pixel |
| Black | `#000000` | Background   |
| Red   | `#FF0000` | Start point  |
| Green | `#00FF00` | End point    |



[![asciicast](https://asciinema.org/a/d4NxunHUXHOgE3KnPoqLuO9Ck.svg)](https://asciinema.org/a/d4NxunHUXHOgE3KnPoqLuO9Ck)

Examples:

The source image:

![](examples/round_with_bubles.bmp)

The generated macro:

![!](examples/result.png)
