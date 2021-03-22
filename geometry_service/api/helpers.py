import os
from geometry_service.loggers import logger


def parse_read_options(form, prefix=''):
    """Extract read options from form data.

    Arguments:
        form (obj): Form object

    Keyword Arguments:
        prefix (str): prefix for the form fields (default: {''})

    Returns:
        (dict): Read options key - value dictionary.
    """
    read_options = {
        'encoding': getattr(form, prefix+'encoding').data,
        'delimiter': getattr(form, prefix+'delimiter').data,
    }
    geom = getattr(form, prefix+'geom')
    lat = getattr(form, prefix+'lat')
    lon = getattr(form, prefix+'lon')
    if geom.data != '':
        read_options['geom'] = geom.data
    elif lat.data != '' and lon.data != '':
        read_options['lat'] = lat.data
        read_options['lon'] = lon.data
    return read_options


def send_file(file):
    """Create a send file response.

    Arguments:
        file (str): Path of the file.

    Returns:
        (obj): Flask response
    """
    from flask import send_file as flask_send_file
    file_content = open(file, 'rb')
    filename = os.path.basename(file)
    response = flask_send_file(file_content, attachment_filename=filename, as_attachment=True)
    response.headers['Content-Length'] = str(os.path.getsize(file))
    return response

def copy_to_output(file, ticket):
    """Copy file to output dir, after creating the containing path.

    Arguments:
        file (str): Path of the file.
        ticket (str): Request ticket.

    Returns:
        (str): Relative to output dir path of the copied file.
    """
    from datetime import datetime
    from shutil import copyfile
    filename = os.path.basename(file)
    output_path = os.path.join(datetime.now().strftime("%y%m"),ticket)
    output_file = os.path.join(output_path, filename)
    full_output = os.path.join(os.environ['OUTPUT_DIR'], output_path)
    os.makedirs(full_output, exist_ok=True)
    copyfile(file, os.path.join(full_output, filename))
    return output_file
