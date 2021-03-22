def add_components(spec):
    """Adds the service components to OpenAPI specification.

    Arguments:
        spec (obj): The apispec object.
    """
    import copy

    # Parameters

    spec.components.parameter('idempotencyKey', 'header', {
        "name": "X-Idempotence-Key",
        "description": "A unique idempotency key assigned to each request.",
        "required": False,
        "schema": {"type": "string"},
        "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    })

    # Schemata

    base_form = {
        "type": "object",
        "properties": {
            "response": {
                "type": "string",
                "description": "Response type, either *prompt* to initiate the process promptly and wait for the response, either *deferred* to finish the process asynchronously.",
                "enum": ["prompt", "deferred"],
                "default": "deferred"
            },
            "download": {
                "type": "boolean",
                "description": "**For prompt requests only.** If *true* the response will be a stream, otherwise its path will be returned (ignored for deferred requests).",
                "default": "false",
            },
            "delimiter": {
                "type": "string",
                "description": "In case the file is a delimited text file, the character used to separate values. Ignored for not delimited files.",
                "example": ";",
                "default": ","
            },
            "lat": {
                "type": "string",
                "description": "The attribute name in delimited text files that corresponds to latitude, if the geometry is given in means of lat, lon. Ignored for not delimited files.",
                "example": "latitude"
            },
            "lon": {
                "type": "string",
                "description": "The attribute name in delimited text files that corresponds to longitude, if the geometry is given in means of lat, lon. Ignored for not delimited files.",
                "example": "longitude"
            },
            "geom": {
                "type": "string",
                "description": "The attribute name in delimited text files that corresponds to WKT geometry. Default is 'WKT'; ignored for not delimited files **or** when 'lat', 'lon' are provided.",
                "example": "geometry"
            },
            "crs": {
                "type": "string",
                "description": "The Coordinate Reference System of the geometries. If not given, the CRS information is obtained by the dataset; **required for** spatial files that do not provide CRS information, e.g. CSV.",
                "example": "EPSG:4326"
            },
            "encoding": {
                "type": "string",
                "description": "The encoding of the file. If not given, the encoding is automatically detected.",
                "example": "UTF-8"
            },
        },
    }

    resource = {
        "type": "string",
        "description": "A resolvable path to the spatial file, relative to the **input directory**. The file could be in compressed form: zipped or tar(.gz) archive.",
        "example": "/datasets/shapefile.tar.gz"
    }

    resource_multi = {
        "type" : "string",
        "format": "binary",
        "description": "Stream of the spatial file. The file could be in compressed form: zipped or tar(.gz) archive."
    }

    constructive_form = {
        **base_form,
        "properties": {
            **base_form["properties"],
            "resource": resource
        },
        "required": ["resource"]
    }
    spec.components.schema('constructiveForm', constructive_form)

    constructive_form_multi = {
        **base_form,
        "properties": {
            **base_form["properties"],
            "resource": resource_multi
        },
        "required": ["resource"]
    }
    spec.components.schema('constructiveFormMultipart', constructive_form_multi)

    simplify_extra = {
        "tolerance": {
            "type": "number",
            "format": "float",
            "description": "The maximum allowed geometry displacement. The higher this value, the smaller the number of vertices in the resulting geometry.",
            "example": "1.0"
        },
        "preserve_topology": {
            "type": "boolean",
            "description": "If set to *true*, the operation will avoid creating invalid geometries.",
            "default": "false"
        }
    }

    simplify_form = {
        **base_form,
        "properties": {
            **base_form["properties"],
            **simplify_extra,
            "resource": resource
        },
        "required": ["tolerance", "resource"]
    }
    spec.components.schema('simplifyConstructiveForm', simplify_form)

    simplify_form_multi = {
        **base_form,
        "properties": {
            **base_form["properties"],
            **simplify_extra,
            "resource": resource_multi
        },
        "required": ["tolerance", "resource"]
    }
    spec.components.schema('simplifyConstructiveFormMultipart', simplify_form_multi)

    wkt = {
        "type": "string",
        "description": "The Well-Known-Text representation of the geometry to filter with. It is meant to be in the same srid as the spatial file.",
        "example": "POLYGON((6.4 49., 6.5 50., 6.6 49.5, 6.4 49.))"
    }

    filter_form = {
        **base_form,
        "properties": {
            **base_form["properties"],
            "wkt": wkt,
            "resource": resource
        },
        "required": ["wkt", "resource"]
    }
    spec.components.schema('filterForm', filter_form)

    filter_form_multi = {
        **base_form,
        "properties": {
            **base_form["properties"],
            "wkt": wkt,
            "resource": resource_multi
        },
        "required": ["wkt", "resource"]
    }
    spec.components.schema('filterFormMultipart', filter_form_multi)

    buffer_extra = {
        "radius": {
            "type": "number",
            "format": "float",
            "description": "The radius from the given geometry that the geometries should lie within. The radius is specified in units defined by the srid.",
            "example": 0.1
        }
    }

    buffer_form = {
        **filter_form,
        "properties": {
            **filter_form["properties"],
            **buffer_extra,
            "resource": resource
        },
        "required": ["wkt", "radius", "resource"]
    }
    spec.components.schema('bufferFilterForm', buffer_form)

    buffer_form_multi = {
        **filter_form,
        "properties": {
            **filter_form["properties"],
            **buffer_extra,
            "resource": resource_multi
        },
        "required": ["wkt", "radius", "resource"]
    }
    spec.components.schema('bufferFilterFormMultipart', buffer_form_multi)

    join_base_form = {
        **base_form,
        "properties": {
            **base_form["properties"],
            "other_delimiter": {
                "type": "string",
                "description": "In case the **other** file is a delimited text file, the character used to separate values. Ignored for not delimited files.",
                "example": ";",
                "default": ","
            },
            "other_lat": {
                "type": "string",
                "description": "**For the other file.** The attribute name in delimited text files that corresponds to latitude, if the geometry is given in means of lat, lon. Ignored for not delimited files.",
                "example": "latitude"
            },
            "other_lon": {
                "type": "string",
                "description": "**For the other file.** The attribute name in delimited text files that corresponds to longitude, if the geometry is given in means of lat, lon. Ignored for not delimited files.",
                "example": "longitude"
            },
            "other_geom": {
                "type": "string",
                "description": "The attribute name in delimited text files that corresponds to WKT geometry. Default is 'WKT'; ignored for not delimited files **or** when 'lat', 'lon' are provided.",
                "example": "geometry"
            },
            "other_crs": {
                "type": "string",
                "description": "The Coordinate Reference System of the geometries in the **other** spatial file. If not given, the CRS information is obtained by the dataset; **required for** spatial files that do not provide CRS information, e.g. CSV.",
                "example": "EPSG:4326"
            },
            "other_encoding": {
                "type": "string",
                "description": "The encoding of the **other** file. If not given, the encoding is automatically detected.",
                "example": "UTF-8"
            },
            "how": {
                "type": "string",
                "description": "Type of the spatial join.",
                "enum": ["left", "right", "inner"],
                "default": "inner"
            },
            "lprefix": {
                "type": "string",
                "description": "Prefix for the *left* attributes.",
                "example": "l_"
            },
            "rprefix": {
                "type": "string",
                "description": "Prefix for the *right* attributes.",
                "example": "r_"
            },
            "lsuffix": {
                "type": "string",
                "description": "Suffix for the *left* attributes.",
                "example": "_l"
            },
            "rsuffix": {
                "type": "string",
                "description": "Suffix for the *right* attributes.",
                "example": "_r"
            }
        }
    }

    other = {
        "type": "string",
        "description": "A resolvable path to the **other** spatial file, relative to the **input directory**. The file could be in compressed form: zipped or tar(.gz) archive.",
        "example": "/datasets/shapefile.tar.gz"
    }

    other_multi = {
        "type" : "string",
        "format": "binary",
        "description": "Stream of the **other** spatial file. The file could be in compressed form: zipped or tar(.gz) archive."
    }

    join_form = {
        **join_base_form,
        "properties": {
            **join_base_form["properties"],
            "resource": resource,
            "other": other
        },
        "required": ["resource", "other"]
    }
    spec.components.schema('joinForm', join_form)

    join_form_multi_both = {
        **join_base_form,
        "properties": {
            **join_base_form["properties"],
            "resource": resource_multi,
            "other": other_multi
        },
        "required": ["resource", "other"]
    }
    spec.components.schema('joinFormMultipartBoth', join_form_multi_both)

    join_form_multi_resource = {
        **join_base_form,
        "properties": {
            **join_base_form["properties"],
            "resource": resource_multi,
            "other": other
        },
        "required": ["resource", "other"]
    }
    spec.components.schema('joinFormMultipartResource', join_form_multi_resource)

    join_form_multi_other = {
        **join_base_form,
        "properties": {
            **join_base_form["properties"],
            "resource": resource,
            "other": other_multi
        },
        "required": ["resource", "other"]
    }
    spec.components.schema('joinFormMultipartOther', join_form_multi_other)

    dwithin_join_extra = {
        "distance": {
            "type": "number",
            "format": "float",
            "description": "The distance that the two geometries should be within. It is specified in units defined by the srid of the *resource* spatial file.",
            "example": 4.3
        }
    }
    spec.components.schema('dwithinJoinForm', {
        **join_form,
        "properties": {
            **join_form["properties"],
            **dwithin_join_extra
        },
        "required": ["resource", "other", "distance"]
    })
    spec.components.schema('dwithinJoinFormMultipartBoth', {
        **join_form_multi_both,
        "properties": {
            **join_form_multi_both["properties"],
            **dwithin_join_extra
        },
        "required": ["resource", "other", "distance"]
    })
    spec.components.schema('dwithinJoinFormMultipartResource', {
        **join_form_multi_resource,
        "properties": {
            **join_form_multi_resource["properties"],
            **dwithin_join_extra
        },
        "required": ["resource", "other", "distance"]
    })
    spec.components.schema('dwithinJoinFormMultipartOther', {
        **join_form_multi_other,
        "properties": {
            **join_form_multi_other["properties"],
            **dwithin_join_extra
        },
        "required": ["resource", "other", "distance"]
    })

    # Responses

    validation_error_response = {
        "description": "Form validation error.",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "description": "The key is the request body key.",
                    "additionalProperties": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Description of validation error."
                        }
                    },
                    "example": {
                        "crs": [
                            "Field must be a valid CRS."
                        ]
                    }
                }
            }
        }
    }
    spec.components.response('validationErrorResponse', validation_error_response)

    spec.components.response('deferredResponse', {
        "description": "Request accepted for process.",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Request type.",
                            "enum": ["prompt", "deferred"],
                            "example": "deferred"
                        },
                        "ticket": {
                            "type": "string",
                            "description": "The unique ticket assigned to the request.",
                            "example": "caff960ab6f1627c11b0de3c6406a140"
                        },
                        "statusUri": {
                            "type": "string",
                            "description": "The URI to poll for the status of the request.",
                            "example": "/jobs/status?ticket=caff960ab6f1627c11b0de3c6406a140"
                        }
                    }
                }
            }
        }
    })

    spec.components.response('promptResultResponse', {
        "content": {
            "application/x-tar": {
                "description": "W.",
                "schema": {
                    "type": "string",
                    "format": "binary",
                    "description": "Resulted spatial file (when form parameter *download* was set to true)."
                }
            },
            "application/json": {
                "schema": {
                    "type": "object",
                    "description": "When form parameter *download* was set to false.",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Request type.",
                            "enum": ["prompt", "deferred"]
                        },
                        "path": {
                            "type": "string",
                            "description": "The relative to the *output directory* path for the spatial file.",
                            "example": "2103/3ba6a8b5ecea27db3c5f4e0159c63283/example.csv.gz"
                        }
                    }
                }
            }
        }
    })

    spec.components.response('noContentResponse', {
        "description": "The operation resulted in an empty dataset."
    })
