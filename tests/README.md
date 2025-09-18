# Tests for Navigator Dagster

This directory contains comprehensive tests for the `utils.py` module, specifically testing the enhanced `extract_program_data` function and its supporting functions.

## Test Coverage

The tests cover the following functionality:

### 1. Basic Program Data Extraction (`test_extract_program_data_basic_info`)
- Extracts program name, state, type, and ADEA URL from program cards
- Parses program size, length, application deadline, and start date
- Converts numeric values appropriately (size as int, length as int)

### 2. Detailed Program Information Fetching (`test_fetch_detailed_program_info_*`)
- Tests HTTP request functionality with mocked responses
- Extracts last updated date from `.adea-pgrm-dtl__updated`
- Extracts website URL from header links
- Parses program description from main content sections

### 3. Contact Information Extraction (`test_extract_contact_info`)
- Extracts contact persons with names, titles, emails, and phone numbers
- Parses program address information
- Handles multiple contact persons correctly

### 4. Program Information Table Parsing (`test_extract_program_info_table`)
- Extracts structured program information from HTML tables
- Handles various data types (yes/no, URLs, text)
- Properly formats keys (lowercase with underscores)

### 5. Requirements Extraction (`test_extract_requirements`)
- Parses accordion sections for application requirements
- Handles different content types (lists, paragraphs, checkmarks)
- Extracts standardized test requirements, transcript requirements, etc.

### 6. Integration Testing (`test_extract_program_data_integration`)
- Tests complete end-to-end functionality
- Verifies data structure matches expected output format
- Ensures all components work together correctly

### 7. Error Handling (`test_*_error_handling`)
- Tests graceful handling of invalid inputs
- Verifies proper error responses for network failures
- Ensures functions don't crash on malformed HTML

## Running Tests

### Prerequisites
Install the required dependencies:
```bash
pip install pytest pytest-mock
```

### Running Tests

#### Option 1: Using the test runner script
```bash
python run_tests.py
```

#### Option 2: Using pytest directly
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_utils.py -v

# Run specific test
pytest tests/test_utils.py::TestUtilsParsing::test_extract_program_data_basic_info -v

# Run with coverage
pytest tests/ --cov=src/navigator_dagster/defs/utils --cov-report=html
```

## Test Data

The tests use realistic HTML samples based on the actual ADEA PASS program pages:

- **Program Card HTML**: Simulates the program listing page structure
- **Detailed Program HTML**: Simulates individual program detail pages with all sections

## Expected Output Format

The tests verify that the extracted data matches this structure:

```python
{
    "name": "Program Name",
    "state": "State",
    "type": "Program Type",
    "url": "https://program-website.com",
    "adea_url": "https://programs.adea.org/PASS/programs/...",
    "size": 2,  # integer
    "length": 36,  # integer (months)
    "application_deadline": "October 1",
    "start_date": "July 1",
    "last_updated": "Last updated on May 1, 2025.",
    "description": "Program description text...",
    "information": {
        "accreditation": "CODA-accredited institution",
        "program_type": "Anesthesiology",
        "program_code": "ANES16",
        # ... more fields
    },
    "requirements": [
        {
            "title": "Required Standardized Tests",
            "sections": ["NBDE1", "NBDE2", "..."]
        },
        # ... more requirement sections
    ],
    "contact": {
        "points_of_contact": [
            {
                "name": "Contact Name",
                "title": "Title",
                "email": "email@example.com",
                "phone": "123-456-7890"
            }
        ],
        "address": "123 Main St, City, State, ZIP"
    }
}
```

## Mocking Strategy

The tests use `unittest.mock.patch` to:
- Mock HTTP requests to avoid actual network calls
- Mock the `fetch_detailed_program_info` function for isolated testing
- Provide controlled test data for consistent results

This ensures tests are fast, reliable, and don't depend on external services.
