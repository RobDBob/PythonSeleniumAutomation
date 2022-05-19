def manufacture(type_to_manufacture, parent_web_element, by, value):
    """
    factory method, returns multiple instances of an ui element (type_to_manufacture)
    :param type_to_manufacture:
    :param parent_web_element:
    :param by:
    :param value:
    :return:
    """
    element_count = len(parent_web_element.find_elements(by, value))
    return [type_to_manufacture(parent_web_element, by, value, index) for index in range(element_count)]
