import pytest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from src.navigator_dagster.defs.utils import (
    extract_program_data,
    fetch_detailed_program_info,
    extract_contact_info,
    extract_program_info_table,
    extract_requirements,
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
            assert result["size"] == 2
            assert result["length"] == 36
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
        assert contact1["name"] == "Kenneth Kromash  DDS"
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
        assert "US Citizen" in req5["sections"]
        assert "US Permanent Resident" in req5["sections"]
        assert "Canadian Citizen" in req5["sections"]

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
            assert result["size"] == 2
            assert result["length"] == 36

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
