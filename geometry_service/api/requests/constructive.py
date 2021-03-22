import os
from flask import Blueprint, make_response, g, request
from werkzeug.utils import secure_filename
from flask_executor import Executor
from geometry_service.database.actions import db_update_queue_status
from geometry_service.loggers import logger
from ..forms.constructive import ConstructiveFileForm, ConstructivePathForm, SimplifyFileForm, SimplifyPathForm
from ..context import get_session
from ..async_ import constructive_process, async_callback
from ..helpers import parse_read_options, send_file, copy_to_output

def _before_requests():
    """Executed before each request for this blueprint.

    Get the request form and session details.

    Returns:
        None|Response: In case of validation error, returns a Flask response, None otherwise.
    """
    logger.info('API request [endpoint: "%s"]', request.endpoint)
    if request.endpoint == 'constructive.simplify':
        form = SimplifyFileForm() if 'resource' in request.files.keys() else SimplifyPathForm()
    else:
        form = ConstructiveFileForm() if 'resource' in request.files.keys() else ConstructivePathForm()
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


def _constructive(action, *args, **kwargs):
    """Prepare for the constructive operation.

    Submits the process, update database and return the api response.

    Arguments:
        action (str): The constructive action.
        *args: Additional arguments for the constructive operation.
        **kwargs: Additional arguments for the constructive operation.

    Returns:
        (str): JSONified flask response depending on the requested response type.
    """
    # Prompt Response
    if g.form.response.data == 'prompt':
        ticket, export, success, error_msg = constructive_process(g.session, g.src_file, action, *args, **kwargs)
        if not success:
            db_update_queue_status(ticket, completed=True, success=False, error_msg=error_msg)
            return make_response({'error': error_msg}, 500)
        if g.form.download.data:
            db_update_queue_status(ticket, completed=True, success=True)
            return send_file(export)

        path = copy_to_output(export, ticket)
        db_update_queue_status(ticket, completed=True, success=True, result=path)
        return make_response({'type': 'prompt', 'path': path}, 200)

    # Deferred Response
    future = executor.submit(constructive_process, g.session, g.src_file, action, *args, **kwargs)
    future.add_done_callback(async_callback)
    ticket = g.session['ticket']
    return make_response({'type': 'deferred', 'ticket': ticket, 'statusUri': "/jobs/status?ticket={ticket}".format(ticket=ticket)}, 202)


# FLASK ROUTES

executor = Executor()
bp = Blueprint('constructive', __name__, url_prefix='/constructive')
bp.before_request(_before_requests)

@bp.route('/centroid', methods=['POST'])
def centroid():
    """**Flask POST rule**.

    Create a new spatial file with geometries constructed by their centroids.
    ---
    post:
        summary: Replace geometries with their centroids.
        description: Create a new spatial file with geometries constructed by their centroids.
        tags:
            - Constructive
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: constructiveForm
                multipart/form-data:
                    schema: constructiveFormMultipart
        responses:
            200: promptResultResponse
            202: deferredResponse
            400: validationErrorResponse
    """
    return _constructive('centroid', **g.parameters)


@bp.route('/convex_hull', methods=['POST'])
def convex_hull():
    """**Flask POST rule**.

    Create a new spatial file with geometries constructed by their convex hull.
    ---
    post:
        summary: Replace geometries with their convex hull.
        description: Create a new spatial file with geometries constructed by their convex hull.
        tags:
            - Constructive
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: constructiveForm
                multipart/form-data:
                    schema: constructiveFormMultipart
        responses:
            200: promptResultResponse
            202: deferredResponse
            400: validationErrorResponse
    """
    return _constructive('convex_hull', **g.parameters)


@bp.route('/simplify', methods=['POST'])
def simplify():
    """**Flask POST rule**.

    Create a new spatial file with simplified geometries.
    ---
    post:
        summary: Simplify geometries.
        description: Create a new spatial file with simplified geometries.
        tags:
            - Constructive
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: simplifyConstructiveForm
                multipart/form-data:
                    schema: simplifyConstructiveFormMultipart
        responses:
            200: promptResultResponse
            202: deferredResponse
            400: validationErrorResponse
    """
    return _constructive('simplify', g.form.tolerance.data, preserve_topology=g.form.preserve_topology.data, **g.parameters)
