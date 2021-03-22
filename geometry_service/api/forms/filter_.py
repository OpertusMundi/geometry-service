from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, FloatField, BooleanField
from wtforms.validators import Optional, Length, DataRequired, AnyOf
from .validators import CRS, Encoding, WKT
from . import BaseForm

class FilterForm(BaseForm):
    """Base form for filter requests.

    Extends:
        BaseForm
    """
    response = StringField('response', default='deferred', validators=[Optional(), AnyOf(['prompt', 'deferred'])])
    download = BooleanField('download', default=True, validators=[Optional()])
    delimiter = StringField('delimiter', default=',', validators=[Optional(), Length(min=1, max=2)])
    lat = StringField('lat', validators=[Optional()])
    lon = StringField('lon', validators=[Optional()])
    geom = StringField('geom', validators=[Optional()])
    crs = StringField('crs', validators=[Optional(), CRS()])
    encoding = StringField('encoding', validators=[Optional(), Encoding()])
    wkt = StringField('wkt', validators=[DataRequired(), WKT()])

class FilterFileForm(FilterForm):
    """Generic form for filter requests with file resource.

    Extends:
        FilterForm
    """
    resource = FileField('resource', validators=[FileRequired()])

class FilterPathForm(FilterForm):
    """Generic form for filter requests with resource as path.

    Extends:
        FilterForm
    """
    resource = StringField('resource', validators=[DataRequired()])

class BufferFileForm(FilterFileForm):
    """Form for within buffer filter requests with file resource.

    Extends:
        FilterFileForm
    """
    radius = FloatField('radius', validators=[DataRequired()])

class BufferPathForm(FilterPathForm):
    """Form for within buffer filter requests with resource as path.

    Extends:
        FilterPathForm
    """
    radius = FloatField('radius', validators=[DataRequired()])
