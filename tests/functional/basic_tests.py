import logging
import json
from os import path, environ, listdir
from time import sleep
from uuid import uuid4

from geometry_service import create_app

# Setup/Teardown

app = create_app()

def setup_module():
    print(" == Setting up tests for %s"  % (__name__))
    app.config['TESTING'] = True
    print(" == Using database at %s"  % (app.config['SQLALCHEMY_DATABASE_URI']))
    pass

def teardown_module():
    print(" == Tearing down tests for %s"  % (__name__))
    pass

# Tests
dirname = path.dirname(__file__)
csv_sample = path.join(dirname, '..', 'test_data/geo.csv')
geojson_sample = path.join(dirname, '..', 'test_data/geo.json')
shape_zip = path.join(dirname, '..', 'test_data/geo.zip')
shape_gz = path.join(dirname, '..', 'test_data/geo.tar.gz')

def test_get_documentation_1():
    """Functional - Get documentation"""
    with app.test_client() as client:
        res = client.get('/', query_string=dict(), headers=dict())
        assert res.status_code == 200
        r = res.get_json()
        assert not (r.get('openapi') is None)

def test_health_1():
    """Functional - Check health"""
    with app.test_client() as client:
        res = client.get('/health', query_string=dict(), headers=dict())
        assert res.status_code == 200
        r = res.get_json()
        assert r.get('status') == 'OK'

def test_file_source_1():
    """Functional - Test file source: Send file - constructive"""
    with app.test_client() as client:
        data = {
            'resource': (open(geojson_sample, 'rb'), 'geo.json'),
            'response': 'prompt',
            'download': 'true'
        }
        res = client.post('/constructive/centroid', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.is_streamed

def test_file_source_2():
    """Functional - Test file source: From input dir - constructive"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
            'response': 'prompt',
            'download': 'true'
        }
        res = client.post('/constructive/centroid', data=data)
        assert res.status_code == 200
        assert res.is_streamed

def test_file_source_3():
    """Functional - Test file source: Send file - filter"""
    with app.test_client() as client:
        data = {
            'resource': (open(geojson_sample, 'rb'), 'geo.json'),
            'response': 'prompt',
            'download': 'true',
            'wkt': 'POLYGON((47.4 0.5, 50. 1.5, 47.1 1.8, 47.4 0.5))'
        }
        res = client.post('/filter/within', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.is_streamed

def test_file_source_4():
    """Functional - Test file source: From input dir - filter"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
            'response': 'prompt',
            'download': 'true',
            'wkt': 'POLYGON((47.4 0.5, 50. 1.5, 47.1 1.8, 47.4 0.5))'
        }
        res = client.post('/filter/within', data=data)
        assert res.status_code == 200
        assert res.is_streamed

def test_file_source_5():
    """Functional - Test file source: Send both files - join"""
    with app.test_client() as client:
        data = {
            'response': 'prompt',
            'download': 'true',
            'resource': (open(shape_zip, 'rb'), 'geo.tar.gz'),
            'other': (open(geojson_sample, 'rb'), 'geo.json'),
            'rprefix': 'r_'
        }
        res = client.post('/join/intersects', data=data, content_type='multipart/form-data')
        assert res.status_code == 204
        assert res.is_streamed

def test_endpoints_1():
    """Functional - Test endpoints: constructive centroid"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.csv',
            'response': 'prompt',
            'geom': 'WKT',
            'crs': 'EPSG:3857'
        }
        res = client.post('/constructive/centroid', data=data)
        assert res.status_code == 200

def test_endpoints_2():
    """Functional - Test endpoints: constructive convex_hull"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.csv',
            'response': 'prompt',
            'geom': 'WKT',
            'crs': 'EPSG:3857'
        }
        res = client.post('/constructive/convex_hull', data=data)
        assert res.status_code == 200

def test_endpoints_3():
    """Functional - Test endpoints: constructive simplify"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.csv',
            'response': 'prompt',
            'geom': 'WKT',
            'crs': 'EPSG:3857',
            'tolerance': 1.
        }
        res = client.post('/constructive/simplify', data=data)
        assert res.status_code == 200

def test_endpoints_4():
    """Functional - Test endpoints: filter nearest"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
            'response': 'prompt',
            'wkt': 'POLYGON((47.4 0.5, 50. 1.5, 47.1 1.8, 47.4 0.5))'
        }
        res = client.post('/filter/nearest', data=data)
        assert res.status_code == 200

def test_endpoints_4():
    """Functional - Test endpoints: filter within"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
            'response': 'prompt',
            'wkt': 'POLYGON((47.4 0.5, 50. 1.5, 47.1 1.8, 47.4 0.5))'
        }
        res = client.post('/filter/within', data=data)
        assert res.status_code == 200

def test_endpoints_4():
    """Functional - Test endpoints: filter within_buffer"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
            'response': 'prompt',
            'wkt': 'POINT(49. 1)',
            'radius': 0.5
        }
        res = client.post('/filter/within_buffer', data=data)
        assert res.status_code == 200

def test_endpoints_5():
    """Functional - Test endpoints: join contains"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.zip',
            'response': 'prompt',
            'other': 'test_data/geo.tar.gz',
            'rprefix': 'r_'
        }
        res = client.post('/join/contains', data=data)
        assert res.status_code == 200

def test_endpoints_6():
    """Functional - Test endpoints: join within"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.zip',
            'response': 'prompt',
            'other': 'test_data/geo.tar.gz',
            'rprefix': 'r_'
        }
        res = client.post('/join/within', data=data)
        assert res.status_code == 200

def test_endpoints_7():
    """Functional - Test endpoints: join intersects"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.zip',
            'response': 'prompt',
            'other': 'test_data/geo.tar.gz',
            'rprefix': 'r_'
        }
        res = client.post('/join/intersects', data=data)
        assert res.status_code == 200

def test_endpoints_8():
    """Functional - Test endpoints: join dwithin"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.zip',
            'response': 'prompt',
            'other': 'test_data/geo.tar.gz',
            'rprefix': 'r_',
            'distance': 0.1
        }
        res = client.post('/join/dwithin', data=data)
        assert res.status_code == 200

def test_working_path_clean_1():
    """Functional - Test clean of working path: prompt"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
            'response': 'prompt',
        }
        res = client.post('/constructive/centroid', data=data)
        assert len(listdir(path.join(environ['WORKING_DIR'], 'session'))) == 1
    assert len(listdir(path.join(environ['WORKING_DIR'], 'session'))) == 0

def test_working_path_clean_2():
    """Functional - Test clean of working path: deferred"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.json',
        }
        res = client.post('/constructive/centroid', data=data)
        assert len(listdir(path.join(environ['WORKING_DIR'], 'session'))) == 1
    sleep(1)
    assert len(listdir(path.join(environ['WORKING_DIR'], 'session'))) == 0

def test_file_types_1():
    """Functional - Test file types: CSV"""
    with app.test_client() as client:
        data = {
            'resource': (open(csv_sample, 'rb'), 'geo.csv'),
            'crs': 'EPSG:4326',
            'geom': 'WKT',
            'response': 'prompt',
            'download': 'true'
        }
        res = client.post('/constructive/centroid', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.is_streamed

def test_file_types_2():
    """Functional - Test file types: geoJSON"""
    with app.test_client() as client:
        data = {
            'resource': (open(geojson_sample, 'rb'), 'geo.json'),
            'response': 'prompt',
            'download': 'true'
        }
        res = client.post('/constructive/centroid', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.is_streamed

def test_file_types_3():
    """Functional - Test file types: zipped ShapeFile"""
    with app.test_client() as client:
        data = {
            'resource': (open(shape_zip, 'rb'), 'geo.json'),
            'response': 'prompt',
            'download': 'true'
        }
        res = client.post('/constructive/centroid', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.is_streamed

def test_file_types_4():
    """Functional - Test file types: tar.gz ShapeFile"""
    with app.test_client() as client:
        data = {
            'resource': (open(shape_gz, 'rb'), 'geo.json'),
            'response': 'prompt',
            'download': 'true'
        }
        res = client.post('/constructive/centroid', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert res.is_streamed

def test_deferred_1():
    """Functional - Test deferred: constructive"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.csv',
            'geom': 'WKT',
            'crs': 'EPSG:3857',
            'tolerance': 1
        }
        res = client.post('/constructive/simplify', data=data)
        assert res.status_code == 202
        r = res.get_json()
        assert r.get('type') == 'deferred'
        ticket = r.get('ticket')
        assert ticket is not None
        url = r.get('statusUri')
        assert url == "/jobs/status?ticket={ticket}".format(ticket=r['ticket'])
    with app.test_client() as client:
        res = client.get(url)
        assert res.status_code == 200
        r = res.get_json()
        assert r.get('ticket') == ticket
        for attr in ['idempotencyKey', 'requestType', 'initiated', 'executionTime', 'completed', 'success', 'errorMessage', 'resource']:
            assert attr in r
        assert r.get('idempotencyKey') is None
        assert r.get('requestType') == 'constructive.simplify'
        assert r.get('errorMessage') is None

def test_deferred_2():
    """Functional - Test deferred: filter"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.tar.gz',
            'wkt': 'POLYGON((47.4 0.5, 50. 1.5, 47.1 1.8, 47.4 0.5))'
        }
        res = client.post('/filter/within', data=data)
        assert res.status_code == 202
        r = res.get_json()
        assert r.get('type') == 'deferred'
        ticket = r.get('ticket')
        assert ticket is not None
        url = r.get('statusUri')
        assert url == "/jobs/status?ticket={ticket}".format(ticket=r['ticket'])
    with app.test_client() as client:
        res = client.get(url)
        assert res.status_code == 200
        r = res.get_json()
        assert r.get('ticket') == ticket
        for attr in ['idempotencyKey', 'requestType', 'initiated', 'executionTime', 'completed', 'success', 'errorMessage', 'resource']:
            assert attr in r
        assert r.get('idempotencyKey') is None
        assert r.get('requestType') == 'filter.within'
        assert r.get('errorMessage') is None

def test_deferred_3():
    """Functional - Test deferred: join"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.tar.gz',
            'other': 'test_data/geo.zip',
            'wkt': 'POLYGON((47.4 0.5, 50. 1.5, 47.1 1.8, 47.4 0.5))',
            'rsuffix': 'r_'
        }
        res = client.post('/join/intersects', data=data)
        assert res.status_code == 202
        r = res.get_json()
        assert r.get('type') == 'deferred'
        ticket = r.get('ticket')
        assert ticket is not None
        url = r.get('statusUri')
        assert url == "/jobs/status?ticket={ticket}".format(ticket=r['ticket'])
    with app.test_client() as client:
        res = client.get(url)
        assert res.status_code == 200
        r = res.get_json()
        assert r.get('ticket') == ticket
        for attr in ['idempotencyKey', 'requestType', 'initiated', 'executionTime', 'completed', 'success', 'errorMessage', 'resource']:
            assert attr in r
        assert r.get('idempotencyKey') is None
        assert r.get('requestType') == 'join.join_intersects'
        assert r.get('errorMessage') is None

def test_idempotency_key_1():
    """Functional - Test idempotency key"""
    from uuid import uuid4
    key = str(uuid4())
    with app.test_client() as client:
        data = {'resource': 'test_data/geo.tar.gz'}
        res = client.post('/constructive/centroid', data=data, headers={'X-Idempotency-Key': key})
    with app.test_client() as client:
        res = client.get('jobs/status', query_string={'idempotency-key': key})
        assert res.status_code == 200
        r = res.get_json()
        assert r.get('idempotencyKey') == key

def test_full_cycle_1():
    """Functional - Test full cycle"""
    with app.test_client() as client:
        data = {'resource': 'test_data/geo.tar.gz'}
        res = client.post('/constructive/convex_hull', data=data)
        assert res.status_code == 202
        r = res.get_json()
        assert r.get('type') == 'deferred'
        ticket = r.get('ticket')
        assert ticket is not None
        url = r.get('statusUri')
        assert url == "/jobs/status?ticket={ticket}".format(ticket=r['ticket'])
    completed = False
    while not completed:
        with app.test_client() as client:
            res = client.get(url)
            assert res.status_code == 200
            r = res.get_json()
            completed = r.get('completed')
    assert r.get('ticket') == ticket
    for attr in ['idempotencyKey', 'requestType', 'initiated', 'executionTime', 'completed', 'success', 'errorMessage', 'resource']:
        assert attr in r
    assert r.get('idempotencyKey') is None
    assert r.get('requestType') == 'constructive.convex_hull'
    assert r.get('errorMessage') is None
    assert 'link' in r.get('resource')
    assert 'outputPath' in r.get('resource')
    with app.test_client() as client:
        res = client.get(r.get('resource')['link'])
        assert res.status_code == 200
        assert res.is_streamed
    assert path.isfile(path.join(environ['OUTPUT_DIR'], r.get('resource')['outputPath']))

def test_join_with_reprojection_1():
    """Functional - Test join with reprojection"""
    with app.test_client() as client:
        data = {
            'resource': 'test_data/geo.tar.gz',
            'other': 'test_data/geo.csv',
            'other_geom': 'WKT',
            'other_crs': 'EPSG:3857',
            'response': 'prompt',
            'rsuffix': 'r_'
        }
        res = client.post('/join/intersects', data=data)
        assert res.status_code == 200
