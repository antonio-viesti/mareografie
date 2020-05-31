# --------------------------------------------------
# Copyright (C) 2020 Antonio Viesti (a.viesti@eutropia.it).
# Creative Commons CC BY (https://creativecommons.org/licenses/by/4.0/)
# --------------------------------------------------

# Mareographic service layer.

import json
import logging
from datetime import datetime, timedelta

import pandas

from ispra_rmn.sparql_client import get_response

# Gets the "ISPRA Hydrometric Level" distribution: alta marea, bassa marea.
#
# Args:
# nearby: the tide gauge geographical reference.
# since: the time-depth, formatted as '%Y-%m'.
#
# Returns: the hydrometric level distribution, as a pandas dataframe:
#                        utc  level
# 0      2019-05-01 00:00:00   25.0
# 1      2019-05-01 00:10:00   22.4
# 2      2019-05-01 00:20:00   26.3
# 3      2019-05-01 00:30:00   24.3
# 4      2019-05-01 00:40:00   25.0
# ...
def get_hydrometric_level_distribution(nearby, since):

    logger = logging.getLogger(__name__)

    service = 'http://dati.isprambiente.it/sparql'

    request = ''
    request = request + 'PREFIX : <http://dati.isprambiente.it/ontology/core#>' + '\n'
    request = request + 'PREFIX gn: <http://www.geonames.org/ontology#>' + '\n'
    request = request + 'PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>' + '\n'
    request = request + 'PREFIX dcat: <http://www.w3.org/ns/dcat#>' + '\n'
    request = request + 'PREFIX purl: <http://purl.org/dc/terms/>' + '\n'
    request = request + 'select distinct ?station ?period ?csvUrl where {' + '\n'
    request = request + '?parameter a :HydrometricLevel.' + '\n'
    request = request + '?place rdfs:label \"' + nearby + '\".' + '\n'
    request = request + '?dataset rdfs:label \"Dataset RMN\"@it.' + '\n'
    request = request + 'FILTER ( str(?period) >= \"' + since + '\").' + '\n'
    request = request + '?parameter gn:nearbyFeature ?place.' + '\n'
    request = request + '?collection a :MeasurementCollection;' + '\n'
    request = request + ':measurementPeriod ?period;' + '\n'
    request = request + ':isDataOf ?parameter;' + '\n'
    request = request + ':generatedBy ?instrument;' + '\n'
    request = request + 'purl:isPartOf ?dataset;' + '\n'
    request = request + 'dcat:downloadURL ?csvUrl.' + '\n'
    request = request + '?instrument :placedOn ?stat.' + '\n'
    request = request + '?stat rdfs:label ?station.' + '\n'
    request = request + '} ORDER BY ?period'

    # Get the dictionary of monthly distributions:
    # {
    #   "head": {
    #     "link": [],
    #     "vars": [
    #       "station",
    #       "period",
    #       "csvUrl"
    #     ]
    #   },
    #   "results": {
    #     "distinct": false,
    #     "ordered": true,
    #     "bindings": [
    #       {
    #         "station": {
    #           "type": "literal",
    #           "value": "Bari tide gauge (RMN 2009)"
    #         },
    #         "period": {
    #           "type": "literal",
    #           "value": "2019-05"
    #         },
    #         "csvUrl": {
    #           "type": "uri",
    #           "value": "http://dati.isprambiente.it/rmn/bari/hydrometric.201905.csv"
    #         }
    #       },
    #       ...
    #       {
    #         "station": {
    #           "type": "literal",
    #           "value": "Bari tide gauge (RMN 2009)"
    #         },
    #         "period": {
    #           "type": "literal",
    #           "value": "2020-05"
    #         },
    #         "csvUrl": {
    #           "type": "uri",
    #           "value": "http://dati.isprambiente.it/rmn/bari/hydrometric.202005.csv"
    #         }
    #       }
    #     ]
    #   }
    # }
    logger.debug('Getting the dictionary of monthly distributions...')
    response = get_response(service, request)
    for log in json.dumps(response, indent = 2).splitlines():
        logger.debug(log)

    # Flatten the dictionary of monthly distributions:
    #    station.type               station.value period.type period.value csvUrl.type                                       csvUrl.value
    # 0       literal  Bari tide gauge (RMN 2009)     literal      2019-05         uri  http://dati.isprambiente.it/rmn/bari/hydrometr...
    # 1       literal  Bari tide gauge (RMN 2009)     literal      2019-06         uri  http://dati.isprambiente.it/rmn/bari/hydrometr...
    # 2       literal  Bari tide gauge (RMN 2009)     literal      2019-07         uri  http://dati.isprambiente.it/rmn/bari/hydrometr...
    # ...
    normalized_response = pandas.json_normalize(response['results']['bindings'])
    logger.debug('Flattening the dictionary of monthly distributions...')
    for log in normalized_response.head(1).to_string().splitlines():
        logger.debug(log)
    logger.debug('...')

    # Get the URL of monthly distributions:
    # 0     http://dati.isprambiente.it/rmn/bari/hydrometr...
    # 1     http://dati.isprambiente.it/rmn/bari/hydrometr...
    # 2     http://dati.isprambiente.it/rmn/bari/hydrometr...
    urls = normalized_response['csvUrl.value']
    logger.debug('Getting the URL of monthly distributions...')
    for log in urls.head(1).to_string().splitlines():
        logger.debug(log)
    logger.debug('...')

    # Get and concatenate monthly distributions, iterating over their URLs.
    logger.debug('Getting and concatenating monthly distributions, iterating over their URLs...')
    monthly_distributions = [pandas.read_csv(url, sep=';', header=0, names=['utc', 'level']) for url in urls]
    distribution = pandas.concat(monthly_distributions, ignore_index=True)
    for log in distribution.head(1).to_string().splitlines():
        logger.debug(log)
    logger.debug('...')

    return distribution

# Gets the current "ISPRA Hydrometric Level", as a segmented (cutted) value over quantiles.
#
# Args:
# here: the tide gauge geographical reference.
# cuts: the quantile cuts, defaulting to 10 (deciles).
#
# Returns: the current hydrometric level, as a segmented (cutted) value over quantiles.
def get_discretized_hydrometric_level_nearby(here, cuts=10):

    logger = logging.getLogger(__name__)

    # Get the hydrometric level distribution of the last 365 days.
    when = datetime.now() - timedelta(days = 365)
    since = when.strftime('%Y-%m')
    distribution = get_hydrometric_level_distribution(here, since)
    logger.debug(distribution)

    # Discretize (cut) the the hydrometric level value over quantiles.
    distribution['quantilized_bin'] = pandas.qcut(distribution['level'], q=cuts)
    distribution['quantilized_bin_label'] = pandas.qcut(distribution['level'], q=cuts, labels=[str(i) for i in range(1, cuts+1)])
    distribution['quantilized_bin_label'] = pandas.to_numeric(distribution['quantilized_bin_label'])
    logger.debug(distribution)

    # Get the latest distretized (cutted) hydrometric level value
    level = distribution.quantilized_bin_label.iat[-1]
    logger.info('Latest discretized (cutted) level value near ' + here + ': ' + str(level))
    
    return level

# Gets the current "ISPRA Hydrometric Level" value.
#
# Args:
# here: the tide gauge geographical reference.
#
# Returns: the current hydrometric level value.
def get_hydrometric_level_nearby(here):

    logger = logging.getLogger(__name__)

    # Get the latest monthly distribution
    when = datetime.now()
    if when.day == 1:
        when = when - timedelta(days=1)
    now = when.strftime('%Y-%m')
    latest_monthly_distribution = get_hydrometric_level_distribution(here, now)

    # Get the latest level value
    level = latest_monthly_distribution.level.iat[-1]
    logger.info('Latest level value near ' + here + ': ' + str(level))
    
    return level

if __name__ == '__main__':

    here = 'Bari'

    get_hydrometric_level_nearby(here)

# --------------------------------------------------