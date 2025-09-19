"""
Tests for the enhanced dental programs merging functionality.
"""

import pytest
from src.navigator_dagster.defs.mongo_utils import (
    normalize_name,
    normalize_state,
    calculate_similarity,
    find_best_match,
    merge_program_data,
)


class TestStateNormalization:
    """Test the state normalization functionality."""

    def test_normalize_state_full_name(self):
        """Test normalization of full state names."""
        assert normalize_state("Illinois") == "IL"
        assert normalize_state("California") == "CA"
        assert normalize_state("New York") == "NY"
        assert normalize_state("Pennsylvania") == "PA"
        assert normalize_state("Texas") == "TX"

    def test_normalize_state_code(self):
        """Test normalization of state codes."""
        assert normalize_state("IL") == "IL"
        assert normalize_state("ca") == "CA"
        assert normalize_state("ny") == "NY"
        assert normalize_state("pa") == "PA"

    def test_normalize_state_case_insensitive(self):
        """Test case insensitive normalization."""
        assert normalize_state("ILLINOIS") == "IL"
        assert normalize_state("illinois") == "IL"
        assert normalize_state("Illinois") == "IL"
        assert normalize_state("iL") == "IL"

    def test_normalize_state_with_whitespace(self):
        """Test normalization with whitespace."""
        assert normalize_state(" Illinois ") == "IL"
        assert normalize_state("  CA  ") == "CA"
        assert normalize_state("\tNY\n") == "NY"

    def test_normalize_state_dc_variations(self):
        """Test DC variations."""
        assert normalize_state("District of Columbia") == "DC"
        assert normalize_state("Washington DC") == "DC"
        assert normalize_state("D.C.") == "DC"
        assert normalize_state("dc") == "DC"

    def test_normalize_state_unknown(self):
        """Test unknown states."""
        assert normalize_state("Unknown State") == "UNKNOWN STATE"
        assert normalize_state("") == ""
        assert normalize_state(None) == ""

    def test_normalize_state_territories(self):
        """Test territories and other locations."""
        assert normalize_state("Puerto Rico") == "PUERTO RICO"
        assert normalize_state("Virgin Islands") == "VIRGIN ISLANDS"


class TestNameNormalization:
    """Test the name normalization functionality."""

    def test_normalize_name_basic(self):
        """Test basic name normalization."""
        assert normalize_name("A.T. Still University") == "at still"
        assert (
            normalize_name("University of Pennsylvania") == "university of pennsylvania"
        )
        assert (
            normalize_name("Arizona School of Dentistry & Oral Health")
            == "arizona school of dentistry oral"
        )

    def test_normalize_name_with_special_chars(self):
        """Test normalization with special characters."""
        assert normalize_name("Dr. John's Dental School") == "doctor john s dental"
        assert normalize_name("St. Mary's University") == "saint mary s"

    def test_normalize_name_empty(self):
        """Test normalization with empty or None input."""
        assert normalize_name("") == ""
        assert normalize_name(None) == ""


class TestSimilarityCalculation:
    """Test the similarity calculation functionality."""

    def test_exact_match(self):
        """Test exact matches."""
        assert (
            calculate_similarity(
                "University of Pennsylvania", "University of Pennsylvania"
            )
            == 1.0
        )
        assert (
            calculate_similarity("A.T. Still University", "A.T. Still University")
            == 1.0
        )

    def test_similar_names(self):
        """Test similar but not identical names."""
        similarity = calculate_similarity(
            "A.T. Still University", "AT Still University"
        )
        assert similarity > 0.8

        similarity = calculate_similarity(
            "University of Pennsylvania", "Pennsylvania University"
        )
        assert similarity > 0.5

    def test_different_names(self):
        """Test completely different names."""
        similarity = calculate_similarity("Harvard University", "MIT")
        assert similarity < 0.5

    def test_empty_names(self):
        """Test with empty names."""
        assert calculate_similarity("", "University") == 0.0
        assert calculate_similarity("University", "") == 0.0
        assert calculate_similarity("", "") == 0.0


class TestBestMatch:
    """Test the best match finding functionality."""

    def test_find_exact_match(self):
        """Test finding exact matches."""
        candidates = [
            {"name": "University of Pennsylvania", "type": "advanced_standing"},
            {"name": "Harvard University", "type": "advanced_standing"},
        ]

        match = find_best_match(
            "University of Pennsylvania", "advanced_standing", candidates
        )
        assert match is not None
        assert match["name"] == "University of Pennsylvania"

    def test_find_similar_match(self):
        """Test finding similar matches."""
        candidates = [
            {"name": "A.T. Still University", "type": "advanced_standing"},
            {"name": "Harvard University", "type": "advanced_standing"},
        ]

        match = find_best_match(
            "AT Still University", "advanced_standing", candidates, threshold=0.7
        )
        assert match is not None
        assert match["name"] == "A.T. Still University"

    def test_no_match_below_threshold(self):
        """Test no match when similarity is below threshold."""
        candidates = [
            {"name": "Harvard University", "type": "advanced_standing"},
            {"name": "MIT", "type": "advanced_standing"},
        ]

        match = find_best_match(
            "University of Pennsylvania", "advanced_standing", candidates, threshold=0.9
        )
        assert match is None

    def test_type_filtering(self):
        """Test that type filtering works correctly."""
        candidates = [
            {"name": "University of Pennsylvania", "type": "residency"},
            {"name": "University of Pennsylvania", "type": "advanced_standing"},
        ]

        # Should match residency type
        match = find_best_match("University of Pennsylvania", "residency", candidates)
        assert match is not None
        assert match["type"] == "residency"

        # Should match advanced_standing type
        match = find_best_match(
            "University of Pennsylvania", "advanced_standing", candidates
        )
        assert match is not None
        assert match["type"] == "advanced_standing"


class TestProgramDataMerging:
    """Test the program data merging functionality."""

    def test_merge_adea_pass_program(self):
        """Test merging ADEA PASS program data."""
        adea_program = {
            "name": "Abington Memorial Hospital",
            "state": "Pennsylvania",
            "type": "General Practice Residency",
            "adea_url": "https://programs.adea.org/PASS/programs/abington-memorial-hospital-general-practice-residency",
            "description": "Test description",
            "information": {"program_website": "https://example.com"},
            "requirements": [{"title": "Test", "sections": ["Test requirement"]}],
            "contact": {"points_of_contact": [{"name": "Dr. Test"}]},
        }

        merged = merge_program_data(adea_program)

        assert merged["name"] == "Abington Memorial Hospital"
        assert merged["state"] == "PA"  # Normalized to state code
        assert merged["type"] == "residency"
        assert merged["degree"] is None
        assert merged["speciality"] == "General Practice Residency"
        assert merged["description"] == "Test description"
        assert merged["website"] == "https://example.com"
        assert merged["average_dat"] is None  # SDN field should be None

    def test_merge_adea_caapid_program(self):
        """Test merging ADEA CAAPID program data."""
        adea_program = {
            "name": "A.T. Still Missouri School of Dentistry and Oral Health",
            "state": "Missouri",
            "type": "D.M.D.",
            "adea_url": "https://programs.adea.org/CAAPID/programs/a.t.-still-missouri-school-of-dentistry-and-oral-health",
            "description": "Test description",
            "information": {"program_website": "https://example.com"},
            "requirements": [{"title": "Test", "sections": ["Test requirement"]}],
            "contact": {"points_of_contact": [{"name": "Dr. Test"}]},
        }

        merged = merge_program_data(adea_program)

        assert (
            merged["name"] == "A.T. Still Missouri School of Dentistry and Oral Health"
        )
        assert merged["state"] == "MO"  # Normalized to state code
        assert merged["type"] == "advanced_standing"
        assert merged["degree"] == "D.M.D."
        assert merged["speciality"] is None
        assert merged["description"] == "Test description"

    def test_merge_with_sdn_data(self):
        """Test merging ADEA program with SDN data."""
        adea_program = {
            "name": "A.T. Still University",
            "state": "Missouri",
            "type": "D.M.D.",
            "adea_url": "https://programs.adea.org/CAAPID/programs/test",
            "description": "Test description",
            "information": {"program_website": "https://example.com"},
            "requirements": [],
            "contact": {},
        }

        sdn_program = {
            "name": "A. T. Still University - Arizona School of Dentistry and Oral Health",
            "state": "AZ",
            "degree": "DDS",
            "average_dat": "19.5",
            "average_gpa": "3.52",
            "tuition_in_state": "$96,960",
            "tuition_out_of_state": "$96,960",
            "website": "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health",
            "about_the_school": "Test about",
            "curriculum": "Test curriculum",
        }

        merged = merge_program_data(adea_program, sdn_program)

        # ADEA data should be preserved
        assert merged["name"] == "A.T. Still University"
        assert merged["type"] == "advanced_standing"
        assert merged["degree"] == "D.M.D."

        # SDN data should be merged
        assert merged["average_dat"] == "19.5"
        assert merged["average_gpa"] == "3.52"
        assert merged["tuition_in_state"] == "$96,960"
        assert merged["tuition_out_of_state"] == "$96,960"
        assert merged["about_the_school"] == "Test about"
        assert merged["curriculum"] == "Test curriculum"

        # Website should prefer SDN if available
        assert (
            merged["website"]
            == "https://www.atsu.edu/arizona-school-of-dentistry-and-oral-health"
        )

    def test_merge_with_state_normalization(self):
        """Test that state normalization is applied during merging."""
        adea_program = {
            "name": "Test University",
            "state": "Illinois",  # Full state name
            "type": "D.M.D.",
            "adea_url": "https://programs.adea.org/CAAPID/programs/test",
            "description": "Test description",
            "information": {},
            "requirements": [],
            "contact": {},
        }

        merged = merge_program_data(adea_program)

        # State should be normalized to code
        assert merged["state"] == "IL"
        assert merged["name"] == "Test University"
        assert merged["type"] == "advanced_standing"


class TestIntegration:
    """Integration tests for the complete merging process."""

    def test_mock_mongodb_integration(self):
        """Test the complete merging process with mocked MongoDB."""
        # This would be a more comprehensive integration test
        # that mocks the MongoDB collections and tests the full flow
        pass


if __name__ == "__main__":
    pytest.main([__file__])
