# Tinkertanker Simple PDF Generator

Allow generation of PDF files based on a given schema. Supports Python 3.5 and up.

## Dependencies

- PyPDF2 `>=1.26.0,<1.27`
- reportlab `>=3.5.34,<3.6`
- Pillow `>=7.0.0,<7.1`

## Installation

Install using pip

    pip install git+https://<your_username>@github.com/tinkertanker/tinkertanker-pdfgen.git@0.1.0

or

    pip install git+ssh://git@github.com/tinkertanker/tinkertanker-pdfgen.git@0.1.0

## Usage

Here is a simple example.

    from pdfgen import engine
    generator = engine.PdfGenerator('template.pdf', 'layout.json', 'fonts', 'images')
    generator.generate([['User', 'logo.png']], [['name', 'logo']], 'output.pdf')

You may also run the generator as a command line tool.

    usage: tinkertanker_pdfgen [-h] [-t file] [-l file] [-f folder] [-i folder] [-e [text [text ...]]]
                               [-k [key [key ...]]] [-o file] [-v]

    Tinkertanker PDF Generator

    optional arguments:
      -h, --help            show this help message and exit
      -t file, --template file
                            path to the template file (.pdf)
      -l file, --layout file
                            path to the layout file (.json)
      -f folder, --font-folder folder
                            path to the font folder
      -i folder, --image-folder folder
                            path to the image folder
      -e [text [text ...]], --entries [text [text ...]]
                            inputs to be printed
      -k [key [key ...]], --keys [key [key ...]]
                            key of the inputs to be printed
      -o file, --output-file file
                            path to the output file (.pdf)
      -v, --verbose         increase output verbosity

The number of entries and keys should be equal. All the keys should exist within the provided layout file.

## Layout Schema JSON Format

Here is a sample of the layout file. All parameters are optional.

    {
      "name": {
          "category": "text",
          "alignment": "left",
          "position": "3.4",
          "offset": "0.6",
          "r_offset": "1.0",
          "font": "Helvetica",
          "size": "15",
          "overflow": "wrap",
          "spacing": "0.5",
          "typecase": "default",
          "cmyk_color": ["0.0", "0.0", "0.0", "0.5"]
      },
      "qrcode": {
          "category": "qr",
          "size": "2",
          "offset": "1.0",
          "position": "2.0",
          "rgb_color": ["125.0", "255.0", "0.0"]
      },
      "barcode": {
          "category": "bar",
          "size": "2",
          "offset": "4.0",
          "position": "2.0",
          "rgb_color": ["125.0", "255.0", "0.0"]
      },
      "logo": {
          "category": "image",
          "size": "1",
          "offset": "0.6",
          "position": "0.6"
      }
    }

### Text Category

Valid parameters:

- `alignment`: `left`, `center`, or `right`. Default to `left`.
- `position`: Distance in centimeter from bottom end of the page. Default to 0.6.
- `offset`: Distance in centimeter from left end of page. Default to 0.6.
- `r_offset`: Minimum distance in centimeter from left end of page. Default to the value of `offset` parameter.
- `font`: Font file name to use without the extension.
- `size`: Font size in pt. Default to 8.0.
- `overflow`: Sets the alternative rendering when the expected text width is longer than the given space. Valid options are `shrink`, `wrap`, and `wrapup`. Default to `shrink`.
  - `shrink`: Font size will be reduced until the text fits the given space.
  - `wrap`: Split the text into two lines. The first line will be placed in the original location, while the second line will be placed below it.
  - `wrapup`: Split the text into two lines. The second line will be placed in the original location, while the first line will be placed above it.
- `spacing`: Distance in centimeter between the splitted lines. Only used when `overflow` is set to either `wrap` or `wrapup`. Default to 0.5.
- `typecase`: Change the text typecase before rendering. Valid options are `default`, `upcase`, and `downcase`. Default to `default`.
  - `default`: No change to text.
  - `upcase`: Force text to be uppercase.
  - `downcase`: Force text to be lowercase.
- `cmyk_color`: Set the color of the text in CMYK format. It is an array with exactly four components, whose values are in between 0.0 and 1.0. Default to [0.0, 0.0, 0.0, 1.0]. Conflicts with `rgb_color`. Prefered over `rgb_color`.
- `rgb_color`: Not recommended. Set the color of the text in RGB format. It is an array with exactly three components, whose values are in between 0.0 and 255.0. Conflicts with `cymk_color`.

### QR Category

Valid parameters:

- `position`: Distance in centimeter from bottom end of the page. Default to 0.6.
- `offset`: Distance in centimeter from left end of page. Default to 0.6.
- `size`: Height in centimeter. Default to 8.0. Preferable to have a value of >=2.0.
- `cmyk_color`: Set the color of the text in CMYK format. It is an array with exactly four components, whose values are in between 0.0 and 1.0. Default to [0.0, 0.0, 0.0, 1.0]. Conflicts with `rgb_color`. Prefered over `rgb_color`.
- `rgb_color`: Not recommended. Set the color of the text in RGB format. It is an array with exactly three components, whose values are in between 0.0 and 255.0. Conflicts with `cymk_color`.

### Bar Category

Valid parameters:

- `position`: Distance in centimeter from bottom end of the page. Default to 0.6.
- `offset`: Distance in centimeter from left end of page. Default to 0.6.
- `size`: Height in centimeter. Default to 8.0. Preferable to have a value of >=2.0.
- `cmyk_color`: Set the color of the text in CMYK format. It is an array with exactly four components, whose values are in between 0.0 and 1.0. Default to [0.0, 0.0, 0.0, 1.0]. Conflicts with `rgb_color`. Prefered over `rgb_color`.
- `rgb_color`: Not recommended. Set the color of the text in RGB format. It is an array with exactly three components, whose values are in between 0.0 and 255.0. Conflicts with `cymk_color`.

### Image Category

Images are always aligned to the left and fit the given space as much as possible, while maintaining its own aspect ratio.

Valid parameters:

- `position`: Distance in centimeter from bottom end of the page. Default to 0.6.
- `offset`: Distance in centimeter from left end of page. Default to 0.6.
- `size`: Height in centimeter. Default to 8.0.

## Font Support

Only TTF format is supported.

## Image Support

Most raster graphics formats are supported. PDF and SVG vector formats are also supported.

## Testing

To run the integration tests, you will need to have ImageMagick and Poppler installed. You may install them via Homebrew. At the moment, the integration tests can only be run in macOS. It is theoritically possible to run it in Linux, provided that the dependencies are available. But it is not yet tested.

## Help and Support

This package is currently maintained by Eric Yulianto. If you find any issue, drop me a direct message to `@eric` at Tinkertanker Slack workspace.

_Last Updated: 19 Jun 2020_
