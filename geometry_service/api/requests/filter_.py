import os
from flask import Blueprint, make_response, g, request
from werkzeug.utils import secure_filename
from flask_executor import Executor
from geometry_service.database.actions import db_update_queue_status
from geometry_service.loggers import logger
from ..forms.filter_ import FilterFileForm, FilterPathForm, BufferFileForm, BufferPathForm
from ..context import get_session
from ..async_ import filter_process, async_callback
from ..helpers import parse_read_options, send_file, copy_to_output

def _before_requests():
    """Executed before each request for this blueprint.

    Get the request form and session details.

    Returns:
        None|Response: In case of validation error, returns a Flask response, None otherwise.
    """
    logger.info('API request [endpoint: "%s"]', request.endpoint)
    if request.endpoint == 'filter.within_buffer':
        form = BufferFileForm() if 'resource' in request.files.keys() else BufferPathForm()
    else:
        form = FilterFileForm() if 'resource' in request.files.keys() else FilterPathForm()
    if not form.validate_on_submit():
        return make_response(form.errors, 400)

    session = get_session()

    if 'resource' in request.files.keys():
        src_filename = secure_filename(form.resource.data.filename)
        src_file = os.path.join(session['working_path'], src_filename)
        form.resource.data.save(src_file)
    else:
        src_file = os.path.join(os.environ['INPUT_DIR'], form.resource.data)
    g.src_file = src_file
    g.form = form
    g.session = session

    read_options = parse_read_options(form)
    crs = form.crs.data if form.crs.data != '' else None
    g.parameters = {'crs': crs, 'read_options': read_options}


def _filter(action, **kwargs):
    """Prepare for the filtering operation.

    Submits the process, update database and return the api response.

    Arguments:
        action (str): The filtering action.
        **kwargs: Additional arguments for the filtering operation.

    Returns:
        (str): JSONified flask response depending on the requested response type.
    """
    # Prompt Response
    if g.form.response.data == 'prompt':
        ticket, export, success, error_msg = filter_process(g.session, g.src_file, action, g.form.wkt.data, **kwargs)
        if not success:
            db_update_queue_status(g.session['ticket'], completed=True, success=False, error_msg=error_msg)
            return make_response({'error': error_msg}, 500)
        elif export is None:
            return make_response({}, 204)
        if g.form.download.data:
            db_update_queue_status(ticket, completed=True, success=True)
            return send_file(export)

        path = copy_to_output(export, ticket)
        db_update_queue_status(ticket, completed=True, success=True, result=path)
        return make_response({'type': 'prompt', 'path': path}, 200)

    # Deferred Response
    future = executor.submit(filter_process, g.session, g.src_file, action, g.form.wkt.data, **kwargs)
    future.add_done_callback(async_callback)
    ticket = g.session['ticket']
    return make_response({'type': 'deferred', 'ticket': ticket, 'statusUri': "/jobs/status?ticket={ticket}".format(ticket=ticket)}, 202)


# FLASK ROUTES

executor = Executor()
bp = Blueprint('filter', __name__, url_prefix='/filter')
bp.before_request(_before_requests)

@bp.route('/nearest', methods=['POST'])
def nearest():
    """**Flask POST rule.**

    Create a new spatial file sorted by the nearest geometries.
    ---
    post:
        summary: Find the nearest geometries.
        description: Create a new spatial file sorted by the nearest geometries. A new column *distance* is added to the attribute table with the distance specified in the CRS units.
        tags:
            - Filter
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: filterForm
                multipart/form-data:
                    schema: filterFormMultipart
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _filter('nearest', **g.parameters)

@bp.route('/within', methods=['POST'])
def within():
    """**Flask POST rule.**

    Create a new spatial file, subset of the source, with the condition that each feature in this dataset is completely inside the given geometry.
    ---
    post:
        summary: Apply a within filter on the spatial file.
        description: Create a new spatial file, subset of the source, with the condition that each feature in this dataset is completely inside the given geometry.
        tags:
            - Filter
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: filterForm
                multipart/form-data:
                    schema: filterFormMultipart
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _filter('within', **g.parameters)

@bp.route('/within_buffer', methods=['POST'])
def within_buffer():
    """**Flask POST rule.**

    Create a new spatial file, subset of the source, with the condition that each feature in this dataset is within a given radius from the given geometry.
    ---
    post:
        summary: Apply a within buffer filter.
        description: Create a new spatial file, subset of the source, with the condition that each feature in this dataset is within a given radius from the given geometry.
        tags:
            - Filter
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: bufferFilterForm
                multipart/form-data:
                    schema: bufferFilterFormMultipart
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _filter('within_buffer', radius=g.form.radius.data, **g.parameters)