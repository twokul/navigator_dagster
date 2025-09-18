from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def scrape_adea_programs() -> List[Dict]:
    """Scrape ADEA PASS programs from the website and return structured data."""
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the ADEA PASS programs page
        url = "https://programs.adea.org/PASS/programs"
        driver.get(url)

        # Wait for the page to load and wait for program cards to appear
        wait = WebDriverWait(driver, 20)
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "adea-program-cards"))
        )

        # Wait additional 5 seconds for all content to load
        time.sleep(5)

        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find all program cards
        program_cards = soup.find_all("article", class_="adea-pgrm")

        programs = []
        for card in program_cards:
            try:
                program_data = extract_program_data(card)
                if program_data:
                    programs.append(program_data)
            except Exception as e:
                logger.error(f"Error extracting program data: {e}")
                continue

        return programs

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return []
    finally:
        if driver:
            driver.quit()


def extract_program_data(card) -> Dict:
    """Extract program data from a single program card."""
    try:
        # Extract name
        name_element = card.find("h3", class_="adea-pgrm__title__heading")
        name = (
            name_element.find("a").text.strip()
            if name_element and name_element.find("a")
            else ""
        )

        # Extract state
        meta_list = card.find("ul", class_="adea-pgram__title__meta")
        state = ""
        if meta_list:
            state_li = meta_list.find("li")
            state = state_li.text.strip() if state_li else ""

        # Extract program type
        program_type = ""
        if meta_list:
            badge = meta_list.find("span", class_="ui-badge")
            if badge:
                program_type = badge.find("span", class_="ui-badge__text").text.strip()

        # Extract URL
        url = ""
        if name_element and name_element.find("a"):
            href = name_element.find("a").get("href")
            if href:
                url = f"https://programs.adea.org{href}"

        # Extract program details from the info table
        info_table = card.find("div", class_="adea-pgrm__info")
        size = ""
        length = ""
        application_deadline = ""
        start_date = ""

        if info_table:
            rows = info_table.find_all("div", class_="adea-pgrm__info__row")
            for row in rows:
                header = row.find("div", class_="adea-pgrm__info__col--header")
                value = row.find("div", class_="adea-pgrm__info__col--value")

                if header and value:
                    header_text = header.text.strip()
                    value_text = value.text.strip()

                    if header_text == "Program Size":
                        size = value_text
                    elif header_text == "Program Length":
                        length = value_text
                    elif header_text == "Application Deadline":
                        application_deadline = value_text
                    elif header_text == "Program Start":
                        start_date = value_text

        return {
            "name": name,
            "state": state,
            "type": program_type,
            "url": url,
            "size": size,
            "length": length,
            "application_deadline": application_deadline,
            "start_date": start_date,
        }

    except Exception as e:
        logger.error(f"Error extracting program data from card: {e}")
        return None
