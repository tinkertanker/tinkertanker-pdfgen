# -*- coding: utf-8 -*-

# Python Standard Library Imports
import collections
import io
import os

# Third Party Library Imports
import PIL
import PyPDF2
from reportlab.graphics import renderPDF
from reportlab.graphics import shapes
from reportlab.graphics.barcode import code39
from reportlab.graphics.barcode import qr
from reportlab.lib import colors
from reportlab.lib import units
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

# Local Imports
from pdfgen import metadata
from pdfgen import parser
from pdfgen import utils


def load_fonts(font_root_path):
    for font_filename in os.listdir(font_root_path):
        font_path = os.path.join(font_root_path, font_filename)
        if os.path.isfile(font_path):
            font_name, font_ext = os.path.splitext(os.path.basename(font_path))
            if font_ext == '.ttf':
                font_name = font_name.replace(' ', '_')
                font = ttfonts.TTFont(font_name, font_path)
                pdfmetrics.registerFont(font)


class PdfGenerator(object):
    DEFAULT_PAGE_WIDTH = 9.0 * units.cm
    DEFAULT_PAGE_HEIGHT = 6.2 * units.cm
    Size = collections.namedtuple('Size', ['width', 'height'])

    def __init__(self, template_path=None, layout_path=None,
                 font_root_path=None, image_root_path=None):
        self._template = None

        self.template_path = template_path
        self.layout_path = layout_path
        load_fonts(font_root_path)
        self.image_root_path = image_root_path

    @property
    def template(self):
        if self._template is None:
            self._template = PyPDF2.PdfFileReader(open(self.template_path, 'rb'))
        return self._template

    @property
    def layout_path(self):
        return self._layout_path

    @layout_path.setter
    def layout_path(self, value):
        if value is None:
            self._layout_path = None
            self.layout = None
        else:
            self._layout_path = value
            self.layout = parser.parse_layout(value)

    @property
    def page_size(self):
        try:
            media_box = self.template.getPage(0).mediaBox
        except AttributeError:
            width, height = (self.DEFAULT_PAGE_WIDTH, self.DEFAULT_PAGE_HEIGHT)
        else:
            width, height = (float(media_box[2]), float(media_box[3]))
        finally:
            size = type(self).Size(width=width, height=height)
        return size

    def generate(self, entries, order, filename):
        pdf_output = PyPDF2.PdfFileWriter()

        for i, (page_entries, page_order) in enumerate(zip(entries, order)):
            generated_overlays = self._draw_page_overlays(entries=page_entries,
                                                          order=page_order)
            try:
                page_output = self.template.getPage(i)
            except IndexError:
                page_output = self.template.getPage(0)

            for generated_overlay in generated_overlays:
                try:
                    page_overlay = generated_overlay.getPage(0)
                except IndexError:
                    pass
                else:
                    page_output.mergePage(page_overlay)

            pdf_output.addPage(page_output)

        with open(filename, 'wb') as file_output_stream:
            pdf_output.write(file_output_stream)

    def _draw_page_overlays(self, entries, order):
        overlays = []

        for entry_key, entry_string in zip(order, entries):
            if entry_string and entry_string.strip():
                stripped_entry_string = entry_string.strip()
                draw_format = self.layout[entry_key]
                if draw_format.category == metadata.DrawFormat.CATEGORY_TEXT:
                    overlays.append(self._draw_text(stripped_entry_string,
                                                    draw_format))
                elif draw_format.category == metadata.DrawFormat.CATEGORY_QR:
                    overlays.append(self._draw_qr(stripped_entry_string,
                                                  draw_format))
                elif draw_format.category == metadata.DrawFormat.CATEGORY_BAR:
                    overlays.append(self._draw_bar(stripped_entry_string,
                                                   draw_format))
                elif draw_format.category == metadata.DrawFormat.CATEGORY_IMAGE:
                    overlays.append(self._draw_image(stripped_entry_string,
                                                     draw_format))

        return overlays

    def _draw_text(self, content, draw_format):
        draw_buffer = io.BytesIO();
        draw_canvas = canvas.Canvas(draw_buffer, pagesize=self.page_size)

        font_name = draw_format.font
        font_size = draw_format.size
        draw_canvas.setFont(font_name, font_size)

        draw_canvas.setFillColor(colors.black)
        if draw_format.cmyk_color is not None:
            c, m, y, k = draw_format.cmyk_color
            draw_canvas.setFillColorCMYK(c, m, y, k)
        elif draw_format.rgb_color is not None:
            r, g, b = draw_format.rgb_color
            draw_canvas.setFillColorRGB(r, g, b)

        x_offset = draw_format.offset * units.cm
        x_r_offset = draw_format.r_offset * units.cm
        max_width = self.page_size.width - x_offset - x_r_offset
        y_pos = draw_format.position * units.cm
        spacing = draw_format.spacing * units.cm

        typecase = draw_format.typecase
        if typecase == metadata.DrawFormat.TYPECASE_DEFAULT:
            cased_content = content
        elif typecase == metadata.DrawFormat.TYPECASE_UPCASE:
            cased_content = content.upper()
        elif typecase == metadata.DrawFormat.TYPECASE_DOWNCASE:
            cased_content = content.lower()
        else:
            cased_content = content

        string_width = draw_canvas.stringWidth(cased_content, font_name, font_size)

        if string_width > max_width:
            def calculate_width(text):
                return draw_canvas.stringWidth(text, font_name, font_size)

            if draw_format.overflow == metadata.DrawFormat.OVERFLOW_WRAP:
                top, bottom = utils.split_text(
                    cased_content,
                    max_width,
                    calculate_width
                )
            elif draw_format.overflow == metadata.DrawFormat.OVERFLOW_WRAPUP:
                top, bottom = utils.split_text(
                    cased_content,
                    max_width,
                    calculate_width,
                    True
                )
                if bottom:
                    y_pos += spacing
            else:
                top = cased_content
                bottom = None

            if draw_format.overflow == metadata.DrawFormat.OVERFLOW_SHRINK:
                adjusted_font_size = font_size * max_width / string_width
                draw_canvas.setFont(font_name, adjusted_font_size)
        else:
            top = cased_content
            bottom = None

        alignment = draw_format.alignment
        if alignment == metadata.DrawFormat.ALIGNMENT_CENTER:
            x_pos = (self.page_size.width + x_offset - x_r_offset) / 2.0
            draw_canvas.drawCentredString(x_pos, y_pos, top)
            if bottom:
                draw_canvas.drawCentredString(x_pos, y_pos - spacing, bottom)
        elif alignment == metadata.DrawFormat.ALIGNMENT_LEFT:
            x_pos = x_offset
            draw_canvas.drawString(x_pos, y_pos, top)
            if bottom:
                draw_canvas.drawString(x_pos, y_pos - spacing, bottom)
        elif alignment == metadata.DrawFormat.ALIGNMENT_RIGHT:
            page_width = self.page_size.width
            top_width = draw_canvas.stringWidth(top, font_name, font_size)
            x_pos = page_width - x_offset - top_width
            draw_canvas.drawString(x_pos, y_pos, top)
            if bottom:
                bottom_width = draw_canvas.stringWidth(bottom,
                                                       font_name,
                                                       font_size)
                x_pos = page_width - x_offset - bottom_width
                draw_canvas.drawString(x_pos, y_pos - spacing, bottom)

        draw_canvas.save()
        draw_buffer.seek(0)
        return PyPDF2.PdfFileReader(draw_buffer)

    def _draw_qr(self, content, draw_format):
        draw_buffer = io.BytesIO();
        draw_canvas = canvas.Canvas(draw_buffer, pagesize=self.page_size)

        qr_color = colors.black
        if draw_format.cmyk_color is not None:
            c, m, y, k = draw_format.cmyk_color
            qr_color = colors.CMYKColor(c, m, y, k)
        elif draw_format.rgb_color is not None:
            r, g, b = draw_format.rgb_color
            qr_color = colors.Color(r, g, b)

        qr_code = qr.QrCodeWidget(content,
                                  barFillColor=qr_color,
                                  barBorder=0)
        qr_bounds = qr_code.getBounds()
        qr_size = type(self).Size(qr_bounds[2] - qr_bounds[0],
                                  qr_bounds[3] - qr_bounds[1])

        size = draw_format.size * units.cm
        d = shapes.Drawing(size, size, transform=[size / qr_size.width, 0, 0,
                                                  size / qr_size.height, 0, 0])
        d.add(qr_code)

        x_pos = draw_format.offset * units.cm
        y_pos = draw_format.position * units.cm
        draw_canvas.setFillColor(colors.blue)
        renderPDF.draw(d, draw_canvas, x_pos, y_pos)

        draw_canvas.save()
        draw_buffer.seek(0)
        return PyPDF2.PdfFileReader(draw_buffer)

    def _draw_bar(self, content, draw_format):
        draw_buffer = io.BytesIO();
        draw_canvas = canvas.Canvas(draw_buffer, pagesize=self.page_size)

        font_name = draw_format.font
        font_size = draw_format.size
        draw_canvas.setFont(font_name, font_size)

        content_uppercase = content.upper()
        content_wide = '  '.join(list(content_uppercase))

        x_pos = self.page_size.width / 2.0
        y_pos = draw_format.position * units.cm

        draw_canvas.drawCentredString(x_pos, y_pos, content_wide)

        barcode = code39.Standard39(
            content_uppercase,
            barWidth=0.0075*units.inch*10.0/8.0,
            barHeight=0.7*units.cm,
            checksum=False
        )

        x_pos = draw_format.offset * units.cm
        y_pos -= 0.775 * units.cm

        barcode.drawOn(draw_canvas, x_pos, y_pos)

        draw_canvas.save()
        draw_buffer.seek(0)
        return PyPDF2.PdfFileReader(draw_buffer)

    def _draw_image(self, content, draw_format):
        draw_buffer = io.BytesIO();

        if content.endswith('.svg'):
            draw_canvas = canvas.Canvas(draw_buffer, pagesize=self.page_size)

            image = svg2rlg(self._image_named(content))
            image_width = image.minWidth()
            image_height = image.height

            expected_height = draw_format.size * units.cm
            expected_width = expected_height * image_width / image_height

            x_pos = draw_format.offset * units.cm
            y_pos = draw_format.position * units.cm
            r_x_pos = draw_format.r_offset * units.cm

            max_width = self.page_size.width - x_pos - r_x_pos

            if expected_width > max_width:
                width = max_width
                height = max_width * image_height / image_width
            else:
                width = expected_width
                height = expected_height

            image.width = width
            image.height = height
            image.scale(width / image_width, height / image_height)

            renderPDF.draw(image, draw_canvas, x_pos, y_pos)
            draw_canvas.save()
        elif content.endswith('.pdf'):
            image = PyPDF2.PdfFileReader(self._image_named(content))
            image_page = image.getPage(0)
            image_width = float(image_page.mediaBox[2])
            image_height = float(image_page.mediaBox[3])

            expected_height = draw_format.size * units.cm
            expected_width = expected_height * image_width / image_height

            x_pos = draw_format.offset * units.cm
            y_pos = draw_format.position * units.cm
            r_x_pos = draw_format.r_offset * units.cm

            max_width = self.page_size.width - x_pos - r_x_pos

            if expected_width > max_width:
                width = max_width
                height = max_width * image_height / image_width
            else:
                width = expected_width
                height = expected_height

            image_page.scaleTo(width=width, height=height)

            pdf_writer = PyPDF2.PdfFileWriter()
            pdf_writer.addBlankPage(width=self.page_size.width, height=self.page_size.height)

            page = pdf_writer.getPage(0)
            page.mergeTranslatedPage(image_page, x_pos, y_pos)
            pdf_writer.write(draw_buffer)
        else:
            draw_canvas = canvas.Canvas(draw_buffer, pagesize=self.page_size)

            image = PIL.Image.open(self._image_named(content))
            image_width, image_height = image.size

            expected_height = draw_format.size * units.cm
            expected_width = expected_height * image_width / image_height

            x_pos = draw_format.offset * units.cm
            y_pos = draw_format.position * units.cm
            r_x_pos = draw_format.r_offset * units.cm

            max_width = self.page_size.width - x_pos - r_x_pos

            if expected_width > max_width:
                width = max_width
                height = max_width * image_height / image_width
            else:
                width = expected_width
                height = expected_height

            draw_canvas.drawImage(ImageReader(image), x_pos, y_pos, width=width, height=height)
            draw_canvas.save()

        draw_buffer.seek(0)
        return PyPDF2.PdfFileReader(draw_buffer)

    def _image_named(self, image_name):
        return os.path.join(self.image_root_path, image_name)
