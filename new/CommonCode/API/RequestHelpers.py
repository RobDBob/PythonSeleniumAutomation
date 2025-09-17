from urllib.parse import parse_qs, urlparse


def extractURLParameters(url):
    """
    Extracts parameters from a given URL and returns them as a dictionary.

    url = "MaintainUser.aspx?type=edit&searchuserid=1566770"
    parameters = extract_url_parameters(url)
    print(parameters)
    {'type': 'edit', 'searchuserid': '1566770'}

    :param url: The URL string to parse.
    :return: A dictionary containing the parameters and their values.
    """
    parsedURL = urlparse(url)
    parameters = parse_qs(parsedURL.query)
    # Convert lists to single values if only one value exists for a parameter
    return {key: value[0] if len(value) == 1 else value for key, value in parameters.items()}
