#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

TEST_CASES = [
    ('tests/expected/1.pdf', ['Guest', 'Company', 'Table 1', 'sample', 'a.png'], 'tests/tmp/1.pdf', 'tests/pdfdiff/1'),
    ('tests/expected/2.pdf', ['Person', 'Corporation', 'Table 2', 'example', 'b.jpg'], 'tests/tmp/2.pdf', 'tests/pdfdiff/2'),
    ('tests/expected/4.pdf', ['Student', 'School', '4A', 'class', 'd.svg'], 'tests/tmp/4.pdf', 'tests/pdfdiff/4')
]

def run_command(c):
    p = subprocess.Popen(c)
    p.communicate()

def run_pdfgen(strings, output):
    run_command(['tinkertanker_pdfgen', '-t', 'tests/sample/template/guest.pdf',
                                        '-l', 'tests/sample/layout/guest.json',
                                        '-f', 'tests/sample/font',
                                        '-i', 'tests/sample/image',
                                        '-e'] + strings +
                                       ['-k', 'name', 'affiliation', 'table', 'code', 'image',
                                        '-o', output,
                                        '-v'])


def run_diff(temp, expected, actual):
    run_command(['tests/scripts/diffpdf.sh', temp, expected, actual])

def main():
    run_command(['mkdir', '-p', 'tests/tmp'])
    for (expected, strings, output, diffdir) in TEST_CASES:
        run_pdfgen(strings, output)
        run_diff(diffdir, expected, output)

if __name__ == '__main__':
    main()
