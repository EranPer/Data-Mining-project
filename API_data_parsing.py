import requests
import json
from config import COUNTRIES_NAMES_TO_CODES, API, OK_STATUS


def api_query(**kwargs):
    """
    get the transmission type for each country.
    the types are ordered like this:
    0 = "Community transmission", 1 = "Local transmission", 2 = "Imported cases only",
    3 = "Under investigation", 4 = "Interrupted transmission", 5 = "Sporadic cases",
    6 = "Clusters of cases", 7 = "No cases".
    :param kwargs: optional parameters to query the API. if not given specificlly,
    the API will be queried on all the relevant data
    :return: a nested dictionary with country code as primary key,
    and each value is a dictionary with country name and type of transmission
    (integers from 0 to 7).
    """
    querystring = {}
    if kwargs is not None:
        querystring = dict(kwargs)

    headers = {
        'x-rapidapi-key': "1a1d6280fbmshf2b931091c487dfp1cc02bjsnb3b5ce9088b2",
        'x-rapidapi-host': "who-covid-19-data.p.rapidapi.com"
    }

    response = requests.request("GET", API, headers=headers, params=querystring)
    data_json = json.loads(response.text)

    transmission = dict()

    for cont in data_json:
        if cont['name'] in COUNTRIES_NAMES_TO_CODES.keys():
            transmission[COUNTRIES_NAMES_TO_CODES[cont['name']]] = \
                {'country': cont['name'], 'type': cont['transmissionType']}

    return transmission


def api_request(api):
    """
    This function returns a json response if the status code is OK.
    :param api: an api URL.
    :return: a json response.
    """
    response = requests.get(api)
    if response.status_code == OK_STATUS:
        return response.json()


# print(api_query())