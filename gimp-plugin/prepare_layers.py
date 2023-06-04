#!/usr/bin/env python

import os

from gimpfu import *


def save_layer(obj, output_dir, prefix=""):
    png_path = os.path.join(output_dir, "{prefix}{name}.png".format(prefix=prefix, name=obj.name))
    pdb.gimp_file_save(obj.image, obj, png_path, png_path)


def save_layers(image, output_dir, prefix=""):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for obj in image.layers:
        if pdb.gimp_item_is_group(obj):
            save_layers(obj, output_dir, obj.name + "_")
        else:
            save_layer(obj, output_dir, prefix)


def extract_layers(image, drawable, output_dir):
    save_layers(image, output_dir)


register(
    "python-fu-extract-layers",
    "Extract layers as PNG images",
    "Extracts layers of an XCF image as separate PNG files",
    "Ilia Chichak",
    "Ilia Chichak",
    "2023",
    "<Image>/File/Plugins/Save layers as PNG...",
    "*",
    [(PF_DIRNAME, "output_dir", "Output directory", os.path.expanduser("~"))],
    [],
    extract_layers,
)

main()
