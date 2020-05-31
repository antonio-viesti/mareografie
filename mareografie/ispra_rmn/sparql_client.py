# --------------------------------------------------
# Copyright (C) 2020 Antonio Viesti (a.viesti@eutropia.it).
# Creative Commons CC BY (https://creativecommons.org/licenses/by/4.0/)
# --------------------------------------------------

# Simple SPARQL client.

import logging

from SPARQLWrapper import JSON, SPARQLWrapper

# Posts the request to a SPARQL service, and returns the response.
#
# Args:
# service: the SPARQL service.
# request: the SPARQL request.
#
# Returns: the SPARQL response, as json data.
def get_response(service, request):

    # logger = logging.getLogger(__name__)

    sparql = SPARQLWrapper(service)
    sparql.setQuery(request)
    sparql.setReturnFormat(JSON)

    return sparql.query().convert()

# --------------------------------------------------