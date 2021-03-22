class DBItemNotFound(Exception):
    """Raised when an item not found on update."""

class GeometryNotFound(Exception):
	"""Raise when the geometry is not recognized in a file."""

class ResultedEmptyDataFrame(Exception):
	"""Raise when the resulted dataframe is empty."""