from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject


class Label(BaseTestObject):

    @property
    def color(self):
        return self.element.value_of_css_property("color")

    @property
    def percentageDoublePrecisionValue(self):
        percentageWeightingFloatValue = float(self.element.text.strip('%'))
        return f"{percentageWeightingFloatValue:.2f}%"
