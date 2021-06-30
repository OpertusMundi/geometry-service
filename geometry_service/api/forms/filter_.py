from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, FloatField, BooleanField
from wtforms.validators import Optional, Length, DataRequired, AnyOf, NumberRange
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

class FilterFileForm(FilterForm):
    """Generic form for filter requests with file resource.

    Extends:
        FilterForm
    """
    resource = FileField('resource', validators=[FileRequired()])
    wkt = StringField('wkt', validators=[DataRequired(), WKT()])

class FilterPathForm(FilterForm):
    """Generic form for filter requests with resource as path.

    Extends:
        FilterForm
    """
    resource = StringField('resource', validators=[DataRequired()])
    wkt = StringField('wkt', validators=[DataRequired(), WKT()])

class BufferFileForm(FilterFileForm):
    """Form for within buffer filter requests with file resource.

    Extends:
        FilterFileForm
    """
    radius = FloatField('radius', validators=[DataRequired()])
    wkt = StringField('wkt', validators=[DataRequired(), WKT()])

class BufferPathForm(FilterPathForm):
    """Form for within buffer filter requests with resource as path.

    Extends:
        FilterPathForm
    """
    radius = FloatField('radius', validators=[DataRequired()])
    wkt = StringField('wkt', validators=[DataRequired(), WKT()])

class TravelDistanceFileForm(FilterForm):
    resource = FileField('resource', validators=[FileRequired()])
    distance = FloatField('distance', validators=[DataRequired(), NumberRange(min=0, max=200.0)])
    point_lat = FloatField('point_lat', validators=[DataRequired()])
    point_lon = FloatField('point_lon', validators=[DataRequired()])
    costing = StringField('costing', default="auto", validators=[Optional(), AnyOf(['auto', 'bicycle', 'pedestrian', 'bikeshare', 'bus'])])

class TravelDistancePathForm(FilterForm):
    resource = StringField('resource', validators=[DataRequired()])
    distance = FloatField('distance', validators=[DataRequired(), NumberRange(min=0, max=200.0)])
    point_lat = FloatField('point_lat', validators=[DataRequired()])
    point_lon = FloatField('point_lon', validators=[DataRequired()])
    costing = StringField('costing', default="auto", validators=[Optional(), AnyOf(['auto', 'bicycle', 'pedestrian', 'bikeshare', 'bus'])])

class TravelTimeFileForm(FilterForm):
    resource = FileField('resource', validators=[FileRequired()])
    time = FloatField('time', validators=[DataRequired(), NumberRange(min=0, max=120)])
    point_lat = FloatField('point_lat', validators=[DataRequired()])
    point_lon = FloatField('point_lon', validators=[DataRequired()])
    costing = StringField('costing', default="auto", validators=[Optional(), AnyOf(['auto', 'bicycle', 'pedestrian', 'bikeshare', 'bus'])])

class TravelTimePathForm(FilterForm):
    resource = StringField('resource', validators=[DataRequired()])
    time = FloatField('time', validators=[DataRequired(), NumberRange(min=0, max=120)])
    point_lat = FloatField('point_lat', validators=[DataRequired()])
    point_lon = FloatField('point_lon', validators=[DataRequired()])
    costing = StringField('costing', default="auto", validators=[Optional(), AnyOf(['auto', 'bicycle', 'pedestrian', 'bikeshare', 'bus'])])
