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


def scrape_adea_programs(url: str) -> List[Dict]:
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

                    if header_text == "Application Deadline":
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


def extract_international_eligibility_content(content) -> List[str]:
    """Extract and format International Student Eligibility content into a single section."""
    sections = []

    try:
        # Extract paragraphs first
        paragraphs = content.find_all("p")
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                # Clean up extra whitespace and special characters
                text = " ".join(text.split())
                sections.append(text)

        # Extract list items and format them properly
        lists = content.find_all("ul")
        for ul in lists:
            items = ul.find_all("li")
            if items:
                # Check if there's a preceding paragraph that introduces the list
                list_items = []
                for li in items:
                    text = li.get_text(strip=True)
                    if text:
                        text = " ".join(text.split())
                        list_items.append(text)

                # If we have list items, format them as a single sentence
                if list_items:
                    # Find the paragraph that introduces the list (usually ends with ":")
                    intro_paragraph = None
                    for section in sections:
                        if section.endswith(":"):
                            intro_paragraph = section
                            break

                    if intro_paragraph:
                        # Remove the intro paragraph from sections and combine with list
                        sections = [s for s in sections if s != intro_paragraph]
                        combined_text = f"{intro_paragraph} {', '.join(list_items)}"
                        sections.append(combined_text)
                    else:
                        # If no intro paragraph, just add the list items
                        sections.extend(list_items)

    except Exception as e:
        logger.error(f"Error extracting international eligibility content: {e}")

    return sections


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

                # Clean up tab characters and extra whitespace from name
                contact_person["name"] = " ".join(contact_person["name"].split())
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
                elif "International Student Eligibility" in title:
                    # Special handling for International Student Eligibility
                    sections = extract_international_eligibility_content(content)
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


def scrape_sdn_dental_schools(url: str) -> List[Dict]:
    """Scrape Student Doctor Network dental schools from the website and return structured data."""
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

        # Navigate to the SDN dental schools page
        driver.get(url)

        # Wait for the page to load and wait for school container to appear
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "schoolContainer")))

        # Wait additional 5 seconds for all content to load
        time.sleep(5)

        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Find all school items
        school_items = soup.find_all("div", class_="school-item")

        schools = []
        for item in school_items:
            try:
                school_data = extract_sdn_school_data(item)
                if school_data:
                    schools.append(school_data)
            except Exception as e:
                logger.error(f"Error extracting school data: {e}")
                continue

        return schools

    except Exception as e:
        logger.error(f"Error during SDN scraping: {e}")
        return []
    finally:
        if driver:
            driver.quit()


def extract_sdn_school_data(item) -> Dict:
    """Extract school data from a single school item and fetch detailed information."""
    try:
        if item is None:
            return None

        # Extract basic info from item
        name_element = item.find("h3", class_="name")
        name = ""
        detail_url = ""

        if name_element and name_element.find("a"):
            name = name_element.find("a").text.strip()
            detail_url = name_element.find("a").get("href")

        # Extract location
        location_element = item.find("p", class_="text-sm text-gray-600 mt-2")
        location = location_element.text.strip() if location_element else ""
        # Clean up newlines and extra whitespace
        location = " ".join(location.split())

        # Extract degree and type (currently not used in result)
        # degree_type_element = item.find("p", class_="text-blue-600 font-medium")
        # degree_type = degree_type_element.text.strip() if degree_type_element else ""

        # Extract data attributes
        data_degree = item.get("data-degree", "")
        data_state = item.get("data-state", "")
        data_type = item.get("data-type", "")
        data_id = item.get("data-id", "")
        data_country = item.get("data-country", "")

        # Fetch detailed school information
        detailed_info = fetch_sdn_detailed_school_info(detail_url)

        # Merge basic info with detailed info
        result = {
            "name": name,
            "location": location,
            "state": detailed_info.get("state", ""),
            "degree": data_degree,
            "school_type": detailed_info.get("school_type", ""),
            "detail_url": detail_url,
            "data_attributes": {
                "degree": data_degree,
                "state": data_state,
                "type": data_type,
                "id": data_id,
                "country": data_country,
            },
            "average_dat": detailed_info.get("average_dat", ""),
            "average_gpa": detailed_info.get("average_gpa", ""),
            "tuition_in_state": detailed_info.get("tuition_in_state", ""),
            "tuition_out_of_state": detailed_info.get("tuition_out_of_state", ""),
            "website": detailed_info.get("website", ""),
            "interview_feedback_summary": detailed_info.get(
                "interview_feedback_summary", ""
            ),
            "school_review_summary": detailed_info.get("school_review_summary", ""),
            "common_secondary_essay_questions": detailed_info.get(
                "common_secondary_essay_questions", []
            ),
            "about_the_school": detailed_info.get("about_the_school", ""),
            "curriculum": detailed_info.get("curriculum", ""),
            "facilities": detailed_info.get("facilities", ""),
            "insights": detailed_info.get("insights", {}),
            "school_address": detailed_info.get("school_address", ""),
            "links": detailed_info.get("links", []),
            "last_updated": detailed_info.get("last_updated", ""),
        }

        return result

    except Exception as e:
        logger.error(f"Error extracting SDN school data from item: {e}")
        return None


def fetch_sdn_detailed_school_info(detail_url: str) -> Dict:
    """Fetch detailed school information from the school detail page."""
    try:
        if not detail_url:
            return {}

        # Make HTTP request to get detailed school page
        response = requests.get(detail_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        result = {
            "state": "",
            "school_type": "",
            "average_dat": "",
            "average_gpa": "",
            "tuition_in_state": "",
            "tuition_out_of_state": "",
            "website": "",
            "interview_feedback_summary": "",
            "school_review_summary": "",
            "common_secondary_essay_questions": [],
            "about_the_school": "",
            "curriculum": "",
            "facilities": "",
            "insights": {},
            "school_address": "",
            "links": [],
            "last_updated": "",
        }

        # Extract location and state
        location_element = soup.find("p", class_="text-green-600 font-semibold mt-4")
        if location_element:
            location_text = location_element.text.strip()
            # Clean up newlines and extra whitespace
            location_text = " ".join(location_text.split())
            # Extract state from location (e.g., "Mesa, AZ" -> "AZ")
            if "," in location_text:
                result["state"] = location_text.split(",")[-1].strip()

        # Extract school type
        type_element = soup.find("div", class_="hidden md:flex gap-1")
        if type_element:
            school_type_text = type_element.text.strip()
            # Clean up newlines and extra whitespace, then format properly
            school_type_text = " ".join(school_type_text.split())
            # Replace "|" with "," and clean up extra spaces around commas
            school_type_text = school_type_text.replace("|", ",")
            # Clean up any extra spaces around commas
            school_type_text = ", ".join(
                [part.strip() for part in school_type_text.split(",")]
            )
            result["school_type"] = school_type_text

        # Extract school overview information
        overview_section = soup.find("div", class_="p-4")
        if overview_section:
            paragraphs = overview_section.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                if "Tuition (In State):" in text:
                    result["tuition_in_state"] = text.replace(
                        "Tuition (In State):", ""
                    ).strip()
                elif "Tuition (Out of State):" in text:
                    result["tuition_out_of_state"] = text.replace(
                        "Tuition (Out of State):", ""
                    ).strip()
                elif "Website:" in text:
                    link = p.find("a", href=True)
                    if link:
                        result["website"] = link.get("href")

        # Also check the school overview section more broadly
        school_overview = soup.find("h3", string="School Overview")
        if school_overview:
            overview_div = school_overview.find_parent("div")
            if overview_div:
                paragraphs = overview_div.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if "Tuition (In State):" in text:
                        result["tuition_in_state"] = text.replace(
                            "Tuition (In State):", ""
                        ).strip()
                    elif "Tuition (Out of State):" in text:
                        result["tuition_out_of_state"] = text.replace(
                            "Tuition (Out of State):", ""
                        ).strip()
                    elif "Website:" in text:
                        link = p.find("a", href=True)
                        if link:
                            result["website"] = link.get("href")

        # Fallback: search for tuition and website anywhere in the document
        if (
            not result["tuition_in_state"]
            or not result["tuition_out_of_state"]
            or not result["website"]
        ):
            all_paragraphs = soup.find_all("p")
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                if "Tuition (In State):" in text and not result["tuition_in_state"]:
                    result["tuition_in_state"] = text.replace(
                        "Tuition (In State):", ""
                    ).strip()
                elif (
                    "Tuition (Out of State):" in text
                    and not result["tuition_out_of_state"]
                ):
                    result["tuition_out_of_state"] = text.replace(
                        "Tuition (Out of State):", ""
                    ).strip()
                elif "Website:" in text and not result["website"]:
                    link = p.find("a", href=True)
                    if link:
                        result["website"] = link.get("href")

        # Extract application information
        app_section = soup.find("div", class_="p-4 rounded-lg gap-4")
        if app_section:
            paragraphs = app_section.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                if "Average DAT:" in text:
                    result["average_dat"] = text.replace("Average DAT:", "").strip()
                elif "Average GPA:" in text:
                    result["average_gpa"] = text.replace("Average GPA:", "").strip()

        # Extract interview feedback summary
        interview_section = soup.find(
            "div", class_="mt-6 p-4 bg-gray-100 rounded-lg flex flex-col"
        )
        if interview_section:
            summary_p = interview_section.find("p", class_="text-gray-700 flex-1")
            if summary_p:
                result["interview_feedback_summary"] = summary_p.text.strip()

        # Extract school review summary
        review_sections = soup.find_all(
            "div", class_="mt-6 p-4 bg-gray-100 rounded-lg flex flex-col"
        )
        if len(review_sections) > 1:
            review_section = review_sections[1]
            summary_p = review_section.find("p", class_="text-gray-700 flex-1")
            if summary_p:
                result["school_review_summary"] = summary_p.text.strip()

        # Extract common secondary essay questions
        essay_section = soup.find("div", class_="mt-6 p-4 bg-gray-100 rounded-lg")
        if (
            essay_section
            and "Most Common Secondary Essay Questions" in essay_section.get_text()
        ):
            essay_list = essay_section.find(
                "ul", class_="text-gray-700 text-sm space-y-2"
            )
            if essay_list:
                questions = []
                for li in essay_list.find_all("li"):
                    question_text = li.get_text(strip=True)
                    if question_text:
                        # Remove the number prefix (e.g., "1. " -> "")
                        if ". " in question_text:
                            question_text = question_text.split(". ", 1)[1]
                        questions.append(question_text)
                result["common_secondary_essay_questions"] = questions

        # Extract about the school, curriculum, and facilities
        sections = soup.find_all("div", class_="mt-6 p-2")
        for section in sections:
            heading = section.find("h3", class_="text-lg font-semibold")
            if heading:
                heading_text = heading.text.strip()
                content_p = section.find("p", class_="text-gray-700 break-words")
                if content_p:
                    content_text = content_p.text.strip()
                    if heading_text == "About the School":
                        result["about_the_school"] = content_text
                    elif heading_text == "Curriculum":
                        result["curriculum"] = content_text
                    elif heading_text == "Facilities":
                        result["facilities"] = content_text

        # Extract insights
        insights_section = soup.find(
            "div", class_="bg-white p-2 md:p-6 rounded-lg shadow-md w-full"
        )
        if insights_section and "SDN Insights" in insights_section.get_text():
            insights = {}
            insight_items = insights_section.find_all("div", class_="flex items-start")
            for item in insight_items:
                text_content = item.get_text(strip=True)
                if "Cost of Attendance:" in text_content:
                    # Extract cost from the text
                    cost_match = (
                        text_content.split("Cost of Attendance:")[1].split()[0]
                        if "Cost of Attendance:" in text_content
                        else ""
                    )
                    insights["cost_of_attendance"] = cost_match
                elif "Cost of Living:" in text_content:
                    cost_living = (
                        text_content.split("Cost of Living:")[1].strip()
                        if "Cost of Living:" in text_content
                        else ""
                    )
                    insights["cost_of_living"] = cost_living
                elif "Environment:" in text_content:
                    environment = (
                        text_content.split("Environment:")[1].strip()
                        if "Environment:" in text_content
                        else ""
                    )
                    insights["environment"] = environment
            result["insights"] = insights

        # Extract school address
        address_section = soup.find(
            "div", class_="p-2 md:p-6 rounded-lg shadow-md w-full mb-4 mt-4"
        )
        if address_section and "School Address:" in address_section.get_text():
            address_link = address_section.find("a", target="_blank")
            if address_link:
                address_text = address_link.text.strip()
                # Clean up newlines and extra whitespace
                result["school_address"] = " ".join(address_text.split())

        # Extract links
        links_section = soup.find(
            "div", class_="bg-white p-2 md:p-6 rounded-lg shadow-md w-full mt-4"
        )
        if links_section and "Links" in links_section.get_text():
            links = []
            links_list = links_section.find(
                "ul", class_="text-gray-700 text-sm space-y-1 mt-2"
            )
            if links_list:
                for li in links_list.find_all("li"):
                    link = li.find("a", href=True)
                    if link:
                        links.append(
                            {"label": link.text.strip(), "url": link.get("href")}
                        )
            result["links"] = links

        # Extract last updated
        last_updated_p = soup.find("p", class_="mt-4 text-end")
        if last_updated_p and "Last Updated:" in last_updated_p.get_text():
            result["last_updated"] = (
                last_updated_p.get_text().replace("Last Updated:", "").strip()
            )

        return result

    except Exception as e:
        logger.error(f"Error fetching detailed SDN school info from {detail_url}: {e}")
        return {}
