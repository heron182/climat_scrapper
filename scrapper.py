import json
import logging
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common import exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scrapper")

TIMEOUT = 50

state_selector = "#sel-state-geo"
city_selector = "#sel-city-geo"
btn_selector = "#btn-confirm-geo"
modal_selector = "p.columns:nth-child(2) > span:nth-child(2)"
detailist = {}


def wait_for_element(locator, text=None):
    if text is None:
        return WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located(locator)
        ) and WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    return WebDriverWait(driver, TIMEOUT).until(
        EC.visibility_of_element_located(locator)
    ) and WebDriverWait(driver, TIMEOUT).until(
        EC.text_to_be_present_in_element(locator, text)
    )


def scrape_city_data(current_city, current_state, driver):
    wait_for_element((By.CSS_SELECTOR, btn_selector))

    logger.info("Current state %s", current_state)
    logger.info("Current city %s", current_city)

    wait_for_element((By.CSS_SELECTOR, state_selector), text=current_state)
    state_select = Select(driver.find_element_by_css_selector(state_selector))
    state_select.select_by_visible_text(current_state)

    wait_for_element((By.CSS_SELECTOR, city_selector), text=current_city)
    city_select = Select(driver.find_element_by_css_selector(city_selector))
    city_select.select_by_visible_text(current_city)

    wait_for_element((By.CSS_SELECTOR, btn_selector))
    driver.find_element_by_css_selector(btn_selector).click()

    table_selector = "table.left"
    wait_for_element((By.CSS_SELECTOR, table_selector))
    data_source = BeautifulSoup(driver.page_source, features="lxml")

    table = data_source.select("table.left")[0]
    df = pd.read_html(str(table), header=0)
    detailist["%s - %s" % (current_city, current_state)] = json.loads(
        df[0].to_json(orient="records")
    )

    wait_for_element((By.CSS_SELECTOR, modal_selector))
    driver.execute_script(
        "arguments[0].click();", driver.find_element_by_css_selector(modal_selector)
    )
    logger.info("Going back to city select")


def scrape(url, driver):
    logger.info("Getting url %s", url)
    driver.get(url)
    driver.maximize_window()

    modal_selector = "p.columns:nth-child(2) > span:nth-child(2)"
    wait_for_element((By.CSS_SELECTOR, modal_selector))
    driver.find_element_by_css_selector(modal_selector).click()

    state_selector = "#sel-state-geo"
    city_selector = "#sel-city-geo"
    btn_selector = "#btn-confirm-geo"

    # make sure options were loaded
    wait_for_element((By.CSS_SELECTOR, city_selector))
    wait_for_element((By.CSS_SELECTOR, state_selector))

    detailist = {}

    state_soup = (
        BeautifulSoup(driver.page_source, features="lxml")
        .select(state_selector)[0]
        .find_all("option")
    )

    for state in state_soup:
        current_state = getattr(state, "text", state)
        if "BUSCANDO" in current_state:
            continue
        wait_for_element((By.CSS_SELECTOR, state_selector), text=current_state)

        state_select = Select(driver.find_element_by_css_selector(state_selector))
        state_select.select_by_visible_text(current_state)

        city_soup = (
            BeautifulSoup(driver.page_source, features="lxml")
            .select(city_selector)[0]
            .find_all("option")
        )

        for city in city_soup:
            current_city = getattr(city, "text", city)
            if "BUSCANDO" in current_city:
                continue
            wait_for_element((By.CSS_SELECTOR, btn_selector))

            logger.info("Current state %s", current_state)
            logger.info("Current city %s", current_city)

            wait_for_element((By.CSS_SELECTOR, state_selector), text=current_state)
            state_select = Select(driver.find_element_by_css_selector(state_selector))
            state_select.select_by_visible_text(current_state)

            wait_for_element((By.CSS_SELECTOR, city_selector), text=current_city)
            city_select = Select(driver.find_element_by_css_selector(city_selector))
            city_select.select_by_visible_text(current_city)

            wait_for_element((By.CSS_SELECTOR, btn_selector))
            driver.find_element_by_css_selector(btn_selector).click()

            table_selector = "table.left"
            wait_for_element((By.CSS_SELECTOR, table_selector))
            data_source = BeautifulSoup(driver.page_source, features="lxml")

            table = data_source.select("table.left")[0]
            df = pd.read_html(str(table), header=0)
            detailist["%s - %s" % (current_city, current_state)] = json.loads(
                df[0].to_json(orient="records")
            )

            wait_for_element((By.CSS_SELECTOR, modal_selector))
            driver.execute_script(
                "arguments[0].click();",
                driver.find_element_by_css_selector(modal_selector),
            )
            logger.info("Going back to city select")

    json_result = open("result.json", "w", encoding="utf-8")
    json_result.write(json.dumps(detailist, ensure_ascii=False))
    json_result.close()


if __name__ == "__main__":
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

    scrape(url, driver)
