import logging
import sys

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select

from .constants import (
    BTN_SELECTOR,
    CITY_LIMIT,
    CITY_SELECTOR,
    MODAL_SELECTOR,
    STATE_SELECTOR,
)
from .utils import dump_cities, wait_for_element

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cities_list = []


def cities_from_state(state, driver):
    EXCLUDE_STATE_OPTS = ["Nome do Estado", "BUSCANDO..."]
    current_state = getattr(state, "text", state)

    logger.info("Selecting state... %s", state)

    if current_state in EXCLUDE_STATE_OPTS:
        return

    wait_for_element(driver, (By.CSS_SELECTOR, STATE_SELECTOR), text=current_state)
    state_select = Select(driver.find_element_by_css_selector(STATE_SELECTOR))
    state_select.select_by_visible_text(current_state)

    wait_for_element(driver, (By.CSS_SELECTOR, CITY_SELECTOR), opts_length_gt=2)

    city_soup = (
        BeautifulSoup(driver.page_source, features="lxml")
        .select(CITY_SELECTOR)[0]
        .find_all("option")
    )

    for city in city_soup:
        yield city


def scrape_city_data(current_city, current_state, driver, city_limit):
    EXCLUDE_CITY_OPTS = ["Nome da Cidade", "BUSCANDO..."]
    if current_city in EXCLUDE_CITY_OPTS:
        return

    wait_for_element(driver, (By.CSS_SELECTOR, STATE_SELECTOR), opts_length_gt=2)
    wait_for_element(driver, (By.CSS_SELECTOR, CITY_SELECTOR), opts_length_gt=2)

    logger.info("Current state %s", current_state)
    logger.info("Current city %s", current_city)

    wait_for_element(driver, (By.CSS_SELECTOR, STATE_SELECTOR), text=current_state)

    state_select = Select(driver.find_element_by_css_selector(STATE_SELECTOR))
    state_select.select_by_visible_text(current_state)

    wait_for_element(driver, (By.CSS_SELECTOR, CITY_SELECTOR), text=current_city)

    city_select = Select(driver.find_element_by_css_selector(CITY_SELECTOR))
    city_select.select_by_visible_text(current_city)

    wait_for_element(driver, (By.CSS_SELECTOR, BTN_SELECTOR))
    driver.find_element_by_css_selector(BTN_SELECTOR).click()

    table_selector = "table.left"
    if not wait_for_element(driver, (By.CSS_SELECTOR, table_selector)):
        return
    data_source = BeautifulSoup(driver.page_source, features="lxml")

    table = data_source.select("table.left")[0]

    df = pd.read_html(str(table), header=0)[0]
    df.insert(0, "Cidade", current_city)
    df.insert(1, "Estado", current_state)
    df.assign(Cidade=current_city, Estado=current_state)

    cities_list.append(df)
    if len(cities_list) == city_limit:
        logger.info("%s cities scrapped. Exiting..." % city_limit)
        dump_cities(cities_list)

    wait_for_element(driver, (By.CSS_SELECTOR, MODAL_SELECTOR))
    driver.execute_script(
        "arguments[0].click();", driver.find_element_by_css_selector(MODAL_SELECTOR)
    )

    logger.info("Going back to city select")


def scrape(url, driver, city_limit=CITY_LIMIT):
    driver.get(url)

    wait_for_element(driver, (By.CSS_SELECTOR, MODAL_SELECTOR))
    driver.find_element_by_css_selector(MODAL_SELECTOR).click()

    # make sure options are loaded
    wait_for_element(driver, (By.CSS_SELECTOR, STATE_SELECTOR), opts_length_gt=2)
    wait_for_element(driver, (By.CSS_SELECTOR, CITY_SELECTOR), opts_length_gt=2)

    state_soup = (
        BeautifulSoup(driver.page_source, features="lxml")
        .select(STATE_SELECTOR)[0]
        .find_all("option")
    )

    for state in state_soup:
        current_state = getattr(state, "text", state)

        for city in cities_from_state(current_state, driver):
            current_city = getattr(city, "text", city)
            scrape_city_data(current_city, current_state, driver, city_limit)


def main():
    url = "https://www.climatempo.com.br/climatologia/2/santos-sp"

    chrome_options = Options()
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.default_content_settings": {"popups": 1},
    }

    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)

    try:
        city_limit = int(sys.argv[1])
        logger.info("Using custom city scrapper limit %s", city_limit)

    except IndexError:
        logger.info("Using default city scrapper limit %s", city_limit)

    scrape(url, driver, city_limit)
