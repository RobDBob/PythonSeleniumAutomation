from selenium.webdriver.common.by import By


def update_locator(by, value):
    """
    Locator update to search for a partial class whenever by class is used.
    :param by:
    :param value:
    :return:
    """
    if by == By.CLASS_NAME:
        by_ = By.CSS_SELECTOR
        value_ = '[class*="{0}"]'.format(value)
    else:
        by_ = by
        value_ = value

    return by_, value_
