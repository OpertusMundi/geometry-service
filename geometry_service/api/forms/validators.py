"""A collection of custom WTForms Validators."""

from wtforms.validators import ValidationError

class CRS(object):
    """Validates CRS fields."""
    def __init__(self, message=None):
        if not message:
            message = 'Field must be a valid CRS.'
        self.message = message

    def __call__(self, form, field):
        import pyproj
        from pyproj.exceptions import CRSError
        try:
            pyproj.crs.CRS.from_user_input(field.data)
        except CRSError:
            raise ValidationError(self.message)


class Encoding(object):
    """Validates an encoding field."""
    def __init__(self, message=None):
        if not message:
            message = 'Field must be a valid encoding.'
        self.message = message

    def __call__(self, form, field):
        try:
            ''.encode(encoding=field.data, errors='replace')
        except LookupError:
            raise ValidationError(self.message)


class WKT(object):
    """Validates a Well-Known-Text geometry field."""
    def __init__(self, message=None):
        if not message:
            message = 'Field must be a valid Well-Known-Text geometry.'
        self.message = message

    def __call__(self, form, field):
        from pygeos import from_wkt, GEOSException
        try:
            from_wkt(field.data)
        except GEOSException:
            raise ValidationError(self.message)
