from .geovaex import GeoVaex
from shutil import rmtree
import os
from geometry_service.database.actions import db_update_queue_status
from geometry_service.exceptions import ResultedEmptyDataFrame
from .helpers import copy_to_output

def async_callback(future):
    """Generic callback for asynchronous operations.

    Updates database with the results.

    Arguments:
        future (obj): Future object.
    """
    ticket, file, success, error_msg = future.result()
    path = None
    if success:
        path = copy_to_output(file, ticket)
    try:
        rmtree(os.path.dirname(file))
    except:
        pass
    db_update_queue_status(ticket, completed=True, success=success, error_msg=error_msg, result=path)


def constructive_process(session, file, action, *args, **kwargs):
    """Wrapper function for the constuctive process.

    Arguments:
        session (dict): Dictionary with session information.
        file (str): The full path of the source file.
        action (str): The constructive operation.
        *args: Additional arguments for the constructive operation.
        **kwargs: Additional keyword arguments for the constructive operation.

    Returns:
        (tuple):
            - (str): Request ticket.
            - (str): Full path of the resulted file(s).
            - (bool): Whether operation succeeded.
            - (str): Error message in case of failure.
    """
    try:
        crs = kwargs.pop('crs', None)
        read_options = kwargs.pop('read_options', {})
        geovaex = GeoVaex(file, session['working_path'], crs=crs, read_options=read_options)
        export = geovaex.constructive(action, *args, **kwargs)
    except Exception as e:
        return (session['ticket'], None, False, str(e))

    return (session['ticket'], export, True, None)


def filter_process(session, file, action, wkt, **kwargs):
    """Wrapper function for the filtering process.

    Arguments:
        session (dict): Dictionary with session information.
        file (str): The full path of the source file.
        action (str): The filtering operation.
        wkt (str): Well-Known Text of the input geometry.
        **kwargs: Additional keyword arguments for the filtering operation.

    Returns:
        (tuple):
            - (str): Request ticket.
            - (str): Full path of the resulted file(s).
            - (bool): Whether operation succeeded.
            - (str): Error message in case of failure.
    """
    try:
        crs = kwargs.pop('crs', None)
        read_options = kwargs.pop('read_options', {})
        geovaex = GeoVaex(file, session['working_path'], crs=crs, read_options=read_options)
        export = geovaex.filter_(action, wkt, **kwargs)
    except ResultedEmptyDataFrame as e:
        return (session['ticket'], None, True, str(e))
    except Exception as e:
        return (session['ticket'], None, False, str(e))

    return (session['ticket'], export, True, None)


def join_process(session, left, right, predicate, **kwargs):
    """Wrapper function for spatial join.

    Arguments:
        session (dict): Dictionary with session information.
        left (str): The full path of the left file.
        right (str): The full path of the right file.
        predicate (str): The spatial join predicate.
        **kwargs: Additional keyword arguments for the filtering operation.

    Returns:
        (tuple):
            - (str): Request ticket.
            - (str): Full path of the resulted file(s).
            - (bool): Whether operation succeeded.
            - (str): Error message in case of failure.
    """
    try:
        crs = kwargs.pop('left_crs', None)
        read_options = kwargs.pop('left_read_options', {})
        geovaex = GeoVaex(left, session['working_path'], crs=crs, read_options=read_options)
        right_crs = kwargs.pop('right_crs', None)
        right_read_options = kwargs.pop('right_read_options', {})
        export = geovaex.join(right, predicate, crs=right_crs, read_options=right_read_options, **kwargs)
    except ResultedEmptyDataFrame as e:
        return (session['ticket'], None, True, str(e))
    except Exception as e:
        return (session['ticket'], None, False, str(e))

    return (session['ticket'], export, True, None)
