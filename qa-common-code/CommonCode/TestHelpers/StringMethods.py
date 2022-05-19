import random
import string
import socket
import struct


def get_unique_string(prefix='random_'):
    """
    Used for any name that needs to be unique and can contains Letter (lower and upper case) and Digits
    :param prefix:
    :return:
    """
    chars = string.ascii_letters + string.digits
    random_text = ''.join([random.choice(chars) for _ in range(5)])

    return prefix + random_text


def get_unique_name(prefix='random_'):
    """
    Used for Authentication names, as this unique name is only composed of Digits (Authentication names cannot
    contain Uppercase characters)
    :param prefix:
    :return:
    """
    chars = string.digits
    random_text = ''.join([random.choice(chars) for _ in range(5)])

    return prefix + random_text


def get_unique_ip():
    address = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    if '127' not in address:
        return address
    return get_unique_ip()


def random_number(min_value, max_value, except_value=None):
    """
    Method  generates random number

    :param min_value:1
    :param max_value:65535
    :param except_value: either single value or a list of values. Value(s) to avoid when generating a number
    :return:
    """
    if except_value is None:
        except_value = []
    elif type(except_value) != list:
        except_value = [except_value]

    random.seed()
    number = random.randrange(min_value, max_value)

    if except_value and number in except_value:
        return random_number(min_value, max_value, except_value)

    return number


def random_number_as_string(min_value, max_value, except_value=None):
    return str(random_number(min_value, max_value, except_value))
