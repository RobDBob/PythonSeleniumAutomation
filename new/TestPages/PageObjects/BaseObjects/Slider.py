from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class Slider:
    def __init__(self, entity, index=0):
        self.element = entity.find_elements(By.CLASS_NAME, 'rc-slider')[index]

    def drag(self, driver, drag_pixels_in_x_direction, drag_pixels_in_y_direction):
        slider_handler = self.element.find_element(By.CSS_SELECTOR, 'div.rc-slider-handle')
        ActionChains(driver).drag_and_drop_by_offset(slider_handler, drag_pixels_in_x_direction, drag_pixels_in_y_direction).perform()

    def get_left_value(self):
        ov = self.element.find_elements(By.CSS_SELECTOR, "div[role='slider']")[0].get_attribute('style')
        return float(ov.split(':')[1].split('%')[0].strip())

    def get_left_value_now(self):
        return int(self.element.find_elements(By.CSS_SELECTOR, "div[role='slider']")[0].get_attribute('aria-valuenow'))

    def get_left_value_min(self):
        return int(self.element.find_elements(By.CSS_SELECTOR, "div[role='slider']")[0].get_attribute('aria-valuemin'))

    def get_left_value_max(self):
        return int(self.element.find_elements(By.CSS_SELECTOR, "div[role='slider']")[0].get_attribute('aria-valuemax'))

    def get_left_slider_track_value(self):
        ov = self.element.find_elements(By.CSS_SELECTOR, "div[class='rc-slider-track']")[0].get_attribute('style')
        return float(ov.split(':')[2].split('%')[0].strip())

    def get_right_value(self):
        ov = self.element.find_elements(By.CSS_SELECTOR, "div[role='slider']")[1].get_attribute('style')
        return float(ov.split(':')[1].split('%')[0].strip())

    def get_right_value_now(self):
        return int(self.element.find_elements(By.CSS_SELECTOR, "div[role='slider']")[1].get_attribute('aria-valuenow'))

    @property
    def current_value(self):
        return float(self.element.find_element(By.CSS_SELECTOR, 'div.rc-slider-handle').get_attribute('aria-valuenow'))

    @property
    def current_value_left(self):
        return int(float(self.element.find_element(By.CSS_SELECTOR, 'div.rc-slider-handle-1').get_attribute('aria-valuenow')))

    @property
    def current_value_right(self):
        return int(float(self.element.find_element(By.CSS_SELECTOR, 'div.rc-slider-handle-2').get_attribute('aria-valuenow')))
