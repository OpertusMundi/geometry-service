"""Common Flask context functions, shared among blueprints."""
from flask import request
import os
from geometry_service.loggers import logger
from geometry_service.database.actions import db_queue

def get_session():
    """Prepares session.

    Returns:
        (dict): Dictionary with session info.
    """

    idempotency_key = request.headers.get('X-Idempotency-Key')
    queue = db_queue(idempotency_key=idempotency_key, request=request.endpoint)

    working_path = os.path.join(os.environ['WORKING_DIR'], 'session', queue['ticket'])
    os.makedirs(working_path, exist_ok=True)

    session = {'ticket': queue['ticket'], 'working_path': working_path, 'idempotency_key': idempotency_key}

    return session
