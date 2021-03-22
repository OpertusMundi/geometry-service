from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, FloatField, BooleanField
from wtforms.validators import Optional, Length, DataRequired, AnyOf
from .validators import CRS, Encoding
from . import BaseForm

class ConstructiveForm(BaseForm):
    """Base form for constructive requests.

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

class ConstructiveFileForm(ConstructiveForm):
    """Generic form for constructive requests with file resource.

    Extends:
        ConstructiveForm
    """
    resource = FileField('resource', validators=[FileRequired()])

class ConstructivePathForm(ConstructiveForm):
    """Generic form for constructive requests with resource as path.

    Extends:
        ConstructiveForm
    """
    resource = StringField('resource', validators=[DataRequired()])

class SimplifyFileForm(ConstructiveFileForm):
    """Form for simplify constructive requests with file resource.

    Extends:
        ConstructiveFileForm
    """
    tolerance = FloatField('tolerance', validators=[DataRequired()])
    preserve_topology = BooleanField('preserve_topology', default=False, validators=[Optional()])

class SimplifyPathForm(ConstructivePathForm):
    """Form for simplify constructive requests with resource as path.

    Extends:
        ConstructiveFileForm
    """
    tolerance = FloatField('tolerance', validators=[DataRequired()])
    preserve_topology = BooleanField('preserve_topology', default=False, validators=[Optional()])
