import logging
import json
import os
from shutil import rmtree

# Setup/Teardown
def setup_module():
    print(" == Setting up tests for %s"  % (__name__))
    pass

def teardown_module():
    print(" == Tearing down tests for %s"  % (__name__))
    pass

# Tests

def test_validators_1():
    """Unit - Test CRS form validator"""
    from wtforms.validators import ValidationError
    from geometry_service.api.forms.validators import CRS
    class Field:
        def __init__(self, data):
            self.data = data
    message = 'Test message'
    validator = CRS(message)
    try:
        validator(None, Field('wrongcrs'))
    except Exception as e:
        exc = e
    assert 'exc' in locals()
    assert isinstance(exc, ValidationError)
    assert str(exc) == message
    validator(None, Field('EPSG:4326'))

def test_validators_2():
    """Unit - Test Encoding form validator"""
    from wtforms.validators import ValidationError
    from geometry_service.api.forms.validators import Encoding
    class Field:
        def __init__(self, data):
            self.data = data
    message = 'Test message'
    validator = Encoding(message)
    try:
        validator(None, Field('utf-1'))
    except Exception as e:
        exc = e
    assert 'exc' in locals()
    assert isinstance(exc, ValidationError)
    assert str(exc) == message
    validator(None, Field('utf-8'))

def test_validators_3():
    """Unit - Test WKT form validator"""
    from wtforms.validators import ValidationError
    from geometry_service.api.forms.validators import WKT
    class Field:
        def __init__(self, data):
            self.data = data
    message = 'Test message'
    validator = WKT(message)
    try:
        validator(None, Field('wrongwkt'))
    except Exception as e:
        exc = e
    assert 'exc' in locals()
    assert isinstance(exc, ValidationError)
    assert str(exc) == message
    validator(None, Field('POINT(24. 37)'))

def test_geovaex_1():
    """Unit - Test geovaex open file"""
    from geometry_service.api.geovaex import GeoVaex
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(path, 'test_data', 'geo.tar.gz')
    working_path = os.path.join(os.environ['WORKING_DIR'], 'session', 'abc')
    os.makedirs(working_path, exist_ok=True)
    gvx = GeoVaex(path, working_path)
    assert len(gvx.gdf) == 3
    assert gvx.gdf.geometry.crs.to_epsg() == 4326
    rmtree(working_path)
