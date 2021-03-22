import os
from flask import Blueprint, make_response, g, request
from werkzeug.utils import secure_filename
from flask_executor import Executor
from geometry_service.database.actions import db_update_queue_status
from geometry_service.loggers import logger
from ..forms.join import JoinFileForm, JoinPathForm, JoinDWithinFileForm, JoinDWithinPathForm
from ..context import get_session
from ..async_ import join_process, async_callback
from ..helpers import parse_read_options, send_file, copy_to_output

def _before_requests():
    """Executed before each request for this blueprint.

    Get the request form and session details.

    Returns:
        None|Response: In case of validation error, returns a Flask response, None otherwise.
    """
    logger.info('API request [endpoint: "%s"]', request.endpoint)
    file_keys = request.files.keys()
    if 'resource' in file_keys and 'other' in file_keys:
        form = JoinDWithinFileForm() if request.endpoint == 'join.join_dwithin' else JoinFileForm()
    elif 'resource' in file_keys:
        form = JoinDWithinResourceFileForm() if request.endpoint == 'join.join_dwithin' else JoinResourceFileForm()
    elif 'other' in file_keys:
        form = JoinDWithinOtherFileForm() if request.endpoint == 'join.join_dwithin' else JoinOtherFileForm()
    else:
        form = JoinDWithinPathForm() if request.endpoint == 'join.join_dwithin' else JoinPathForm()
    if not form.validate_on_submit():
        return make_response(form.errors, 400)

    session = get_session()

    if 'resource' in request.files.keys():
        left_filename = secure_filename(form.resource.data.filename)
        left_file = os.path.join(session['working_path'], left_filename)
        form.resource.data.save(left_file)
    else:
        left_file = os.path.join(os.environ['INPUT_DIR'], form.resource.data)

    if 'other' in request.files.keys():
        right_filename = secure_filename(form.other.data.filename)
        right_file = os.path.join(session['working_path'], right_filename)
        form.other.data.save(right_file)
    else:
        right_file = os.path.join(os.environ['INPUT_DIR'], form.other.data)

    g.left_file = left_file
    g.right_file = right_file
    g.form = form
    g.session = session

    left_read_options = parse_read_options(form)
    left_crs = form.crs.data if form.crs.data != '' else None
    right_read_options = parse_read_options(form, prefix="other_")
    right_crs = form.other_crs.data if form.other_crs.data != '' else None
    g.parameters = {'left_crs': left_crs, 'left_read_options': left_read_options, 'right_crs': right_crs, 'right_read_options': right_read_options}


def _join(predicate, **kwargs):
    """Prepare for the join operation.

    Submits the process, update database and return the api response.

    Arguments:
        predicate (str): The spatial join predicate.
        **kwargs: Additional arguments for the spatial join.

    Returns:
        (str): JSONified flask response depending on the requested response type.
    """
    column_fix = {}
    for fix in ['lprefix', 'rprefix', 'lsuffix', 'rsuffix']:
        value = getattr(g.form, fix).data
        if value != '':
            column_fix[fix] = value
    # Prompt Response
    if g.form.response.data == 'prompt':
        ticket, export, success, error_msg = join_process(g.session, g.left_file, g.right_file, predicate, how=g.form.how.data, **column_fix, **kwargs)
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
    future = executor.submit(join_process, g.session, g.left_file, g.right_file, predicate, how=g.form.how.data, **column_fix, **kwargs)
    future.add_done_callback(async_callback)
    ticket = g.session['ticket']
    return make_response({'type': 'deferred', 'ticket': ticket, 'statusUri': "/jobs/status?ticket={ticket}".format(ticket=ticket)}, 202)


# FLASK ROUTES

executor = Executor()
bp = Blueprint('join', __name__, url_prefix='/join')
bp.before_request(_before_requests)

@bp.route('/contains', methods=['POST'])
def join_contains():
    """**Flask POST rule.**

    Spatial join on two spatial files drived by contains relationship.
    ---
    post:
        summary: Spatial join on two spatial files drived by contains relationship.
        description: Create a new spatial file on the condition that the geometry of the **other** dataset is completely inside the geometry of the **resource**. The new file contains attributes from both datasets, prefixed and suffixed according to the given parameters, and geometry from the *resource* dataset.
        tags:
            - Join
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: joinForm
                multipart/form-data:
                    schema:
                        oneOf:
                            - $ref: "#/components/schemas/joinFormMultipartBoth"
                            - $ref: "#/components/schemas/joinFormMultipartResource"
                            - $ref: "#/components/schemas/joinFormMultipartOther"
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _join('contains', **g.parameters)

@bp.route('/within', methods=['POST'])
def join_within():
    """**Flask POST rule.**

    Spatial join on two spatial files drived by within relationship.
    ---
    post:
        summary: Spatial join on two spatial files drived by within relationship.
        description: Create a new spatial file on the condition that the geometry of the **resource** dataset is completely inside the geometry of the **other**. The new file contains attributes from both datasets, prefixed and suffixed according to the given parameters, and geometry from the *resource* dataset.
        tags:
            - Join
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: joinForm
                multipart/form-data:
                    schema:
                        oneOf:
                            - $ref: "#/components/schemas/joinFormMultipartBoth"
                            - $ref: "#/components/schemas/joinFormMultipartResource"
                            - $ref: "#/components/schemas/joinFormMultipartOther"
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _join('within', **g.parameters)

@bp.route('/intersects', methods=['POST'])
def join_intersects():
    """**Flask POST rule.**

    Spatial join on two spatial files drived by intersects relationship.
    ---
    post:
        summary: Spatial join on two spatial files drived by intersects relationship.
        description: Create a new spatial file on the condition that the two geometries intersect. The new file contains attributes from both datasets, prefixed and suffixed according to the given parameters, and geometry from the *resource* dataset.
        tags:
            - Join
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: joinForm
                multipart/form-data:
                    schema:
                        oneOf:
                            - $ref: "#/components/schemas/joinFormMultipartBoth"
                            - $ref: "#/components/schemas/joinFormMultipartResource"
                            - $ref: "#/components/schemas/joinFormMultipartOther"
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _join('intersects', **g.parameters)

@bp.route('/dwithin', methods=['POST'])
def join_dwithin():
    """**Flask POST rule.**

    Spatial join on two spatial files drived by within distance relationship.
    ---
    post:
        summary: Spatial join on two spatial files drived by within distance relationship.
        description: Create a new spatial file on the condition that the two geometries are within the given distance. The new file contains attributes from both datasets, prefixed and suffixed according to the given parameters, and geometry from the *resource* dataset.
        tags:
            - Join
        parameters:
            - idempotencyKey
        requestBody:
            required: true
            content:
                application/x-www-form-urlencoded:
                    schema: dwithinJoinForm
                multipart/form-data:
                    schema:
                        oneOf:
                            - $ref: "#/components/schemas/dwithinJoinFormMultipartBoth"
                            - $ref: "#/components/schemas/dwithinJoinFormMultipartResource"
                            - $ref: "#/components/schemas/dwithinJoinFormMultipartOther"
        responses:
            200: promptResultResponse
            202: deferredResponse
            204: noContentResponse
            400: validationErrorResponse
    """
    return _join('dwithin', distance=g.form.distance.data, **g.parameters)
