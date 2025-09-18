import pytest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from src.navigator_dagster.defs.utils import (
    extract_program_data,
    fetch_detailed_program_info,
    extract_contact_info,
    extract_program_info_table,
    extract_requirements,
    extract_international_eligibility_content,
    scrape_sdn_dental_schools,
    extract_sdn_school_data,
    fetch_sdn_detailed_school_info,
)


class TestUtilsParsing:
    """Test parsing functionality of utils.py functions."""

    @pytest.fixture
    def sample_program_card_html(self):
        """Sample program card HTML for testing."""
        return """
        <article class="adea-pgrm">
            <h3 class="adea-pgrm__title__heading">
                <a href="/PASS/programs/illinois-masonic-medical-center-anesthesiology">Advocate Illinois Masonic Medical Center</a>
            </h3>
            <ul class="adea-pgram__title__meta">
                <li>Illinois</li>
                <li><span class="ui-badge"><span class="ui-badge__text">Anesthesiology</span></span></li>
            </ul>
            <div class="adea-pgrm__info">
                <div class="adea-pgrm__info__row">
                    <div class="adea-pgrm__info__col--header">Program Size</div>
                    <div class="adea-pgrm__info__col--value">2</div>
                </div>
                <div class="adea-pgrm__info__row">
                    <div class="adea-pgrm__info__col--header">Program Length</div>
                    <div class="adea-pgrm__info__col--value">36 months</div>
                </div>
                <div class="adea-pgrm__info__row">
                    <div class="adea-pgrm__info__col--header">Application Deadline</div>
                    <div class="adea-pgrm__info__col--value">October 1</div>
                </div>
                <div class="adea-pgrm__info__row">
                    <div class="adea-pgrm__info__col--header">Program Start</div>
                    <div class="adea-pgrm__info__col--value">July 1</div>
                </div>
            </div>
        </article>
        """

    @pytest.fixture
    def sample_detailed_program_html(self):
        """Sample detailed program HTML for testing."""
        return """
        <div class="adea-pgrm-dtl__container svelte-63rybf">
            <div class="adea-pgrm-dtl__updated svelte-63rybf">
                <span>Last updated on May 1, 2025.</span>
            </div>
            <div class="adea-pgrm-dtl__header svelte-63rybf">
                <div class="adea-pgrm-dtl__header__content svelte-63rybf">
                    <h1 class="adea-pgrm-dtl__heading svelte-63rybf">Advocate Illinois Masonic Medical Center</h1>
                    <ul class="adea-pgrm-dtl__header__meta ui-reset svelte-63rybf">
                        <li class="svelte-63rybf">Illinois</li>
                        <li class="svelte-63rybf">
                            <span class="ui-badge svelte-kwl03w">
                                <span class="ui-badge__text">Anesthesiology</span>
                            </span>
                        </li>
                        <li class="svelte-63rybf">
                            <a href="https://www.advocatehealth.com/education/residency-opportunities/advocate-illinois-masonic-medical-center/residency/dental-anesthesiology/" target="_blank" rel="noopener noreferrer" class="svelte-4i3h5u ui-aligncenter">
                                <span>advocatehealth.com</span>
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="adea-pgrm-dtl__meta svelte-63rybf">
                <div role="table" aria-label="Information for Program Advocate Illinois Masonic Medical Center" class="adea-pgrm__info svelte-s8v6de larger">
                    <div role="rowgroup" class="adea-pgrm__info__rowgroup svelte-s8v6de">
                        <div role="row" class="adea-pgrm__info__row svelte-s8v6de">
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--header svelte-s8v6de">
                                <span>Program Size</span>
                            </div>
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--value svelte-s8v6de">
                                <span>2</span>
                            </div>
                        </div>
                        <div role="row" class="adea-pgrm__info__row svelte-s8v6de">
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--header svelte-s8v6de">
                                <span>Program Length</span>
                            </div>
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--value svelte-s8v6de">
                                <span>36 months</span>
                            </div>
                        </div>
                        <div role="row" class="adea-pgrm__info__row svelte-s8v6de">
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--header svelte-s8v6de">
                                <span>Application Deadline</span>
                            </div>
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--value svelte-s8v6de">
                                <span>October 1</span>
                            </div>
                        </div>
                        <div role="row" class="adea-pgrm__info__row svelte-s8v6de">
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--header svelte-s8v6de">
                                <span>Program Start</span>
                            </div>
                            <div class="adea-pgrm__info__col adea-pgrm__info__col--value svelte-s8v6de">
                                <span>July 1</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="adea-pgrm-dtl__main svelte-63rybf hasSidebar">
                <div class="adea-pgrm-dtl-contact svelte-63rybf">
                    <div class="adea-pgrm-dtl-contact__container svelte-63rybf">
                        <div class="adea-pgrm-dtl-contact__main svelte-63rybf">
                            <h2 class="adea-pgrm-dtl-contact__heading svelte-63rybf">Program Contact</h2>
                            <div class="adea-pgrm-dtl-contact__info svelte-63rybf">
                                <div class="adea-pgrm-dtl-contact__name">
                                    <span class="svelte-63rybf"><strong>Kenneth Kromash</strong>  DDS</span>
                                    <span class="svelte-63rybf">Program Director</span>
                                </div>
                                <div class="adea-pgrm-dtl-contact__address">
                                    <p>The current address is 913 W. Wellington, Chicago, Illinois, 60657.&nbsp;</p>
                                </div>
                                <div class="adea-pgrm-dtl-contact__actions svelte-63rybf">
                                    <span class="svelte-63rybf">
                                        <a href="mailto:kenneth.kromash@aah.org">kenneth.kromash@aah.org</a>
                                    </span>
                                    <span class="svelte-63rybf">
                                        <a href="tel:773-871-6138">773-871-6138</a>
                                    </span>
                                </div>
                                <div class="adea-pgrm-dtl-contact__name">
                                    <span class="svelte-63rybf"><strong>Nikki Pasic</strong></span>
                                    <span class="svelte-63rybf">Program Coordinator</span>
                                </div>
                                <div class="adea-pgrm-dtl-contact__actions svelte-63rybf">
                                    <span class="svelte-63rybf">
                                        <a href="mailto:nikki.pasic@aah.org">nikki.pasic@aah.org</a>
                                    </span>
                                    <span class="svelte-63rybf">
                                        <a href="tel:773-871-6138">773-871-6138</a>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="adea-pgrm-dtl__body svelte-63rybf">
                <div class="adea-pgrm-dtl__section svelte-63rybf">
                    <div class="adea-pgrm-dtl__section__content">
                        <p>AIMMC and the Departments of Dentistry and Anesthesiology are proud to sponsor a 36-month, two resident per year Dental Anesthesiology Residency program which meets all the criteria for examination by the American Dental Board of Anesthesiology. AIMMC has a long history of training dentist anesthesiologists, previously sponsoring a 24-month dental anesthesiology residency from the early 1980s to 2004 prior to specialty recognition. Under the leadership of Dental Anesthesiology Program Director, Dr. Ken Kromash, who completed a two-year dental anesthesiology residency at AIMMC in 1992, the dental anesthesiology program has been reformed and launched July 1, 2019. The program will prepare the dentist anesthesiologist to comprehensively manage pain and anxiety for children, adults and patients with special needs in both the inpatient and ambulatory settings for dental and maxillofacial procedures.&nbsp;</p>
                        <p>Dental anesthesiology residents will receive didactic and clinical training in the administration of deep sedation/general anesthesia and other forms of pain anxiety control for ambulatory dental patients on several rotations. Residents will receive a significant portion of their dental anesthesia training in the Advocate Dental Center which is located on the AIMMC campus.</p>
                        <p>AIMMC's Department of Anesthesia and the affiliated Anesthesia Residency program, which closely support the dental anesthesiology residency, offers a broad-based residency program, encompassing the entire spectrum of anesthesiology specialties. Our website is now available at <a href="https://www.advocatehealth.com/education/residency-opportunities/advocate-illinois-masonic-medical-center/residency/dental-anesthesiology/">https://www.advocatehealth.com/education/residency-opportunities/advocate-illinois-masonic-medical-center/residency/dental-anesthesiology/</a></p>
                        <p>For further information/description, please contact Program Director Dr. Ken Kromash at kenneth.kromash@aah.org.</p>
                    </div>
                </div>
                <div class="adea-pgrm-dtl__section svelte-63rybf">
                    <h2 class="adea-pgrm-dtl__section__heading svelte-63rybf">Program Information</h2>
                    <div class="adea-pgrm-dtl__section__content">
                        <div class="ui-program-table svelte-haoeb7">
                            <table aria-label="Information about program Advocate Illinois Masonic Medical Center" class="svelte-haoeb7">
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Accreditation</th>
                                    <td class="svelte-haoeb7">This program is offered by a CODA-accredited institution</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Program Type</th>
                                    <td class="svelte-haoeb7">Anesthesiology</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Program Code</th>
                                    <td class="svelte-haoeb7">ANES16</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Degrees Offered</th>
                                    <td class="svelte-haoeb7">Certificate</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Program Size</th>
                                    <td class="svelte-haoeb7">2</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Program Length</th>
                                    <td class="svelte-haoeb7">36 months</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Application Deadline</th>
                                    <td class="svelte-haoeb7">October 1</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Program Start Date</th>
                                    <td class="svelte-haoeb7">July 1</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Supplemental Application</th>
                                    <td class="svelte-haoeb7">No</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Supplemental Fee</th>
                                    <td class="svelte-haoeb7">No</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Stipend Offered</th>
                                    <td class="svelte-haoeb7">Yes</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Match Participating</th>
                                    <td class="svelte-haoeb7">Yes</td>
                                </tr>
                                <tr class="svelte-haoeb7">
                                    <th scope="row" class="svelte-haoeb7">Program Website</th>
                                    <td class="svelte-haoeb7">
                                        <a href="https://www.advocatehealth.com/education/residency-opportunities/advocate-illinois-masonic-medical-center/residency/dental-anesthesiology/" target="_blank" rel="noopener noreferrer" class="svelte-4i3h5u ui-aligncenter">
                                            <span>advocatehealth.com</span>
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="adea-pgrm-dtl__section adea-pgrm-dtl__section--accordions svelte-63rybf">
                    <h2 class="adea-pgrm-dtl__section__heading svelte-63rybf">Application Requirements</h2>
                    <div class="adea-pgrm-dtl__section__content svelte-63rybf">
                        <div class="adea-pgrm-accordion svelte-1ideh37 enabled">
                            <h3 class="adea-pgrm-accordion__heading svelte-1ideh37">Required Standardized Tests</h3>
                            <div id="adea-pgrm-accdn-reqstandtests" class="adea-pgrm-accordion__content svelte-1ideh37">
                                <div class="adea-pgrm-dtl__checks svelte-63rybf">
                                    <ul class="adea-pgrm-checks svelte-mzp6lt">
                                        <li>
                                            <span class="adea-pgrm-check svelte-10mqztr">
                                                <span class="ui-checkmarkCircle svelte-zf90l5">
                                                    <svg aria-hidden="true" width="1em" height="1em" viewBox="0 0 16 12" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M14.667 1 5.5 10.167 1.333 6" stroke-width="1.67" stroke-linecap="round" stroke-linejoin="round"></path>
                                                    </svg>
                                                </span>
                                                <span>NBDE1</span>
                                            </span>
                                        </li>
                                        <li>
                                            <span class="adea-pgrm-check svelte-10mqztr">
                                                <span class="ui-checkmarkCircle svelte-zf90l5">
                                                    <svg aria-hidden="true" width="1em" height="1em" viewBox="0 0 16 12" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M14.667 1 5.5 10.167 1.333 6" stroke-width="1.67" stroke-linecap="round" stroke-linejoin="round"></path>
                                                    </svg>
                                                </span>
                                                <span>NBDE2</span>
                                            </span>
                                        </li>
                                        <li>
                                            <span class="adea-pgrm-check svelte-10mqztr">
                                                <span class="ui-checkmarkCircle svelte-zf90l5">
                                                    <svg aria-hidden="true" width="1em" height="1em" viewBox="0 0 16 12" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M14.667 1 5.5 10.167 1.333 6" stroke-width="1.67" stroke-linecap="round" stroke-linejoin="round"></path>
                                                    </svg>
                                                </span>
                                                <span>Passing the INBDE before matriculation into the advanced dental education program</span>
                                            </span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="adea-pgrm-accordion svelte-1ideh37 enabled">
                            <h3 class="adea-pgrm-accordion__heading svelte-1ideh37">Transcript Evaluation and Instructions</h3>
                            <div id="adea-pgrm-accdn-transcriptreq" class="adea-pgrm-accordion__content svelte-1ideh37">
                                <p>Undergraduate college and dental school transcripts are required.</p>
                            </div>
                        </div>
                        <div class="adea-pgrm-accordion svelte-1ideh37 enabled">
                            <h3 class="adea-pgrm-accordion__heading svelte-1ideh37">Letters of Evaluation Instructions</h3>
                            <div id="adea-pgrm-accdn-evalinstructions" class="adea-pgrm-accordion__content svelte-1ideh37">
                                <p>Letters of evaluation from dentist anesthesiologists who know you well are strongly encouraged. At least one letter <strong>MUST</strong> be from a dentist anesthesiologist.</p>
                            </div>
                        </div>
                        <div class="adea-pgrm-accordion svelte-1ideh37 enabled">
                            <h3 class="adea-pgrm-accordion__heading svelte-1ideh37">Other Requirement Instructions</h3>
                            <div id="adea-pgrm-accdn-otherinstructions" class="adea-pgrm-accordion__content svelte-1ideh37">
                                <p>Applicants must have a minimum of 40 hours of experience shadowing or working with dentist anesthesiologists.</p>
                                <p>Applicants who are chosen for an interview will be required to submit a video presentation no longer than seven minutes answering specific questions. Detailed instructions will be communicated to all applicants.&nbsp;</p>
                            </div>
                        </div>
                        <div class="adea-pgrm-accordion svelte-1ideh37 enabled">
                            <h3 class="adea-pgrm-accordion__heading svelte-1ideh37">International Student Eligibility</h3>
                            <div id="adea-pgrm-accdn-internationalstudents" class="adea-pgrm-accordion__content svelte-1ideh37">
                                <p class="svelte-63rybf">This program will consider applicants who graduated, or plan to graduate, from a <a href="https://coda.ada.org/">non-CODA accredited dental school</a>: No</p>
                                <p class="svelte-63rybf">Applicants are eligible to enroll if they are:</p>
                                <ul class="svelte-63rybf">
                                    <li>US Citizen</li>
                                    <li>US Permanent Resident</li>
                                    <li>Canadian Citizen</li>
                                    <li>Non-US Citizen/Resident (program offers sponsorship)</li>
                                    <li>Illinois Masonic sponsors J-1 visas only.</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="adea-pgrm-dtl__section svelte-63rybf">
                    <h2 class="adea-pgrm-dtl__section__heading svelte-63rybf">Interview Schedule</h2>
                    <div class="adea-pgrm-dtl__section__content">
                        <p>Interviews will be held virtually on Saturday, November 1, 2025.</p>
                    </div>
                </div>
                <div class="adea-pgrm-dtl__section svelte-63rybf">
                    <h2 class="adea-pgrm-dtl__section__heading svelte-63rybf">Additional Information</h2>
                    <div class="adea-pgrm-dtl__section__content">
                        <p>The NBME CBSE scores are not required for consideration at Illinois Masonic.&nbsp; There is a possibility that the exam will be a requirement in the future.&nbsp; Those applicants from schools which are pass/fail or do not rank students are <strong>strongly&nbsp; encouraged to take the CBSE</strong>.&nbsp; These scores will serve to better distinguish those applicants.&nbsp; For those applicants who wish to further support their application, submitting good scores from the exam can only help.&nbsp; A lower score will not count against you.&nbsp; The ADAT is <strong>not</strong> recommended and will be given no weight. Prior exposure to dental anesthesia is strongly encouraged. Applicants accepted for the residency must be available for a two week orientation prior to the official start date of July 1, 2026. Personal statements must be your own original thoughts and writing.&nbsp; Use of AI (Chat GPT, Google Bard, etc.) will be grounds for dismissal from consideration.</p>
                    </div>
                </div>
            </div>
        </div>
        """

    def test_extract_program_data_basic_info(self, sample_program_card_html):
        """Test extraction of basic program information from card."""
        soup = BeautifulSoup(sample_program_card_html, "html.parser")
        card = soup.find("article", class_="adea-pgrm")

        with patch(
            "src.navigator_dagster.defs.utils.fetch_detailed_program_info"
        ) as mock_fetch:
            mock_fetch.return_value = {}

            result = extract_program_data(card)

            assert result is not None
            assert result["name"] == "Advocate Illinois Masonic Medical Center"
            assert result["state"] == "Illinois"
            assert result["type"] == "Anesthesiology"
            assert (
                result["adea_url"]
                == "https://programs.adea.org/PASS/programs/illinois-masonic-medical-center-anesthesiology"
            )
            # Size and length are now only in information object
            assert "size" not in result
            assert "length" not in result
            assert result["application_deadline"] == "October 1"
            assert result["start_date"] == "July 1"

    def test_fetch_detailed_program_info_last_updated(
        self, sample_detailed_program_html
    ):
        """Test extraction of last updated date."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_detailed_program_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_detailed_program_info("https://programs.adea.org/test")

            assert result["last_updated"] == "Last updated on May 1, 2025."

    def test_fetch_detailed_program_info_website_url(
        self, sample_detailed_program_html
    ):
        """Test extraction of website URL from header."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_detailed_program_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_detailed_program_info("https://programs.adea.org/test")

            assert (
                result["website_url"]
                == "https://www.advocatehealth.com/education/residency-opportunities/advocate-illinois-masonic-medical-center/residency/dental-anesthesiology/"
            )

    def test_fetch_detailed_program_info_description(
        self, sample_detailed_program_html
    ):
        """Test extraction of program description."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_detailed_program_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_detailed_program_info("https://programs.adea.org/test")

            description = result["description"]
            assert (
                "AIMMC and the Departments of Dentistry and Anesthesiology are proud to sponsor"
                in description
            )
            assert (
                "36-month, two resident per year Dental Anesthesiology Residency program"
                in description
            )
            assert (
                "The program will prepare the dentist anesthesiologist to comprehensively manage pain and anxiety"
                in description
            )

    def test_extract_contact_info(self, sample_detailed_program_html):
        """Test extraction of contact information."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")
        contact_element = soup.find("div", class_="adea-pgrm-dtl-contact")

        result = extract_contact_info(contact_element)

        assert (
            result["address"]
            == "The current address is 913 W. Wellington, Chicago, Illinois, 60657."
        )
        assert len(result["points_of_contact"]) == 2

        # Test first contact person
        contact1 = result["points_of_contact"][0]
        assert contact1["name"] == "Kenneth Kromash DDS"  # Extra spaces cleaned
        assert contact1["title"] == "Program Director"
        assert contact1["email"] == "kenneth.kromash@aah.org"
        assert contact1["phone"] == "773-871-6138"

        # Test second contact person
        contact2 = result["points_of_contact"][1]
        assert contact2["name"] == "Nikki Pasic"
        assert contact2["title"] == "Program Coordinator"
        assert contact2["email"] == "nikki.pasic@aah.org"
        assert contact2["phone"] == "773-871-6138"

    def test_extract_program_info_table(self, sample_detailed_program_html):
        """Test extraction of program information table."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")
        table = soup.find("table")

        result = extract_program_info_table(table)

        assert (
            result["accreditation"]
            == "This program is offered by a CODA-accredited institution"
        )
        assert result["program_type"] == "Anesthesiology"
        assert result["program_code"] == "ANES16"
        assert result["degrees_offered"] == "Certificate"
        assert result["program_size"] == "2"
        assert result["program_length"] == "36 months"
        assert result["application_deadline"] == "October 1"
        assert result["program_start_date"] == "July 1"
        assert result["supplemental_application"] == "no"
        assert result["supplemental_fee"] == "no"
        assert result["stipend_offered"] == "yes"
        assert result["match_participating"] == "yes"
        assert (
            result["program_website"]
            == "https://www.advocatehealth.com/education/residency-opportunities/advocate-illinois-masonic-medical-center/residency/dental-anesthesiology/"
        )

    def test_extract_requirements(self, sample_detailed_program_html):
        """Test extraction of requirements from accordion sections."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")
        accordion_section = soup.find(
            "div", class_="adea-pgrm-dtl__section--accordions"
        )

        result = extract_requirements(accordion_section)

        assert len(result) == 5

        # Test Required Standardized Tests
        req1 = result[0]
        assert req1["title"] == "Required Standardized Tests"
        assert "NBDE1" in req1["sections"]
        assert "NBDE2" in req1["sections"]
        assert (
            "Passing the INBDE before matriculation into the advanced dental education program"
            in req1["sections"]
        )

        # Test Transcript Evaluation
        req2 = result[1]
        assert req2["title"] == "Transcript Evaluation and Instructions"
        assert (
            "Undergraduate college and dental school transcripts are required."
            in req2["sections"]
        )

        # Test Letters of Evaluation
        req3 = result[2]
        assert req3["title"] == "Letters of Evaluation Instructions"
        assert (
            "Letters of evaluation from dentist anesthesiologists who know you well are strongly encouraged"
            in req3["sections"][0]
        )

        # Test Other Requirements
        req4 = result[3]
        assert req4["title"] == "Other Requirement Instructions"
        assert (
            "Applicants must have a minimum of 40 hours of experience shadowing"
            in req4["sections"][0]
        )
        assert "video presentation no longer than seven minutes" in req4["sections"][1]

        # Test International Student Eligibility
        req5 = result[4]
        assert req5["title"] == "International Student Eligibility"
        assert (
            "This program will consider applicants who graduated, or plan to graduate, from anon-CODA accredited dental school: No"
            in req5["sections"][0]
        )
        # The list items are now combined into a single section
        assert "US Citizen" in req5["sections"][1]
        assert "US Permanent Resident" in req5["sections"][1]
        assert "Canadian Citizen" in req5["sections"][1]

    def test_fetch_detailed_program_info_interview_schedule(
        self, sample_detailed_program_html
    ):
        """Test extraction of interview schedule and additional information."""
        soup = BeautifulSoup(sample_detailed_program_html, "html.parser")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_detailed_program_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_detailed_program_info("https://programs.adea.org/test")

            # Check that interview schedule and additional info are added to requirements
            requirements = result["requirements"]
            interview_req = next(
                (req for req in requirements if req["title"] == "Interview Schedule"),
                None,
            )
            additional_req = next(
                (
                    req
                    for req in requirements
                    if req["title"] == "Additional Information"
                ),
                None,
            )

            assert interview_req is not None
            assert (
                "Interviews will be held virtually on Saturday, November 1, 2025."
                in interview_req["sections"]
            )

            assert additional_req is not None
            assert (
                "The NBME CBSE scores are not required for consideration at Illinois Masonic"
                in additional_req["sections"][0]
            )
            assert (
                "Personal statements must be your own original thoughts and writing"
                in additional_req["sections"][0]
            )

    def test_extract_program_data_integration(
        self, sample_program_card_html, sample_detailed_program_html
    ):
        """Test complete integration of extract_program_data with detailed info."""
        soup = BeautifulSoup(sample_program_card_html, "html.parser")
        card = soup.find("article", class_="adea-pgrm")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_detailed_program_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = extract_program_data(card)

            # Test basic info
            assert result["name"] == "Advocate Illinois Masonic Medical Center"
            assert result["state"] == "Illinois"
            assert result["type"] == "Anesthesiology"
            # Size and length are now only in information object
            assert "size" not in result
            assert "length" not in result

            # Test detailed info
            assert result["last_updated"] == "Last updated on May 1, 2025."
            assert (
                "AIMMC and the Departments of Dentistry and Anesthesiology are proud to sponsor"
                in result["description"]
            )

            # Test contact info
            assert len(result["contact"]["points_of_contact"]) == 2
            assert (
                result["contact"]["address"]
                == "The current address is 913 W. Wellington, Chicago, Illinois, 60657."
            )

            # Test requirements
            assert len(result["requirements"]) >= 5
            assert any(
                req["title"] == "Required Standardized Tests"
                for req in result["requirements"]
            )
            assert any(
                req["title"] == "Interview Schedule" for req in result["requirements"]
            )

            # Test information table
            assert "accreditation" in result["information"]
            assert result["information"]["program_type"] == "Anesthesiology"
            assert result["information"]["stipend_offered"] == "yes"

    def test_extract_program_data_error_handling(self):
        """Test error handling in extract_program_data."""
        # Test with invalid card
        result = extract_program_data(None)
        assert result is None

        # Test with empty card - should return a dict with empty values
        soup = BeautifulSoup("<div></div>", "html.parser")
        result = extract_program_data(soup)
        assert result is not None
        assert isinstance(result, dict)

    def test_fetch_detailed_program_info_error_handling(self):
        """Test error handling in fetch_detailed_program_info."""
        # Test with empty URL
        result = fetch_detailed_program_info("")
        assert result == {}

        # Test with HTTP error
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("HTTP Error")
            result = fetch_detailed_program_info("https://test.com")
            assert result == {}

    def test_extract_contact_info_error_handling(self):
        """Test error handling in extract_contact_info."""
        # Test with None input
        result = extract_contact_info(None)
        assert result == {"points_of_contact": [], "address": ""}

        # Test with empty element
        soup = BeautifulSoup("<div></div>", "html.parser")
        result = extract_contact_info(soup)
        assert result == {"points_of_contact": [], "address": ""}

    def test_extract_program_info_table_error_handling(self):
        """Test error handling in extract_program_info_table."""
        # Test with None input
        result = extract_program_info_table(None)
        assert result == {}

        # Test with empty table
        soup = BeautifulSoup("<table></table>", "html.parser")
        result = extract_program_info_table(soup)
        assert result == {}

    def test_extract_requirements_error_handling(self):
        """Test error handling in extract_requirements."""
        # Test with None input
        result = extract_requirements(None)
        assert result == []

        # Test with empty section
        soup = BeautifulSoup("<div></div>", "html.parser")
        result = extract_requirements(soup)
        assert result == []

    def test_extract_program_data_no_redundant_size_length(
        self, sample_program_card_html
    ):
        """Test that size and length are not included at root level."""
        soup = BeautifulSoup(sample_program_card_html, "html.parser")
        card = soup.find("article", class_="adea-pgrm")

        with patch(
            "src.navigator_dagster.defs.utils.fetch_detailed_program_info"
        ) as mock_fetch:
            mock_fetch.return_value = {
                "information": {
                    "size": "2",
                    "length": "36 months",
                    "program_size": "2",
                    "program_length": "36 months",
                }
            }

            result = extract_program_data(card)

            # Check that size and length are NOT at root level
            assert "size" not in result
            assert "length" not in result

            # Check that they exist in information object
            assert "information" in result
            assert "size" in result["information"]
            assert "length" in result["information"]

    def test_extract_contact_info_cleans_tab_characters(self):
        """Test that contact names have tab characters removed."""
        html_with_tabs = """
        <div class="adea-pgrm-dtl-contact">
            <div class="adea-pgrm-dtl-contact__name">
                <span><strong>Dr.  Marissa Rubenstein\n\t\t\t\t\t\t\t\t\t\t\t\t\t DMD</strong></span>
                <span>Program Director</span>
            </div>
            <div class="adea-pgrm-dtl-contact__actions">
                <span>
                    <a href="mailto:marissa.rubenstein@jefferson.edu">marissa.rubenstein@jefferson.edu</a>
                </span>
                <span>
                    <a href="tel:215-481-2193">215-481-2193</a>
                </span>
            </div>
        </div>
        """

        soup = BeautifulSoup(html_with_tabs, "html.parser")
        contact_element = soup.find("div", class_="adea-pgrm-dtl-contact")

        result = extract_contact_info(contact_element)

        assert len(result["points_of_contact"]) == 1
        contact = result["points_of_contact"][0]
        assert contact["name"] == "Dr. Marissa Rubenstein DMD"
        assert contact["title"] == "Program Director"
        assert contact["email"] == "marissa.rubenstein@jefferson.edu"
        assert contact["phone"] == "215-481-2193"

    def test_extract_international_eligibility_content_collapses_sections(self):
        """Test that International Student Eligibility content is properly collapsed."""
        html_content = """
        <div>
            <p>This program will consider applicants who graduated, or plan to graduate, from a non-CODA accredited dental school: No</p>
            <p>Applicants are eligible to enroll if they are:</p>
            <ul>
                <li>US Citizen</li>
                <li>US Permanent Resident</li>
                <li>Non-US Citizen/Resident (program offers sponsorship)</li>
                <li>Only applicants who graduated, or plan to graduate with a DDS or DMD degree from a U.S. CODA accredited dental school will be considered for acceptance.</li>
            </ul>
        </div>
        """

        soup = BeautifulSoup(html_content, "html.parser")
        result = extract_international_eligibility_content(soup)

        # Should have 2 sections: the first paragraph and the combined intro + list
        assert len(result) == 2
        assert (
            "This program will consider applicants who graduated, or plan to graduate, from a non-CODA accredited dental school: No"
            in result
        )
        assert (
            "Applicants are eligible to enroll if they are: US Citizen, US Permanent Resident, Non-US Citizen/Resident (program offers sponsorship), Only applicants who graduated, or plan to graduate with a DDS or DMD degree from a U.S. CODA accredited dental school will be considered for acceptance."
            in result
        )

    def test_extract_requirements_international_eligibility_special_handling(self):
        """Test that International Student Eligibility gets special handling in requirements extraction."""
        html_accordion = """
        <div class="adea-pgrm-dtl__section--accordions">
            <div class="adea-pgrm-accordion">
                <h3 class="adea-pgrm-accordion__heading">International Student Eligibility</h3>
                <div class="adea-pgrm-accordion__content">
                    <p>This program will consider applicants who graduated, or plan to graduate, from a non-CODA accredited dental school: No</p>
                    <p>Applicants are eligible to enroll if they are:</p>
                    <ul>
                        <li>US Citizen</li>
                        <li>US Permanent Resident</li>
                        <li>Non-US Citizen/Resident (program offers sponsorship)</li>
                        <li>Only applicants who graduated, or plan to graduate with a DDS or DMD degree from a U.S. CODA accredited dental school will be considered for acceptance.</li>
                    </ul>
                </div>
            </div>
        </div>
        """

        soup = BeautifulSoup(html_accordion, "html.parser")
        accordion_section = soup.find(
            "div", class_="adea-pgrm-dtl__section--accordions"
        )

        result = extract_requirements(accordion_section)

        assert len(result) == 1
        req = result[0]
        assert req["title"] == "International Student Eligibility"
        assert len(req["sections"]) == 2
        assert (
            "This program will consider applicants who graduated, or plan to graduate, from a non-CODA accredited dental school: No"
            in req["sections"]
        )
        assert (
            "Applicants are eligible to enroll if they are: US Citizen, US Permanent Resident, Non-US Citizen/Resident (program offers sponsorship), Only applicants who graduated, or plan to graduate with a DDS or DMD degree from a U.S. CODA accredited dental school will be considered for acceptance."
            in req["sections"]
        )

    def test_extract_international_eligibility_content_error_handling(self):
        """Test error handling in extract_international_eligibility_content."""
        # Test with None input
        result = extract_international_eligibility_content(None)
        assert result == []

        # Test with empty content
        soup = BeautifulSoup("<div></div>", "html.parser")
        result = extract_international_eligibility_content(soup)
        assert result == []

    def test_integration_all_fixes(self, sample_program_card_html):
        """Test integration of all fixes together."""
        soup = BeautifulSoup(sample_program_card_html, "html.parser")
        card = soup.find("article", class_="adea-pgrm")

        # Mock detailed info with the problematic data from the user's example
        mock_detailed_info = {
            "last_updated": "Last updated on August 30, 2024.",
            "description": "The Jefferson Abington Dental Residency Program is a comprehensive 1 year experience...",
            "website_url": "https://www.jeffersonhealth.org/about-us/academic-programs/graduate-medical-education/residency-programs/dentistry-residency-program",
            "information": {
                "size": "4",
                "length": "12 months",
                "program_size": "4",
                "program_length": "12 months",
                "application_deadline": "November 1",
                "program_start_date": "June 24",
                "program_type": "General Practice Residency",
                "program_code": "GPR654",
                "degrees_offered": "Certificate",
                "supplemental_application": "no",
                "supplemental_fee": "no",
                "stipend_offered": "yes",
                "match_participating": "yes",
                "program_website": "https://www.jeffersonhealth.org/about-us/academic-programs/graduate-medical-education/residency-programs/dentistry-residency-program",
            },
            "requirements": [
                {
                    "title": "Required Standardized Tests",
                    "sections": [
                        "INBDE",
                        "Passing the INBDE before matriculation into the advanced dental education program",
                    ],
                },
                {
                    "title": "International Student Eligibility",
                    "sections": [
                        "This program will consider applicants who graduated, or plan to graduate, from anon-CODA accredited dental school: No",
                        "Applicants are eligible to enroll if they are: US Citizen, US Permanent Resident, Non-US Citizen/Resident (program offers sponsorship), Only applicants who graduated, or plan to graduate with a DDS or DMD degree from a U.S. CODA accredited dental school will be considered for acceptance.",
                    ],
                },
            ],
            "contact": {
                "points_of_contact": [
                    {
                        "name": "Dr. Marissa Rubenstein DMD",
                        "title": "Program Director",
                        "email": "marissa.rubenstein@jefferson.edu",
                        "phone": "215-481-2193",
                    }
                ],
                "address": "Abington Memorial Hospital, 1200 Old York Rd., Dental Div./GR Fl. Arches , Abington, Pennsylvania, 19001",
            },
        }

        with patch(
            "src.navigator_dagster.defs.utils.fetch_detailed_program_info"
        ) as mock_fetch:
            mock_fetch.return_value = mock_detailed_info

            result = extract_program_data(card)

            # Test 1: No redundant size/length at root level
            assert "size" not in result
            assert "length" not in result
            assert "size" in result["information"]
            assert "length" in result["information"]

            # Test 2: Contact name is clean (no tabs)
            contact = result["contact"]["points_of_contact"][0]
            assert contact["name"] == "Dr. Marissa Rubenstein DMD"
            assert "\t" not in contact["name"]

            # Test 3: International Student Eligibility is properly collapsed
            intl_req = next(
                (
                    req
                    for req in result["requirements"]
                    if req["title"] == "International Student Eligibility"
                ),
                None,
            )
            assert intl_req is not None
            assert len(intl_req["sections"]) == 2
            assert (
                "Applicants are eligible to enroll if they are: US Citizen, US Permanent Resident, Non-US Citizen/Resident (program offers sponsorship), Only applicants who graduated, or plan to graduate with a DDS or DMD degree from a U.S. CODA accredited dental school will be considered for acceptance."
                in intl_req["sections"]
            )


class TestSDNScraping:
    """Test SDN dental schools scraping functionality."""

    @pytest.fixture
    def sample_sdn_school_item_html(self):
        """Sample SDN school item HTML for testing."""
        return """
        <div class="school-item flex border p-4 rounded-lg items-center space-x-4 mb-4" data-degree="DDS" data-state="4" data-type="1" data-id="189" data-country="US">
            <a class="flex-shrink-0 w-24 h-24" href="https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/a-t-still-university-arizona-school-of-dentistry-and-oral-health" aria-label="More about A. T. Still University - Arizona School of Dentistry and Oral Health">
                <div class="school_img flex items-center justify-center">
                    <img src="https://www.studentdoctor.net/schools-database/img/schools/ASDOH.jpg?v=2025-08-22 20:39:53" class="rounded-md object-contain" alt="A. T. Still University - Arizona School of Dentistry and Oral Health">
                </div>
            </a>
            <div class="flex-1">
                <h3 class="mt-2 font-semibold name">
                    <a href="https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/a-t-still-university-arizona-school-of-dentistry-and-oral-health" aria-label="More about A. T. Still University - Arizona School of Dentistry and Oral Health">A. T. Still University - Arizona School of Dentistry and Oral Health</a>
                </h3>
                <p class="text-sm text-gray-600 mt-2">
                    Mesa, 
                    AZ
                </p>
                <p class="text-blue-600 font-medium">DDS | Private</p>
            </div>
        </div>
        """

    @pytest.fixture
    def sample_sdn_detailed_school_html(self):
        """Sample SDN detailed school HTML for testing."""
        return """
        <div class="flex flex-wrap items-center gap-4">
            <img class="w-32 md:w-40 object-cover rounded-xl" src="https://www.studentdoctor.net/schools-database/img/schools/ASDOH.jpg?v=2025-08-22 20:39:53" style="max-width: 150px" alt="A. T. Still University - Arizona School of Dentistry and Oral Health">
            <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold flex-1">
                A. T. Still University - Arizona School of Dentistry and Oral Health
            </h1>
        </div>

        <div class="flex flex-col md:flex-row w-full">
            <div class="w-full md:w-[75%]">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 font-semibold mt-4">
                            Mesa, 
                            AZ
                        </p>
                        <div class="hidden md:flex gap-1">
                            <div class="text-green-600 font-semibold">
                                Dental Schools
                                |
                                Private Non-Profit
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4">
                    <div class="p-4">
                        <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">School Overview</h3>
                        <p><strong>Tuition (In State):</strong> $96,960</p>
                        <p><strong>Tuition (Out of State):</strong> $96,960</p>
                        <p><strong>Accreditation Status:</strong> Approval</p>
                        <p><strong>Acceptance Rate:</strong> N/A </p>
                        <p><strong>Total Enrollment:</strong> 78 </p>
                        <p><strong>Degrees:</strong> DDS </p>
                        <p><strong>Founding Year:</strong> 2003  </p>
                        <p><strong>Accreditation Year:</strong> 2007  </p>
                        <p>
                            <strong>Website:</strong>
                            <span class="text-blue-500">
                                <a target="_blank" href="https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health" aria-label="More about A. T. Still University - Arizona School of Dentistry and Oral Health">
                                    https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health
                                </a>
                            </span>
                        </p>
                    </div>
                    <div class="p-4 rounded-lg gap-4">
                        <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">Application Information</h3>
                        <p><strong>Average DAT:</strong> 19.5</p>
                        <p><strong>Average GPA:</strong> 3.52</p>
                        <p><strong>Male:</strong> N/A</p>
                        <p><strong>Female:</strong> N/A</p>                       
                    </div>
                </div>
                
                <div class="grid md:grid-cols-2 gap-4">
                    <div class="mt-6 p-4 bg-gray-100 rounded-lg flex flex-col">
                        <h3 class="text-lg font-semibold mb-4">Interview Feedback Summary</h3>
                        <p class="text-gray-700 flex-1">Overall, applicants ranked the school in the top 32% of interviews, indicating it is moderately regarded. They found the interview generally impressive with a moderate stress level and felt they did okay.</p>
                    </div>
                    <div class="mt-6 p-4 bg-gray-100 rounded-lg flex flex-col">
                        <h3 class="text-lg font-semibold mb-4">School Review Summary</h3>
                        <p class="text-gray-700 flex-1">Insufficient reviews to generate a summary. Add your review!</p>
                    </div>
                </div>
                
                <div class="mt-6 p-4 bg-gray-100 rounded-lg">
                   <h2 class="text-gray-800 font-semibold text-lg">5 Most Common Secondary Essay Questions for ATSU-ASDOH</h2>
                   <hr class="my-2 border-gray-300">
                   <ul class="text-gray-700 text-sm space-y-2">
                       <li><strong>1. Understanding and Commitment to Medicine</strong> – Describe your experiences with osteopathic physicians. Have you ever shadowed a DO? If not, please explain why. Do you have a letter of recommendation from a DO? If not, please explain why.</li>
                       <li><strong>2. Motivation and Fit</strong> – What unique feature of SOMA appeals to you, and what specific feature of SOMA concerns you?</li>
                       <li><strong>3. Personal Attributes and Characteristics</strong> – What do you consider your strongest attribute as a SOMA student, and what do you consider your weakest?</li>
                       <li><strong>4. Community, Diversity, and Equity</strong> – How do you plan to engage with medically underserved populations in your medical career, and how have your past volunteer experiences shaped these plans?</li>
                   </ul>
               </div>
               
               <div class="mt-6 p-2">
                   <h3 class="text-lg font-semibold">About the School</h3>
                   <p class="text-gray-700 break-words">
                       The Arizona School of Dentistry & Oral Health (ASDOH) prepares caring, technologically adept dental students to become community and educational leaders serving those in need. The school offers students an experience-rich learning environment where health professionals approach patient health as part of an interdisciplinary team.
                   </p>
               </div>
               
               <div class="mt-6 p-2">
                   <h3 class="text-lg font-semibold">Curriculum</h3>
                   <p class="text-gray-700 break-words">
                       ASDOH students spend the first two years studying the basic sciences and clinical introductions in a classroom setting. Third-year students complete dental simulation exercises and work side by side with trained dentists in our campus clinic.
                   </p>
               </div>
               
               <div class="mt-6 p-2">
                   <h3 class="text-lg font-semibold">Facilities</h3>
                   <p class="text-gray-700 break-words">
                       N/A
                   </p>
               </div>
               
               <p class="mt-4 text-end"><strong>Last Updated:</strong> Aug 22, 2025</p>
            </div>
            
            <div class="w-full md:w-[35%] p-2 md:p-6">
                <div class="bg-white p-2 md:p-6 rounded-lg shadow-md w-full">
                    <h2 class="text-gray-700 font-semibold text-lg">SDN Insights</h2>
                    <div class="mt-4 space-y-4">
                        <div class="flex items-start">
                            <span class="text-xl">💰</span>
                            <div class="ml-3">
                                <h3 class="text-blue-600 font-semibold">Cost of Attendance:
                                    <a target="_blank" class="text-red-600 link link-hover" href="https://www.studentdoctor.net/student-loan-calculators/d/medical-school-student-loan-calculator/?avg_debt=$583,079&amp;payment_percent=25">$583,079</a>
                                </h3>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <span class="text-xl">⚖️</span>
                            <div class="ml-3">
                                <h3 class="text-red-600 font-semibold">Cost of Living: Lower than 99% Nationally</h3>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <span class="text-xl">🌳</span>
                            <div class="ml-3">
                                <h3 class="text-green-600 font-semibold">Environment: Urban</h3>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="p-2 md:p-6 rounded-lg shadow-md w-full mb-4 mt-4" style="background: aliceblue">
                    <p>
                        <strong>School Address:</strong>
                        <a target="_blank" href="https://www.google.com/maps/place/%2C+5850+E.+Still+Circle%2C+Mesa%2C+ARIZONA%2C+85206%2C+US" class="text-blue-500">
                            5850 E. Still Circle, Mesa, AZ 85206
                        </a>
                    </p>
                </div>
                
                <div class="bg-white p-2 md:p-6 rounded-lg shadow-md w-full mt-4">
                    <h3 class="text-gray-800 font-semibold">Links</h3>
                    <ul class="text-gray-700 text-sm space-y-1 mt-2">
                        <li><a href="https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health" target="_blank" class="text-blue-600 link link-hover">ATSU-ASDOH School Website</a></li>
                        <li><a href="https://forums.studentdoctor.net/threads/asdoh-class-of-2030-interview-acceptance-thread.1508285/" target="_blank" class="text-blue-600 link link-hover">ATSU-ASDOH Current Cycle SDN Forum Thread</a></li>
                        <li><a href="https://en.wikipedia.org/wiki/Arizona_School_of_Dentistry_and_Oral_Health" target="_blank" class="text-blue-600 link link-hover">Wikipedia</a></li>
                    </ul>
                </div>
            </div>
        </div>
        """

    def test_extract_sdn_school_data_basic_info(self, sample_sdn_school_item_html):
        """Test extraction of basic school information from SDN school item."""
        soup = BeautifulSoup(sample_sdn_school_item_html, "html.parser")
        item = soup.find("div", class_="school-item")

        with patch(
            "src.navigator_dagster.defs.utils.fetch_sdn_detailed_school_info"
        ) as mock_fetch:
            mock_fetch.return_value = {}

            result = extract_sdn_school_data(item)

            assert result is not None
            assert (
                result["name"]
                == "A. T. Still University - Arizona School of Dentistry and Oral Health"
            )
            assert result["location"] == "Mesa, AZ"
            assert result["degree"] == "DDS"
            assert (
                result["detail_url"]
                == "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/a-t-still-university-arizona-school-of-dentistry-and-oral-health"
            )
            assert result["data_attributes"]["degree"] == "DDS"
            assert result["data_attributes"]["state"] == "4"
            assert result["data_attributes"]["type"] == "1"
            assert result["data_attributes"]["id"] == "189"
            assert result["data_attributes"]["country"] == "US"

    def test_fetch_sdn_detailed_school_info_basic_data(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of basic detailed school information."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            assert result["state"] == "AZ"
            assert result["school_type"] == "Dental Schools, Private Non-Profit"
            assert result["tuition_in_state"] == "$96,960"
            assert result["tuition_out_of_state"] == "$96,960"
            assert (
                result["website"]
                == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
            )
            assert result["average_dat"] == "19.5"
            assert result["average_gpa"] == "3.52"

    def test_fetch_sdn_detailed_school_info_feedback_summaries(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of interview and review feedback summaries."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            assert (
                "Overall, applicants ranked the school in the top 32% of interviews"
                in result["interview_feedback_summary"]
            )
            assert (
                result["school_review_summary"]
                == "Insufficient reviews to generate a summary. Add your review!"
            )

    def test_fetch_sdn_detailed_school_info_essay_questions(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of common secondary essay questions."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            questions = result["common_secondary_essay_questions"]
            assert len(questions) == 4
            assert (
                "Understanding and Commitment to Medicine– Describe your experiences with osteopathic physicians"
                in questions[0]
            )
            assert (
                "Motivation and Fit– What unique feature of SOMA appeals to you"
                in questions[1]
            )
            assert (
                "Personal Attributes and Characteristics– What do you consider your strongest attribute"
                in questions[2]
            )
            assert (
                "Community, Diversity, and Equity– How do you plan to engage with medically underserved populations"
                in questions[3]
            )

    def test_fetch_sdn_detailed_school_info_about_curriculum_facilities(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of about the school, curriculum, and facilities."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            assert (
                "The Arizona School of Dentistry & Oral Health (ASDOH) prepares caring"
                in result["about_the_school"]
            )
            assert (
                "ASDOH students spend the first two years studying the basic sciences"
                in result["curriculum"]
            )
            assert result["facilities"] == "N/A"

    def test_fetch_sdn_detailed_school_info_insights(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of SDN insights."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            insights = result["insights"]
            assert insights["cost_of_attendance"] == "$583,079"
            assert insights["cost_of_living"] == "Lower than 99% Nationally"
            assert insights["environment"] == "Urban"

    def test_fetch_sdn_detailed_school_info_address_and_links(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of school address and links."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            assert "5850 E. Still Circle, Mesa, AZ 85206" in result["school_address"]

            links = result["links"]
            assert len(links) == 3
            assert links[0]["label"] == "ATSU-ASDOH School Website"
            assert (
                links[0]["url"]
                == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
            )
            assert links[1]["label"] == "ATSU-ASDOH Current Cycle SDN Forum Thread"
            assert links[2]["label"] == "Wikipedia"

    def test_fetch_sdn_detailed_school_info_last_updated(
        self, sample_sdn_detailed_school_html
    ):
        """Test extraction of last updated date."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info(
                "https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test"
            )

            assert result["last_updated"] == "Aug 22, 2025"

    def test_extract_sdn_school_data_integration(
        self, sample_sdn_school_item_html, sample_sdn_detailed_school_html
    ):
        """Test complete integration of extract_sdn_school_data with detailed info."""
        soup = BeautifulSoup(sample_sdn_school_item_html, "html.parser")
        item = soup.find("div", class_="school-item")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_sdn_detailed_school_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = extract_sdn_school_data(item)

            # Test basic info
            assert (
                result["name"]
                == "A. T. Still University - Arizona School of Dentistry and Oral Health"
            )
            assert result["location"] == "Mesa, AZ"
            assert result["degree"] == "DDS"

            # Test detailed info
            assert result["state"] == "AZ"
            assert result["average_dat"] == "19.5"
            assert result["average_gpa"] == "3.52"
            assert result["tuition_in_state"] == "$96,960"
            assert result["tuition_out_of_state"] == "$96,960"
            assert (
                result["website"]
                == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
            )

            # Test feedback summaries
            assert (
                "Overall, applicants ranked the school in the top 32% of interviews"
                in result["interview_feedback_summary"]
            )
            assert (
                result["school_review_summary"]
                == "Insufficient reviews to generate a summary. Add your review!"
            )

            # Test essay questions
            assert len(result["common_secondary_essay_questions"]) == 4

            # Test about/curriculum/facilities
            assert (
                "The Arizona School of Dentistry & Oral Health (ASDOH) prepares caring"
                in result["about_the_school"]
            )
            assert (
                "ASDOH students spend the first two years studying the basic sciences"
                in result["curriculum"]
            )
            assert result["facilities"] == "N/A"

            # Test insights
            assert result["insights"]["cost_of_attendance"] == "$583,079"
            assert result["insights"]["cost_of_living"] == "Lower than 99% Nationally"
            assert result["insights"]["environment"] == "Urban"

            # Test address and links
            assert "5850 E. Still Circle, Mesa, AZ 85206" in result["school_address"]
            assert len(result["links"]) == 3

            # Test last updated
            assert result["last_updated"] == "Aug 22, 2025"

    def test_scrape_sdn_dental_schools_mock(self):
        """Test the main scraping function with mocked webdriver."""
        with patch("src.navigator_dagster.defs.utils.webdriver.Chrome") as mock_chrome:
            # Mock the webdriver and its methods
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver

            # Mock page source with sample school items
            sample_page_html = """
            <div id="schoolContainer">
                <div class="school-item flex border p-4 rounded-lg items-center space-x-4 mb-4" data-degree="DDS" data-state="4" data-type="1" data-id="189" data-country="US">
                    <a class="flex-shrink-0 w-24 h-24" href="https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test">
                        <div class="school_img flex items-center justify-center">
                            <img src="test.jpg" class="rounded-md object-contain" alt="Test School">
                        </div>
                    </a>
                    <div class="flex-1">
                        <h3 class="mt-2 font-semibold name">
                            <a href="https://www.studentdoctor.net/schools-database/school/detail/ATSU-ASDOH/test">Test School</a>
                        </h3>
                        <p class="text-sm text-gray-600 mt-2">Test City, TS</p>
                        <p class="text-blue-600 font-medium">DDS | Private</p>
                    </div>
                </div>
            </div>
            """
            mock_driver.page_source = sample_page_html

            # Mock WebDriverWait
            with patch("src.navigator_dagster.defs.utils.WebDriverWait") as mock_wait:
                mock_wait_instance = Mock()
                mock_wait.return_value = mock_wait_instance
                mock_wait_instance.until.return_value = None

                # Mock the detailed school info fetch
                with patch(
                    "src.navigator_dagster.defs.utils.fetch_sdn_detailed_school_info"
                ) as mock_fetch:
                    mock_fetch.return_value = {
                        "state": "TS",
                        "school_type": "Dental Schools | Private",
                        "average_dat": "20.0",
                        "average_gpa": "3.5",
                        "tuition_in_state": "$100,000",
                        "tuition_out_of_state": "$100,000",
                        "website": "https://test.edu",
                        "interview_feedback_summary": "Test feedback",
                        "school_review_summary": "Test review",
                        "common_secondary_essay_questions": ["Test question"],
                        "about_the_school": "Test about",
                        "curriculum": "Test curriculum",
                        "facilities": "Test facilities",
                        "insights": {"cost_of_attendance": "$500,000"},
                        "school_address": "123 Test St, Test City, TS 12345",
                        "links": [{"label": "Test Link", "url": "https://test.com"}],
                        "last_updated": "Jan 1, 2025",
                    }

                    result = scrape_sdn_dental_schools("https://test.com")

                    assert len(result) == 1
                    school = result[0]
                    assert school["name"] == "Test School"
                    assert school["location"] == "Test City, TS"
                    assert school["degree"] == "DDS"
                    assert school["state"] == "TS"
                    assert school["average_dat"] == "20.0"
                    assert school["average_gpa"] == "3.5"

    def test_extract_sdn_school_data_error_handling(self):
        """Test error handling in extract_sdn_school_data."""
        # Test with None input
        result = extract_sdn_school_data(None)
        assert result is None

        # Test with empty item
        soup = BeautifulSoup("<div></div>", "html.parser")
        result = extract_sdn_school_data(soup)
        assert result is not None
        assert isinstance(result, dict)

    def test_fetch_sdn_detailed_school_info_error_handling(self):
        """Test error handling in fetch_sdn_detailed_school_info."""
        # Test with empty URL
        result = fetch_sdn_detailed_school_info("")
        assert result == {}

        # Test with HTTP error
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("HTTP Error")
            result = fetch_sdn_detailed_school_info("https://test.com")
            assert result == {}

    def test_scrape_sdn_dental_schools_error_handling(self):
        """Test error handling in scrape_sdn_dental_schools."""
        with patch("src.navigator_dagster.defs.utils.webdriver.Chrome") as mock_chrome:
            mock_chrome.side_effect = Exception("WebDriver Error")

            result = scrape_sdn_dental_schools("https://test.com")
            assert result == []

    def test_extract_sdn_school_data_missing_elements(self):
        """Test extraction when some elements are missing."""
        html_missing_elements = """
        <div class="school-item flex border p-4 rounded-lg items-center space-x-4 mb-4" data-degree="DDS" data-state="4" data-type="1" data-id="189" data-country="US">
            <div class="flex-1">
                <h3 class="mt-2 font-semibold name">
                    <a href="https://www.studentdoctor.net/schools-database/school/detail/test">Test School</a>
                </h3>
            </div>
        </div>
        """

        soup = BeautifulSoup(html_missing_elements, "html.parser")
        item = soup.find("div", class_="school-item")

        with patch(
            "src.navigator_dagster.defs.utils.fetch_sdn_detailed_school_info"
        ) as mock_fetch:
            mock_fetch.return_value = {}

            result = extract_sdn_school_data(item)

            assert result is not None
            assert result["name"] == "Test School"
            assert result["location"] == ""
            assert result["degree"] == "DDS"
            assert (
                result["detail_url"]
                == "https://www.studentdoctor.net/schools-database/school/detail/test"
            )

    def test_fetch_sdn_detailed_school_info_missing_sections(self):
        """Test extraction when some sections are missing from detailed page."""
        html_missing_sections = """
        <div class="flex flex-col md:flex-row w-full">
            <div class="w-full md:w-[75%]">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 font-semibold mt-4">Test City, TS</p>
                    </div>
                </div>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = html_missing_sections.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            # Should have empty values for missing sections
            assert result["state"] == "TS"
            assert result["school_type"] == ""
            assert result["average_dat"] == ""
            assert result["average_gpa"] == ""
            assert result["tuition_in_state"] == ""
            assert result["tuition_out_of_state"] == ""
            assert result["website"] == ""
            assert result["interview_feedback_summary"] == ""
            assert result["school_review_summary"] == ""
            assert result["common_secondary_essay_questions"] == []
            assert result["about_the_school"] == ""
            assert result["curriculum"] == ""
            assert result["facilities"] == ""
            assert result["insights"] == {}
            assert result["school_address"] == ""
            assert result["links"] == []
            assert result["last_updated"] == ""

    def test_location_parsing_cleans_newlines(self):
        """Test that location parsing cleans up newlines and extra whitespace."""
        html_with_newlines = """
        <div class="school-item flex border p-4 rounded-lg items-center space-x-4 mb-4" data-degree="DDS" data-state="4" data-type="1" data-id="189" data-country="US">
            <div class="flex-1">
                <h3 class="mt-2 font-semibold name">
                    <a href="https://www.studentdoctor.net/schools-database/school/detail/test">Test School</a>
                </h3>
                <p class="text-sm text-gray-600 mt-2">
                    Mesa, 
                    AZ
                </p>
            </div>
        </div>
        """

        soup = BeautifulSoup(html_with_newlines, "html.parser")
        item = soup.find("div", class_="school-item")

        with patch(
            "src.navigator_dagster.defs.utils.fetch_sdn_detailed_school_info"
        ) as mock_fetch:
            mock_fetch.return_value = {}

            result = extract_sdn_school_data(item)

            assert result["location"] == "Mesa, AZ"

    def test_school_type_parsing_formats_correctly(self):
        """Test that school type parsing formats correctly with commas instead of pipes."""
        html_with_school_type = """
        <div class="flex flex-col md:flex-row w-full">
            <div class="w-full md:w-[75%]">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 font-semibold mt-4">Mesa, AZ</p>
                        <div class="hidden md:flex gap-1">
                            <div class="text-green-600 font-semibold">
                                Dental Schools
                                |
                                Private Non-Profit
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = html_with_school_type.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            assert result["school_type"] == "Dental Schools, Private Non-Profit"

    def test_school_address_parsing_cleans_newlines(self):
        """Test that school address parsing cleans up newlines and extra whitespace."""
        html_with_address = """
        <div class="p-2 md:p-6 rounded-lg shadow-md w-full mb-4 mt-4" style="background: aliceblue">
            <p>
                <strong>School Address:</strong>
                <a target="_blank" href="https://www.google.com/maps/place/test" class="text-blue-500">
                    5850 E. Still Circle, 

                    Mesa, 
                    AZ 85206
                </a>
            </p>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = html_with_address.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            assert result["school_address"] == "5850 E. Still Circle, Mesa, AZ 85206"

    def test_location_state_extraction_cleans_newlines(self):
        """Test that location and state extraction cleans up newlines in detailed page."""
        html_with_location = """
        <div class="flex flex-col md:flex-row w-full">
            <div class="w-full md:w-[75%]">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 font-semibold mt-4">
                            Mesa, 
                            AZ
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = html_with_location.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            assert result["state"] == "AZ"

    def test_website_extraction_works_correctly(self):
        """Test that website extraction works correctly from school overview section."""
        html_with_website = """
        <div class="grid md:grid-cols-2 gap-4">
            <div class="p-4">
                <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">School Overview</h3>
                <p>
                    <strong>Website:</strong>
                    <span class="text-blue-500">
                        <a target="_blank" href="https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health" aria-label="More about Test School">
                            https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health
                        </a>
                    </span>
                </p>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = html_with_website.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            assert (
                result["website"]
                == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
            )

    def test_tuition_extraction_works_correctly(self):
        """Test that tuition extraction works correctly for both in-state and out-of-state."""
        html_with_tuition = """
        <div class="grid md:grid-cols-2 gap-4">
            <div class="p-4">
                <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">School Overview</h3>
                <p><strong>Tuition (In State):</strong> $96,960</p>
                <p><strong>Tuition (Out of State):</strong> $96,960</p>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = html_with_tuition.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            assert result["tuition_in_state"] == "$96,960"
            assert result["tuition_out_of_state"] == "$96,960"

    def test_integration_all_parsing_fixes(self):
        """Test integration of all parsing fixes with the provided HTML example."""
        # This test uses the exact HTML structure provided by the user
        sample_html = """
        <div class="flex flex-wrap items-center gap-4">
            <img class="w-32 md:w-40 object-cover rounded-xl" src="https://www.studentdoctor.net/schools-database/img/schools/ASDOH.jpg?v=2025-08-22 20:39:53" style="max-width: 150px" alt="A. T. Still University - Arizona School of Dentistry and Oral Health">
            <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold flex-1">
                A. T. Still University - Arizona School of Dentistry and Oral Health
            </h1>
        </div>

        <div class="flex flex-col md:flex-row w-full">
            <div class="w-full md:w-[75%]">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 font-semibold mt-4">
                            Mesa, 
                            AZ
                        </p>
                        <div class="hidden md:flex gap-1">
                            <div class="text-green-600 font-semibold">
                                Dental Schools
                                |
                                Private Non-Profit
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4">
                    <div class="p-4">
                        <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">School Overview</h3>
                        <p><strong>Tuition (In State):</strong> $96,960</p>
                        <p><strong>Tuition (Out of State):</strong> $96,960</p>
                        <p>
                            <strong>Website:</strong>
                            <span class="text-blue-500">
                                <a target="_blank" href="https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health" aria-label="More about A. T. Still University - Arizona School of Dentistry and Oral Health">
                                    https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health
                                </a>
                            </span>
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="w-full md:w-[35%] p-2 md:p-6">
                <div class="p-2 md:p-6 rounded-lg shadow-md w-full mb-4 mt-4" style="background: aliceblue">
                    <p>
                        <strong>School Address:</strong>
                        <a target="_blank" href="https://www.google.com/maps/place/%2C+5850+E.+Still+Circle%2C+Mesa%2C+ARIZONA%2C+85206%2C+US" class="text-blue-500">
                            5850 E. Still Circle, 

                            Mesa, 
                            AZ 85206
                        </a>
                    </p>
                </div>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = sample_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            # Test all the fixes
            assert result["state"] == "AZ"
            assert result["school_type"] == "Dental Schools, Private Non-Profit"
            assert result["tuition_in_state"] == "$96,960"
            assert result["tuition_out_of_state"] == "$96,960"
            assert (
                result["website"]
                == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
            )
            assert result["school_address"] == "5850 E. Still Circle, Mesa, AZ 85206"

    def test_real_html_structure_parsing(self):
        """Test with the exact real HTML structure provided by the user."""
        # This uses the exact HTML structure from the user's example
        real_html = """
        <div class="flex flex-col md:flex-row w-full">
            <div class="w-full md:w-[75%]">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-green-600 font-semibold mt-4">
                            Mesa, 
                            AZ
                        </p>
                        <div class="hidden md:flex gap-1">
                            <div class="text-green-600 font-semibold">
                                Dental Schools
                                |
                                Private Non-Profit
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4">
                    <div class="p-4">
                        <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">School Overview</h3>
                        <p><strong>Tuition (In State):</strong> $96,960</p>
                        <p><strong>Tuition (Out of State):</strong> $96,960</p>
                        <p><strong>Accreditation Status:</strong> Approval</p>
                        <p><strong>Acceptance Rate:</strong> N/A </p>
                        <p><strong>Total Enrollment:</strong> 78 </p>
                        <p><strong>Degrees:</strong> DDS </p>
                        <p><strong>Founding Year:</strong> 2003  </p>
                        <p><strong>Accreditation Year:</strong> 2007  </p>
                        <p>
                            <strong>Website:</strong>
                            <span class="text-blue-500">
                                <a target="_blank" href="https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health" aria-label="More about A. T. Still University - Arizona School of Dentistry and Oral Health">
                                    https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health
                                </a>
                            </span>
                        </p>
                    </div>
                    <div class="p-4 rounded-lg gap-4">
                        <h3 class="text-2xl font-semibold border-b border-gray-300 mb-2">Application Information</h3>
                        <p><strong>Average DAT:</strong> 19.5</p>
                        <p><strong>Average GPA:</strong> 3.52</p>
                        <p><strong>Male:</strong> N/A</p>
                        <p><strong>Female:</strong> N/A</p>                       
                    </div>
                </div>
            </div>
            
            <div class="w-full md:w-[35%] p-2 md:p-6">
                <div class="p-2 md:p-6 rounded-lg shadow-md w-full mb-4 mt-4" style="background: aliceblue">
                    <p>
                        <strong>School Address:</strong>
                        <a target="_blank" href="https://www.google.com/maps/place/%2C+5850+E.+Still+Circle%2C+Mesa%2C+ARIZONA%2C+85206%2C+US" class="text-blue-500">
                            5850 E. Still Circle, 

                            Mesa, 
                            AZ 85206
                        </a>
                    </p>
                </div>
            </div>
        </div>
        """

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = real_html.encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_sdn_detailed_school_info("https://test.com")

            # Test that all the problematic fields are now correctly extracted
            assert result["state"] == "AZ"
            assert result["school_type"] == "Dental Schools, Private Non-Profit"
            assert result["tuition_in_state"] == "$96,960", (
                f"Expected '$96,960', got '{result['tuition_in_state']}'"
            )
            assert result["tuition_out_of_state"] == "$96,960", (
                f"Expected '$96,960', got '{result['tuition_out_of_state']}'"
            )
            assert (
                result["website"]
                == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
            ), f"Expected website URL, got '{result['website']}'"
            assert result["school_address"] == "5850 E. Still Circle, Mesa, AZ 85206"
            assert result["average_dat"] == "19.5"
            assert result["average_gpa"] == "3.52"
