from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
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
    """Extract program data from a single program card and fetch detailed information."""
    try:
        if card is None:
            return None

        # Extract basic info from card
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

        # Extract ADEA URL
        adea_url = ""
        if name_element and name_element.find("a"):
            href = name_element.find("a").get("href")
            if href:
                adea_url = f"https://programs.adea.org{href}"

        # Extract basic program details from the info table
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

        # Fetch detailed program information
        detailed_info = fetch_detailed_program_info(adea_url)

        # Merge basic info with detailed info
        result = {
            "name": name,
            "state": state,
            "type": program_type,
            "url": detailed_info.get("website_url", ""),
            "adea_url": adea_url,
            "size": int(size) if size.isdigit() else size,
            "length": int(length.split()[0])
            if length and length.split()[0].isdigit()
            else length,
            "application_deadline": application_deadline,
            "start_date": start_date,
            "last_updated": detailed_info.get("last_updated", ""),
            "description": detailed_info.get("description", ""),
            "information": detailed_info.get("information", {}),
            "requirements": detailed_info.get("requirements", []),
            "contact": detailed_info.get("contact", {}),
        }

        return result

    except Exception as e:
        logger.error(f"Error extracting program data from card: {e}")
        return None


def fetch_detailed_program_info(adea_url: str) -> Dict:
    """Fetch detailed program information from the program detail page."""
    try:
        if not adea_url:
            return {}

        # Make HTTP request to get detailed program page
        response = requests.get(adea_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        result = {
            "last_updated": "",
            "description": "",
            "website_url": "",
            "information": {},
            "requirements": [],
            "contact": {},
        }

        # Extract last updated date
        updated_element = soup.find("div", class_="adea-pgrm-dtl__updated")
        if updated_element:
            result["last_updated"] = updated_element.text.strip()

        # Extract header information
        header_element = soup.find("div", class_="adea-pgrm-dtl__header")
        if header_element:
            # Extract website URL from header
            website_link = header_element.find("a", href=True)
            if website_link and "advocatehealth.com" in website_link.get("href", ""):
                result["website_url"] = website_link.get("href")

        # Extract meta information
        meta_element = soup.find("div", class_="adea-pgrm-dtl__meta")
        if meta_element:
            info_table = meta_element.find("div", class_="adea-pgrm__info")
            if info_table:
                rows = info_table.find_all("div", class_="adea-pgrm__info__row")
                for row in rows:
                    header = row.find("div", class_="adea-pgrm__info__col--header")
                    value = row.find("div", class_="adea-pgrm__info__col--value")

                    if header and value:
                        header_text = header.text.strip()
                        value_text = value.text.strip()

                        if header_text == "Program Size":
                            result["information"]["size"] = value_text
                        elif header_text == "Program Length":
                            result["information"]["length"] = value_text
                        elif header_text == "Application Deadline":
                            result["information"]["application_deadline"] = value_text
                        elif header_text == "Program Start":
                            result["information"]["start_date"] = value_text

        # Extract main content information
        main_element = soup.find("div", class_="adea-pgrm-dtl__main")
        if main_element:
            # Extract contact information
            contact_element = main_element.find("div", class_="adea-pgrm-dtl-contact")
            if contact_element:
                contact_info = extract_contact_info(contact_element)
                result["contact"] = contact_info

        # Extract body content for description and requirements
        body_element = soup.find("div", class_="adea-pgrm-dtl__body")
        if body_element:
            # Extract description from first section
            first_section = body_element.find("div", class_="adea-pgrm-dtl__section")
            if first_section:
                content = first_section.find(
                    "div", class_="adea-pgrm-dtl__section__content"
                )
                if content:
                    # Get all paragraph text
                    paragraphs = content.find_all("p")
                    description_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and not text.startswith("For further information"):
                            description_parts.append(text)
                    result["description"] = " ".join(description_parts)

            # Extract program information table
            sections = body_element.find_all("div", class_="adea-pgrm-dtl__section")
            for section in sections:
                heading = section.find("h2", class_="adea-pgrm-dtl__section__heading")
                if heading and "Program Information" in heading.text:
                    table = section.find("table")
                    if table:
                        program_info = extract_program_info_table(table)
                        result["information"].update(program_info)
                    break

            # Extract requirements from accordion sections
            accordion_section = body_element.find(
                "div", class_="adea-pgrm-dtl__section--accordions"
            )
            if accordion_section:
                requirements = extract_requirements(accordion_section)
                result["requirements"] = requirements

            # Extract interview schedule and additional information
            sections = body_element.find_all("div", class_="adea-pgrm-dtl__section")
            for section in sections:
                heading = section.find("h2", class_="adea-pgrm-dtl__section__heading")
                if heading:
                    heading_text = heading.text.strip()
                    content = section.find(
                        "div", class_="adea-pgrm-dtl__section__content"
                    )
                    if content:
                        if heading_text == "Interview Schedule":
                            interview_text = content.get_text(strip=True)
                            result["requirements"].append(
                                {"title": heading_text, "sections": [interview_text]}
                            )
                        elif heading_text == "Additional Information":
                            additional_text = content.get_text(strip=True)
                            result["requirements"].append(
                                {"title": heading_text, "sections": [additional_text]}
                            )

        return result

    except Exception as e:
        logger.error(f"Error fetching detailed program info from {adea_url}: {e}")
        return {}


def extract_contact_info(contact_element) -> Dict:
    """Extract contact information from contact section."""
    contact_info = {"points_of_contact": [], "address": ""}

    try:
        # Extract address
        address_element = contact_element.find(
            "div", class_="adea-pgrm-dtl-contact__address"
        )
        if address_element:
            contact_info["address"] = address_element.get_text(strip=True)

        # Extract contact persons
        contact_names = contact_element.find_all(
            "div", class_="adea-pgrm-dtl-contact__name"
        )
        contact_actions = contact_element.find_all(
            "div", class_="adea-pgrm-dtl-contact__actions"
        )

        for i, name_element in enumerate(contact_names):
            contact_person = {}

            # Extract name and title
            name_parts = name_element.find_all("span")
            if len(name_parts) >= 2:
                # Get the full text and split by the title span
                full_text = name_element.get_text()
                title_text = name_parts[1].get_text(strip=True)

                # Find where the title starts and extract name before it
                title_index = full_text.find(title_text)
                if title_index > 0:
                    contact_person["name"] = full_text[:title_index].strip()
                else:
                    contact_person["name"] = name_parts[0].get_text(strip=True)
                contact_person["title"] = title_text

            # Extract email and phone from corresponding actions element
            if i < len(contact_actions):
                actions_element = contact_actions[i]
                email_link = actions_element.find(
                    "a", href=lambda x: x and x.startswith("mailto:")
                )
                phone_link = actions_element.find(
                    "a", href=lambda x: x and x.startswith("tel:")
                )

                if email_link:
                    contact_person["email"] = email_link.get("href").replace(
                        "mailto:", ""
                    )
                if phone_link:
                    contact_person["phone"] = phone_link.get("href").replace("tel:", "")

            if contact_person:
                contact_info["points_of_contact"].append(contact_person)

    except Exception as e:
        logger.error(f"Error extracting contact info: {e}")

    return contact_info


def extract_program_info_table(table) -> Dict:
    """Extract program information from the information table."""
    info = {}

    try:
        rows = table.find_all("tr")
        for row in rows:
            th = row.find("th")
            td = row.find("td")

            if th and td:
                key = th.text.strip().lower().replace(" ", "_")
                value = td.text.strip()

                # Handle website URL specially
                if key == "program_website":
                    link = td.find("a", href=True)
                    if link:
                        value = link.get("href")

                info[key] = value.lower() if value.lower() in ["yes", "no"] else value

    except Exception as e:
        logger.error(f"Error extracting program info table: {e}")

    return info


def extract_requirements(accordion_section) -> List[Dict]:
    """Extract requirements from accordion sections."""
    requirements = []

    try:
        accordions = accordion_section.find_all("div", class_="adea-pgrm-accordion")

        for accordion in accordions:
            heading = accordion.find("h3", class_="adea-pgrm-accordion__heading")
            content = accordion.find("div", class_="adea-pgrm-accordion__content")

            if heading and content:
                title = heading.text.strip()
                sections = []

                # Extract different types of content
                if "Required Standardized Tests" in title:
                    # Extract checkmarks
                    checks = content.find_all("li")
                    for check in checks:
                        text = check.get_text(strip=True)
                        if text:
                            sections.append(text)
                else:
                    # Extract paragraphs and lists
                    paragraphs = content.find_all("p")
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text:
                            # Clean up extra whitespace and special characters
                            text = " ".join(text.split())
                            sections.append(text)

                    # Extract list items
                    lists = content.find_all("ul")
                    for ul in lists:
                        items = ul.find_all("li")
                        for li in items:
                            text = li.get_text(strip=True)
                            if text:
                                # Clean up extra whitespace and special characters
                                text = " ".join(text.split())
                                sections.append(text)

                if sections:
                    requirements.append({"title": title, "sections": sections})

    except Exception as e:
        logger.error(f"Error extracting requirements: {e}")

    return requirements
