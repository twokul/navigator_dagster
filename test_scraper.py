#!/usr/bin/env python3
"""
Test script for the ADEA PASS programs scraper.
This script tests the scraping functionality without requiring Dagster.
"""

import sys

sys.path.append("src")

from navigator_dagster.defs.assets import scrape_adea_programs


def test_scraper():
    """Test the scraper function."""
    print("Testing ADEA PASS programs scraper...")
    print("Note: This requires Chrome browser to be installed.")
    print("Make sure you have Chrome installed and chromedriver in your PATH.")
    print()

    try:
        programs = scrape_adea_programs()

        if programs:
            print(f"Successfully scraped {len(programs)} programs!")
            print("\nFirst program sample:")
            if programs:
                first_program = programs[0]
                for key, value in first_program.items():
                    print(f"  {key}: {value}")
        else:
            print("No programs were scraped. Check the error messages above.")

    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Make sure you have Chrome installed and the required dependencies.")


if __name__ == "__main__":
    test_scraper()
