import logging
import sys

import pandas as pd
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.support.ui import WebDriverWait

from scrapper.contants import MODAL_SELECTOR, TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class options_are_greather_than(object):
    def __init__(self, locator, length):
        self.locator = locator
        self.length = length

    def __call__(self, driver):
        element = _find_element(driver, self.locator)
        opts = element.find_elements_by_tag_name("option")
        return len(opts) > self.length


def wait_for_element(driver, locator, text=None, opts_length_gt=0):
    try:
        url = driver.current_url
        if text is None and opts_length_gt == 0:
            return WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located(locator)
            ) and WebDriverWait(driver, TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            )

        if text:
            return WebDriverWait(driver, TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            ) and WebDriverWait(driver, TIMEOUT).until(
                EC.text_to_be_present_in_element(locator, text)
            )

        if opts_length_gt:
            return WebDriverWait(driver, TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            ) and WebDriverWait(driver, TIMEOUT).until(
                options_are_greather_than(locator, opts_length_gt)
            )
    except exceptions.TimeoutException:
        if driver.current_url == "https://www.climatempo.com.br/ops":
            logger.info("URL not available, trying next city...")
            driver.get(url)
            wait_for_element((By.CSS_SELECTOR, MODAL_SELECTOR))
            driver.find_element_by_css_selector(MODAL_SELECTOR).click()

            return False

        raise


def dump_cities(cities):
    result = pd.concat(
        [pd.DataFrame(cities[i]) for i in range(len(cities))], ignore_index=True
    )
    result.to_csv("result.csv", index=False)
    sys.exit()
