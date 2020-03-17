# -*- coding: utf-8 -*-


class DrawFormat(object):
    # Category Constants
    CATEGORY_TEXT = 'text'
    CATEGORY_QR = 'qr'
    CATEGORY_BAR = 'bar'
    CATEGORY_IMAGE = 'image'
    # Alignment Constants
    ALIGNMENT_LEFT = 'left'
    ALIGNMENT_CENTER = 'center'
    ALIGNMENT_RIGHT = 'right'
    # Font Constants
    FONT_HELVETICA = 'Helvetica'
    # Overflow Constants
    OVERFLOW_WRAP = 'wrap'
    OVERFLOW_WRAPUP = 'wrapup'
    OVERFLOW_SHRINK = 'shrink'
    # Typecase Constants
    TYPECASE_DEFAULT = 'default'
    TYPECASE_UPCASE = 'upcase'
    TYPECASE_DOWNCASE = 'downcase'

    def __init__(self, name, category=None, alignment=None,
                 cmyk_color=None, rgb_color=None,
                 offset=None, r_offset=None,
                 position=None, font=None, size=None,
                 overflow=None, spacing=None, typecase=None):
        # Defaults
        self._category = type(self).CATEGORY_TEXT
        self._alignment = type(self).ALIGNMENT_CENTER
        self._offset = 0.6
        self._r_offset = None
        self._position = 0.6
        self._cmyk_color = [0.0, 0.0, 0.0, 1.0]
        self._rgb_color = None
        self._font = type(self).FONT_HELVETICA
        self._size = 8.0
        self._overflow = type(self).OVERFLOW_WRAP
        self._spacing = 0.5
        self._typecase = type(self).TYPECASE_DEFAULT

        self.name = name
        self.category = category
        self.alignment = alignment
        self.cmyk_color = cmyk_color
        self.rgb_color = rgb_color
        self.offset = offset
        self.r_offset = r_offset
        self.position = position
        self.font = font
        self.size = size
        self.overflow = overflow
        self.spacing = spacing
        self.typecase = typecase

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if value in type(self).valid_categories():
            self._category = value

    @property
    def alignment(self):
        return self._alignment

    @alignment.setter
    def alignment(self, value):
        if value in type(self).valid_alignments():
            self._alignment = value

    @property
    def cmyk_color(self):
        return self._cmyk_color

    @cmyk_color.setter
    def cmyk_color(self, value):
        if value and isinstance(value, list) and len(value) == 4:
            new_cmyk_color = [self._validate_zero_to_one(component)
                              for component in value]
            if None not in new_cmyk_color:
                self._cmyk_color = new_cmyk_color
                self._rgb_color = None

    @property
    def rgb_color(self):
        return self._rgb_color

    @rgb_color.setter
    def rgb_color(self, value):
        if value and isinstance(value, list) and len(value) == 3:
            new_rgb_color = [self._validate_zero_to_one(component, norm=255.0)
                             for component in value]
            if None not in new_rgb_color:
                self._rgb_color = new_rgb_color
                self._cmyk_color = None

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        new_offset = self._validate_non_negative_float(value)
        if new_offset is not None:
            self._offset = new_offset

    @property
    def r_offset(self):
        return self._r_offset or self._offset

    @r_offset.setter
    def r_offset(self, value):
        if value is None:
            self._r_offset = None
        else:
            new_r_offset = self._validate_non_negative_float(value)
            if new_r_offset is not None:
                self._r_offset = new_r_offset

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        new_position = self._validate_non_negative_float(value)
        if new_position is not None:
            self._position = new_position

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        new_size = self._validate_non_negative_float(value)
        if new_size is not None:
            self._size = new_size

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        if value and isinstance(value, str):
            self._font = value

    @property
    def overflow(self):
        return self._overflow

    @overflow.setter
    def overflow(self, value):
        if value in type(self).valid_overflows():
            self._overflow = value

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        new_spacing = self._validate_non_negative_float(value)
        if new_spacing is not None:
            self._spacing = new_spacing

    @property
    def typecase(self):
        return self._typecase

    @typecase.setter
    def typecase(self, value):
        if value in type(self).valid_typecases():
            self._typecase = value

    @classmethod
    def valid_categories(cls):
        return [cls.CATEGORY_TEXT,
                cls.CATEGORY_QR,
                cls.CATEGORY_BAR,
                cls.CATEGORY_IMAGE]

    @classmethod
    def valid_alignments(cls):
        return [cls.ALIGNMENT_LEFT,
                cls.ALIGNMENT_CENTER,
                cls.ALIGNMENT_RIGHT]

    @classmethod
    def valid_overflows(cls):
        return [cls.OVERFLOW_WRAP,
                cls.OVERFLOW_WRAPUP,
                cls.OVERFLOW_SHRINK]

    @classmethod
    def valid_typecases(cls):
        return [cls.TYPECASE_DEFAULT,
                cls.TYPECASE_UPCASE,
                cls.TYPECASE_DOWNCASE]

    def _validate_non_negative_float(self, value):
        try:
            float_value = float(value)
        except (TypeError, ValueError):
            return None
        else:
            if float_value >= 0:
                return float_value
            else:
                return None

    def _validate_zero_to_one(self, value, norm=1.0):
        float_value = self._validate_non_negative_float(value)
        if float_value is not None:
            float_value /= norm
            if float_value <= 1.0:
                return float_value
        return None
