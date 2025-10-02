from selenium.common.exceptions import WebDriverException


class UIException(WebDriverException):
    pass


class TokenExpiredException(Exception):
    pass


class APIException(Exception):
    pass


class AccessDeniedException(Exception):
    pass


class AccessBlockedException(Exception):
    pass


class APIExceptionSessionExpired(Exception):
    pass


class FileNotReadyException(Exception):
    pass


class DataException(Exception):
    pass
