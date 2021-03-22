# Geometry-Service

## Description

The *geometry service* offers the ability to apply geometric operations on one or more spatial files, using **geoVaex**. Following the upload of a spatial file, the requested geometric operation generates, promptly or asynchronously, a new spatial file available for download. Depending on the operation, the generated file could

- contain new geometries (**constructive** operations) constructed from the original ones,
- be a filtered subset of the initial file (**filter** operations), or
- be a result of a spatial join (**join** operations) of two files.

## Installation

### Dependencies

* Python 3.8
* Running instance of a database
* [GEOS library](https://github.com/libgeos/geos)
* [PROJ 7](https://proj.org)
* [GDAL 3.1](https://gdal.org/download.html#binaries)
* [Apache Arrow binaries](https://github.com/apache/arrow)
* [PCRE development files](https://www.pcre.org)

### Install package

Install `geovaed`:
```
pip install git+https://github.com/OpertusMundi/geovaex
```
Install service with pip:
```
pip install git+https://github.com/OpertusMundi/geometry-service.git
```
Install separately the Python required packages:
```
pip install -r requirements.txt -r requirements-production.txt
```
### Set environment

The following environment variables should be set:
* `FLASK_ENV`<sup>*</sup>: `development` or `production`.
* `FLASK_APP`<sup>*</sup>: `geometry_service` (if running as a container, this will be always set).
* `SECRET_KEY`<sup>*</sup>: The application secret key.
* `DATABASE_URI`<sup>*</sup>: `engine://user:pass@host:port/database`
* `WORKING_DIR` : The location for storing the session files (*default*: the system temporary path).
* `OUTPUT_DIR`<sup>*</sup>: The location used to store exported files.
* `INPUT_DIR`<sup>*</sup>: The location of the input files.
* `CORS`: List or string of allowed origins (*default*: '*').
* `LOGGING_CONFIG_FILE`<sup>*</sup>: The logging configuration file.

<sup>*</sup> Required.

### Database

A database should have been created in a DataBase server.

Initialize the database, running:
```
flask init-db
```

## Usage

For details about using the service API, you can browse the full [OpenAPI documentation](https://opertusmundi.github.io/geometry-service/).

## Build and run as a container

Copy `.env.example` to `.env` and configure (e.g `FLASK_ENV` variable).

Copy `compose.yml.example` to `compose.yml` (or `docker-compose.yml`) and adjust to your needs (e.g. specify volume source locations etc.).

Build:

    docker-compose -f compose.yml build

Prepare the following files/directories:

   * `./secrets/secret_key`: file needed (by Flask) for signing/encrypting session data.
   * `./secrets/postgres/password`: file containing the password for the PostGIS database user.
   * `./logs`: a directory to keep logs.
   * `./temp`: a directory to be used as temporary storage.
   * `./output`: a directory to be used to store exported files.
   * `./input`: a directory where input files are read from.

Start application:

    docker-compose -f compose.yml up


## Run tests

Copy `compose-testing.yml.example` to `compose-testing.yml` and adjust to your needs. This is a just a docker-compose recipe for setting up the testing container.

Run nosetests (in an ephemeral container):

    docker-compose -f compose-testing.yml run --rm --user "$(id -u):$(id -g)" nosetests -v
