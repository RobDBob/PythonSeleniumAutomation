def getValueFromURLParams(url, paramName):
    """
    Example. 
    url = 'https://slwrapte5.fnz.co.uk/fnzhome.aspx/popups/loaddocstore.aspx?filename=ommfup111Rw991TImYYsKnbp6CeMzdFQdxWpV60oNjwRhBdhE-vJeKMIvl8dtffUruEtpmXobquFt8RfwqmZuPmodkGqvYTejqAXC-2glrs1&encrypt=yes'
    paramName = fileName
    urlparse result:
    0: 'https'
    1: 'slwrapte5.fnz.co.uk'
    2: '/popups/loaddocstore.aspx'
    3: ''
    4: 'filename=ommfup111Rw991TImYYsKnbp6CeMzdFQdxWpV60oNjwRhBdhE-vJeKMIvl8dtffUruEtpmXobquFt8RfwqmZuPmodkGqvYTejqAXC-2glrs1&encrypt=yes'
    5: ''
    """
    from urllib.parse import urlparse
    from urllib.parse import parse_qs
    parsedUrl = urlparse(url)
    parsedQuery = parse_qs(parsedUrl.query)
    if paramName in parsedQuery:
        return parsedQuery[paramName][0]