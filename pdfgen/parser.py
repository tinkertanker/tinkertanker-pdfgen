# -*- coding: utf-8 -*-

# Python Standard Library Imports
import json

# Local Imports
from pdfgen import metadata


def parse_layout(layout_json_path):
    with open(layout_json_path, 'rt') as layout_json_file:
        layout_json = json.load(layout_json_file)
    parsed_layout = {}
    for entry_key, draw_format_json in layout_json.items():
        draw_format = metadata.DrawFormat(name=entry_key)
        for key, value in draw_format_json.items():
            setattr(draw_format, key, value)
        parsed_layout[entry_key] = draw_format
    return parsed_layout
