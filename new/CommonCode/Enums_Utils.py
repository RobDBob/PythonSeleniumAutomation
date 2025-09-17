def list_enum(enum):
    """
    List values for all non private / system variables in the class.
    Often used to print out enum values.
    :param enum:
    :return:
    """
    assert type(enum) == type
    return [getattr(enum, i) for i in list_parameters(enum)]


def list_parameters(enum):
    """
    Lists names ofr non private / system variables in the class.
    :param enum:
    :return:
    """
    assert type(enum) == type
    return [i for i in dir(enum) if not i.startswith('_')]