from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, FloatField, BooleanField
from wtforms.validators import Optional, Length, DataRequired, AnyOf
from .validators import CRS, Encoding
from . import BaseForm

class JoinForm(BaseForm):
    """Base form for join requests.

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
    other_delimiter = StringField('other_delimiter', default=',', validators=[Optional(), Length(min=1, max=2)])
    other_lat = StringField('other_lat', validators=[Optional()])
    other_lon = StringField('other_lon', validators=[Optional()])
    other_geom = StringField('other_geom', validators=[Optional()])
    other_crs = StringField('other_crs', validators=[Optional(), CRS()])
    other_encoding = StringField('other_encoding', validators=[Optional(), Encoding()])
    how = StringField('how', default="inner", validators=[Optional(), AnyOf(["left", "right", "inner"])])
    lprefix = StringField('lprefix', validators=[Optional()])
    rprefix = StringField('rprefix', validators=[Optional()])
    lsuffix = StringField('lsuffix', validators=[Optional()])
    rsuffix = StringField('rsuffix', validators=[Optional()])


class JoinFileForm(JoinForm):
    """Generic form for join requests with both assets as files.

    Extends:
        JoinForm
    """
    resource = FileField('resource', validators=[FileRequired()])
    other = FileField('other', validators=[FileRequired()])

class JoinResourceFileForm(JoinForm):
    """Generic form for join requests with main asset as file and the other as path.

    Extends:
        JoinForm
    """
    resource = FileField('resource', validators=[FileRequired()])
    other = StringField('other', validators=[DataRequired()])

class JoinOtherFileForm(JoinForm):
    """Generic form for join requests with main asset as path and the other as file.

    Extends:
        JoinForm
    """
    resource = StringField('resource', validators=[DataRequired()])
    other = FileField('other', validators=[FileRequired()])

class JoinPathForm(JoinForm):
    """Generic form for join requests with both assets as paths.

    Extends:
        JoinForm
    """
    resource = StringField('resource', validators=[DataRequired()])
    other = StringField('other', validators=[DataRequired()])

class JoinDWithinFileForm(JoinFileForm):
    """Form for dwithin join requests with both assets as files.

    Extends:
        JoinFileForm
    """
    distance = FloatField('distance', validators=[DataRequired()])

class JoinDWithinResourceFileForm(JoinResourceFileForm):
    """Form for dwithin join requests with main asset as file and the other as path.

    Extends:
        JoinResourceFileForm
    """
    distance = FloatField('distance', validators=[DataRequired()])

class JoinDWithinOtherFileForm(JoinOtherFileForm):
    """Form for dwithin join requests with main asset as path and the other as file.

    Extends:
        JoinOtherFileForm
    """
    distance = FloatField('distance', validators=[DataRequired()])

class JoinDWithinPathForm(JoinPathForm):
    """Form for dwithin join requests with both assets as paths.

    Extends:
        JoinPathForm
    """
    distance = FloatField('distance', validators=[DataRequired()])
