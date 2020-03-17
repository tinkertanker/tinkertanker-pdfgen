#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python Standard Library Imports
import argparse
import logging

# Locals Imports
from pdfgen import engine


def parse_arguments(args=None):
    argument_parser = argparse.ArgumentParser(description='Tinkertanker PDF Generator')
    argument_parser.add_argument('-t', '--template', metavar='file', type=str,
                                 help='path to the template file (.pdf)')
    argument_parser.add_argument('-l', '--layout', metavar='file', type=str,
                                 help='path to the layout file (.json)')
    argument_parser.add_argument('-f', '--font-folder', metavar='folder', type=str,
                                 help='path to the font folder')
    argument_parser.add_argument('-e', '--entries', nargs='*', metavar='text', type=str,
                                 help='inputs to be printed')
    argument_parser.add_argument('-k', '--keys', nargs='*', metavar='key', type=str,
                                 help='key of the inputs to be printed')
    argument_parser.add_argument('-o', '--output-file', metavar='file', type=str,
                                 help='path to the output file (.pdf)')
    argument_parser.add_argument('-v', '--verbose', action='store_true',
                                 help='increase output verbosity')
    return argument_parser.parse_args(args)


def main():
    args = parse_arguments()

    # Logging setup
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = '[%(asctime)-15s] (%(name)s) %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format,
                        level=log_level)

    logger = logging.getLogger(__name__)

    logger.debug('Arguments: {args}'.format(args=args))

    template_path = args.template
    layout_path = args.layout
    font_root_path = args.font_folder
    entries = args.entries
    keys = args.keys
    output_file = args.output_file

    if len(args.entries) == len(args.keys):
        pdf_generator = engine.PdfGenerator(template_path, layout_path, font_root_path)
        pdf_generator.generate([entries], [keys], output_file)
        logger.info('Generated at {output}'.format(output=output_file))
    else:
        logger.error('Entries and keys should have the same number of elements.')


if __name__ == '__main__':
    main()
