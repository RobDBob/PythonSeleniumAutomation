import math
import os
import time
from PIL import Image
from selenium.webdriver.remote.webdriver import WebDriver
from CommonCode.TestHelpers.StringMethods import getUniqueAlphaNumericString


class Screenshot:
    """
    Modified from: https://pypi.org/project/Selenium-Screenshot/
    """
    _stitchedImage: Image = None
    totalWidth = None
    height = None

    def __init__(self, webdriver):
        self.webdriver: WebDriver = webdriver
        self.scrollTo(0)
        self.totalHeight = self.webdriver.execute_script("return document.documentElement.scrollHeight")
        self.viewportHeight = self.webdriver.execute_script("return window.innerHeight")
        self.heightRatio = float(self.totalHeight / self.viewportHeight)

    def scrollTo(self, yAxis):
        self.webdriver.execute_script(f"window.scrollTo(0, {yAxis})")
        time.sleep(2)

    def fullScreenshot(self, imagePath: str):
        """
        Size of view port does not match size of screenshot
        Using size ration as comparison between view port total size and screenshot
        """
        try:
            screenshotsFiles = []
            totalNumberOfScreens = math.ceil(self.heightRatio)
            for index in range(totalNumberOfScreens):
                screenshotName = f"screenshot_partial_{getUniqueAlphaNumericString()}.png"
                self.webdriver.get_screenshot_as_file(screenshotName)
                screenshotsFiles.append(screenshotName)

                image = Image.open(screenshotName)
                self.totalWidth, self.height = image.size

                if index + 1 > self.heightRatio:
                    factionedPart = self.heightRatio % 1
                    x, y = image.size
                    yFrom = y - y * factionedPart
                    image = image.crop((0, yFrom, x, y))
                self.stitchedImage.paste(image, (0, index * self.height))
                self.scrollTo((index + 1) * self.viewportHeight)

            self.stitchedImage.save(imagePath)
        finally:
            for screenshotName in screenshotsFiles:
                if os.path.isfile(screenshotName):
                    os.remove(screenshotName)

    @property
    def stitchedImage(self) -> Image:
        if not self._stitchedImage:
            self._stitchedImage = Image.new('RGB', (self.totalWidth, math.ceil(self.heightRatio * self.height)))
        return self._stitchedImage
