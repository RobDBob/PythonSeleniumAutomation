from CommonCode.TestExecute.Logging import PrintMessage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from CommonCode.BasePageObjects.BaseTestObject import BaseTestObject
from CommonCode.BasePageObjects.CTAButton import Button
from CommonCode.BasePageObjects.EditFIeld import EditField
from CommonCode.BasePageObjects.Labels import Label
from CommonCode.ObjProduction import manufacture
from CommonCode.WebDriver import ExpectedConditions as EC


class DropDownIcon(object):
    """
    There are currently two types of icon available in dropdown ui element
    """
    dropdown_icon = 'dropdown icon'
    search_icon = 'search icon'


class SingleSelectDropdown(BaseTestObject):
    """Editable selection"""

    def __init__(self, parent_web_element, by_type, value):
        super(SingleSelectDropdown, self).__init__(parent_web_element, by_type, value)

        self.dropdown_icon = DropDownIcon.search_icon
        self.wait_for_dimmer_callback = None

    def wait_for_inserted_value_is_applied(self, value):
        input_element = EC.text_to_be_present_in_element(self.element, value)
        WebDriverWait(self.parent_web_element, 60).until(input_element)

    def select_input(self, value):
        PrintMessage("Select_input, inserting {0}".format(value))
        self.scroll_to_element()
        self.input.send_keys(value)
        self.wait_for_inserted_value_is_applied(value)

        self.input.send_keys(Keys.ENTER, clear=False)
        PrintMessage("Drop down value inserted {0}".format(self.get_selected_items_as_text()))

    def get_selected_items_as_text(self):
        """
        Returns single text element.
        Uses same name as multi select counterpart
        :return:
        """
        return self.element.text

    @property
    def side_button(self):
        """
        It might be either search or select.
        This search will only work when used through ElementFinder find by partial class name, otherwise it'll
        fail with 'Compound class names not permitted'
        as webdriver won't take class with multiple words (white space delimited)
        :return:
        """
        return Button(self.element, By.CLASS_NAME, self.dropdown_icon)

    @property
    def input(self):
        return EditField(self.element, By.CLASS_NAME, 'search')


class MultiSelectDropdown(SingleSelectDropdown):
    def __getitem__(self, label_title):
        """
        returns matching filter label
        """
        found_items = self._get_all_selected_items()

        if len(found_items) > 0:
            return [k for k in found_items if label_title in k.value_text][0]

        PrintMessage("Filter element with name : {0} not found".format(label_title))

    def _get_all_selected_items(self):
        return manufacture(Label, self.element, By.CSS_SELECTOR, '.ui.label')

    def get_selected_items_as_text(self):
        """
        Returns list of text strings from edit box
        :return:
        """
        all_items = self._get_all_selected_items()
        return [k.value_text for k in all_items]

    @property
    def selected_items(self):
        """
        Returns UI elements (labels)
        Those come with text and action to remove
        :return:
        """
        return self._get_all_selected_items()


class Dropdown(object):
    def __init__(self, webdriver,
                 by_type=By.CSS_SELECTOR,
                 value="div[role='combobox'].search.selection.dropdown",
                 index=0,
                 input_index=None,
                 arrow_index=None):
        """
        Input for index is by default none, and it is only used when we are working with disabled dropdowns
        :param webdriver:
        :param by_type:
        :param value:
        :param index:
        :param input_index:
        """
        self.webdriver = webdriver
        self.element = self.webdriver.find_elements(by_type, value)[index]
        self.index = index
        if input_index:
            self.input_index = input_index
            self.arrow_index = arrow_index
        else:
            self.input_index = index
            self.arrow_index = index

    def wait(self):
        dropdown = EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="combobox"].search.selection.dropdown'))
        WebDriverWait(self.webdriver, 10).until(dropdown)

    def select_input(self, value=None):
        self.arrow.click()
        self.enter_input.send_keys(value)
        self.enter_input.send_keys(Keys.ENTER, clear=False)
        PrintMessage('Value of %s has been selected' % value)

    def click(self):
        self.wait()
        self.element.click()

    def get_current_text_value(self):
        return self.element.find_element(By.CSS_SELECTOR, 'div[class="text"]').get_attribute('innerText')

    def get_current_value(self):
        return self.element.get_attribute('innerText')

    def get_placeholder_text(self):
        return self.element.get_attribute("placeholder")

    def get_value_without_style(self):
        return self.element.get_attribute('innerText').split('\t')[0]

    @property
    def text(self):
        return self.element.get_attribute('innerText')

    @property
    def arrow(self):
        return Button(self.element, By.CSS_SELECTOR, "i.dropdown.icon")

    @property
    def enter_input(self):
        return EditField(self.element, By.CSS_SELECTOR, "input[type='text']")
