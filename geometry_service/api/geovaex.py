import geovaex as gvx
import pygeos as pg
from uuid import uuid4
import os
from geometry_service.exceptions import GeometryNotFound, ResultedEmptyDataFrame

class GeoVaex:
    """Class to interact with geovaex."""

    def __init__(self, path, working_dir, crs=None, read_options={}):
        """Reads spatial file for further processing.

        Arguments:
            path (str): Full path of the spatial file.
            working_dir (str): Full path of the working path.

        Keyword Arguments:
            crs (str): Native CRS of the spatial file (default: {None})
            read_options (dict): Read options for CSV files (default: {{}})
        """
        path = self._extract_file(path, working_dir)
        filename = os.path.splitext(os.path.basename(path))
        extension = filename[1]
        filename = filename[0]
        arrow_file = os.path.join(working_dir, filename + str(uuid4()) + '.arrow')
        self._gdf = gvx.read_file(path, convert=arrow_file, crs=crs, **read_options)
        try:
            self._driver = self._gdf.metadata['driver']
        except AttributeError:
            raise GeometryNotFound('Geometry not recognized.')
        self._filename = filename
        self._extension = extension
        self._working_dir = working_dir


    @property
    def gdf(self):
        """GeoDataFrame"""
        return self._gdf


    def constructive(self, action, *args, **kwargs):
        """Performs a constructive operation and exports to a spatial file.

        Arguments:
            action (str): The constructive operation.
            *args: Additional arguments for the constructive operation.
            **kwargs: Additional keyword arguments for the constructive operation.

        Returns:
            (str): The path of the exported archive.
        """
        gdf = getattr(self._gdf.constructive, action)(*args, **kwargs)
        export = os.path.join(self._working_dir, "{filename}_{action}{extension}".format(filename=self._filename, action=action, extension=self._extension))
        gdf.export(export, driver=self._driver)

        return self._compress_files(export)


    def filter_(self, action, wkt, **kwargs):
        """Performs a filtering predicate operation and export to a spatial file.

        Arguments:
            action (str): The filtering action, one of 'nearest', 'within', 'within_buffer'.
            wkt (str): Well-Known Text representation of the geometry.
            **kwargs: Additional keyword arguments for the filtering operation.

        Returns:
            (str): The path of the exported archive.
        """
        gdf = self._gdf
        if action == 'nearest':
            # k = kwargs.pop('k', 1)
            # maximum_distance = kwargs.pop('maximum_distance', None)
            # if maximum_distance is not None:
            #     buffer = pg.buffer(pg.from_wkt(wkt), maximum_distance)
            #     gdf = gdf[gdf.predicates.within(buffer)]
            distance = gdf.measurement.distance(wkt)
            gdf.add_column('distance', distance, dtype=float)
            gdf = gdf.sort('distance', ascending=False)
        elif action == 'within':
            gdf = gdf[gdf.predicates.within(wkt)]
        elif action == 'within_buffer':
            radius = kwargs.pop('radius', 0)
            buffer = pg.buffer(pg.from_wkt(wkt), radius)
            gdf = gdf[gdf.predicates.within(buffer)]
        else:
            raise ValueError("action could be one of 'nearest', 'within', 'within_buffer'.")
        if len(gdf) == 0:
            raise ResultedEmptyDataFrame("The resulted dataframe is empty.")
        export = os.path.join(self._working_dir, "{filename}_{action}{extension}".format(filename=self._filename, action=action, extension=self._extension))
        gdf.export(export, driver=self._driver)

        return self._compress_files(export)


    def join(self, other, predicate, crs=None, read_options={}, how="left", **kwargs):
        """Perform a spatial join with the 'other' spatial file.

        Arguments:
            other (str): Path of the 'other' spatial file.
            predicate (str): Predicate for the spatial join, one of 'containts', 'within', 'intersects', 'dwithin'.
            **kwargs: Additional keyword arguments for the spatial join.

        Keyword Arguments:
            crs (str): Native CRS for the other spatial file (default: {None})
            read_options (dict): Read options in case the 'other' file is CSV (default: {{}})
            how (str): how to join, 'left' keeps all rows on the left, and adds columns (with possible missing values) 'right' is similar with self and other swapped. 'inner' will only return rows which overlap. (default: {"left"})

        Returns:
            (str) The path of the exported archive.
        """
        gdf = self._gdf
        other = GeoVaex(other, self._working_dir, crs=crs, read_options=read_options).gdf
        distance = kwargs.pop('distance', None)
        gdf = gdf.sjoin(other, how=how, op=predicate, distance=distance, allow_duplication=True, **kwargs)
        if len(gdf) == 0:
            raise ResultedEmptyDataFrame("The resulted dataframe is empty.")
        export = os.path.join(self._working_dir, "{filename}_sjoin_{predicate}{extension}".format(filename=self._filename, predicate=predicate, extension=self._extension))
        gdf.export(export, driver=self._driver)

        return self._compress_files(export)


    def _extract_file(self, file, extraction_dir):
        """Extracts a compressed archive.

        It extracts zipped and tar files. In case the file is neither of them, it returns the same file.

        Arguments:
            file (str): The full path of the file.
            extraction_dir (str): The path where the archive will be extracted.

        Returns:
            (str): The path of the extracted folder, or the initial file if it was not compressed.
        """
        import zipfile
        import tarfile
        path, filename = os.path.split(file)
        if tarfile.is_tarfile(file):
            handle = tarfile.open(file)
            file = os.path.join(extraction_dir, os.path.splitext(filename)[0])
            handle.extractall(file)
            handle.close()
        elif zipfile.is_zipfile(file):
            tgt = os.path.join(extraction_dir, os.path.splitext(filename)[0])
            with zipfile.ZipFile(file, 'r') as handle:
                handle.extractall(tgt)
            file = tgt
        return file


    def _compress_files(self, path):
        """Compress files to tar.gz

        All the files contained in a folder will be added to the archive.

        Arguments:
            path (str): The full path of the folder containing the files that will be added to the archive.

        Returns:
            (str): The archived file.
        """
        import tarfile
        if os.path.isdir(path):
            result = path + '.tar.gz'
            with tarfile.open(result, "w:gz") as tar:
                for file in os.listdir(path):
                    tar.add(os.path.join(path, file), arcname=file)
        else:
            result = path + '.gz'
            with tarfile.open(result, "w:gz") as tar:
                tar.add(path, arcname=os.path.basename(path))

        return result
