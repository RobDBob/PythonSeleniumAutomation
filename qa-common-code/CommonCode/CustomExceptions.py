from selenium.common.exceptions import WebDriverException


class UIException(WebDriverException):
    pass


class TokenExpiredException(Exception):
    pass


class APIException(Exception):
    pass
