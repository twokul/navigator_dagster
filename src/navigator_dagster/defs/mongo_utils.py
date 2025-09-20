from typing import List, Dict, Any, Optional
import logging
import re
from difflib import SequenceMatcher
import dagster as dg
from .resources import MongoDBResource

logger = dg.get_dagster_logger()

# State name to state code mapping
STATE_MAPPING = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
    "washington dc": "DC",
    "d.c.": "DC",
    "dc": "DC",
}


def normalize_state(state: str) -> str:
    """
    Normalize state name to state code.

    Args:
        state: State name or code

    Returns:
        Normalized state code (e.g., "IL" for "Illinois")
    """
    if not state:
        return ""

    # Convert to lowercase and strip whitespace
    normalized = state.lower().strip()

    # If it's already a 2-letter code, return uppercase
    if len(normalized) == 2 and normalized.isalpha():
        return normalized.upper()

    # Look up in mapping
    state_code = STATE_MAPPING.get(normalized)
    if state_code:
        return state_code

    # If not found, return original (might be a territory or other location)
    return state.upper()


def normalize_name(name: str) -> str:
    """
    Normalize a program name for better matching by:
    - Converting to lowercase
    - Removing common suffixes and prefixes
    - Removing special characters
    - Standardizing common abbreviations
    """
    if not name:
        return ""

    # Convert to lowercase
    normalized = name.lower().strip()

    # Remove common suffixes
    suffixes_to_remove = [
        r"\s+university$",
        r"\s+college$",
        r"\s+school$",
        r"\s+institute$",
        r"\s+center$",
        r"\s+centre$",
        r"\s+medical$",
        r"\s+health$",
        r"\s+of\s+dentistry$",
        r"\s+dental\s+school$",
        r"\s+school\s+of\s+dentistry$",
        r"\s+and\s+oral\s+health$",
        r"\s+oral\s+health$",
    ]

    for suffix in suffixes_to_remove:
        normalized = re.sub(suffix, "", normalized)

    # Remove special characters and extra spaces
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Standardize common abbreviations
    abbreviations = {
        "a.t. still": "at still",
        "a t still": "at still",
        "u.s.": "us",
        "u s": "us",
        "&": "and",
        "st.": "saint",
        "st ": "saint ",
        "dr.": "doctor",
        "dr ": "doctor ",
    }

    for old, new in abbreviations.items():
        normalized = normalized.replace(old, new)

    return normalized


def calculate_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two program names using multiple methods.
    Returns a score between 0 and 1.
    """
    if not name1 or not name2:
        return 0.0

    # Normalize both names
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)

    if not norm1 or not norm2:
        return 0.0

    # Exact match after normalization
    if norm1 == norm2:
        return 1.0

    # Sequence matcher similarity
    sequence_similarity = SequenceMatcher(None, norm1, norm2).ratio()

    # Check if one name contains the other (partial match)
    if norm1 in norm2 or norm2 in norm1:
        partial_similarity = min(len(norm1), len(norm2)) / max(len(norm1), len(norm2))
        return max(sequence_similarity, partial_similarity * 0.9)

    return sequence_similarity


def find_best_match(
    program_name: str,
    program_type: str,
    candidates: List[Dict[str, Any]],
    threshold: float = 0.7,
) -> Optional[Dict[str, Any]]:
    """
    Find the best matching program from a list of candidates.

    Args:
        program_name: Name of the program to match
        program_type: Type of the program (residency, advanced_standing, or dental_school)
        candidates: List of candidate programs to match against
        threshold: Minimum similarity threshold for a match

    Returns:
        Best matching program or None if no match found
    """
    best_match = None
    best_score = 0.0

    for candidate in candidates:
        candidate_name = candidate.get("name", "")
        candidate_type = candidate.get("type", "")

        # Skip if types don't match
        if program_type != candidate_type:
            continue

        similarity = calculate_similarity(program_name, candidate_name)

        if similarity > best_score and similarity >= threshold:
            best_score = similarity
            best_match = candidate

    return best_match


def merge_program_data(
    adea_program: Dict[str, Any], sdn_program: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Merge data from ADEA program and optional SDN program into a unified structure.

    Args:
        adea_program: Program data from ADEA (PASS or CAAPID)
        sdn_program: Optional program data from SDN

    Returns:
        Merged program data
    """
    # Determine program type
    program_type = (
        "residency"
        if "pass" in adea_program.get("adea_url", "").lower()
        else "advanced_standing"
    )

    # Start with ADEA data
    merged = {
        "name": adea_program.get("name", ""),
        "state": normalize_state(adea_program.get("state", "")),
        "type": program_type,
        "degree": adea_program.get("type", "")
        if program_type == "advanced_standing"
        else None,
        "speciality": adea_program.get("type", "")
        if program_type == "residency"
        else None,
        "description": adea_program.get("description", ""),
        "information": adea_program.get("information", {}),
        "requirements": adea_program.get("requirements", []),
        "contact": adea_program.get("contact", {}),
        "adea_url": adea_program.get("adea_url", ""),
        "application_deadline": adea_program.get("application_deadline", ""),
        "start_date": adea_program.get("start_date", ""),
        "last_updated": adea_program.get("last_updated", ""),
        # Initialize SDN fields as None
        "average_dat": None,
        "average_gpa": None,
        "tuition_in_state": None,
        "tuition_out_of_state": None,
        "website": adea_program.get("information", {}).get("program_website", ""),
        "interview_feedback_summary": None,
        "school_review_summary": None,
        "common_secondary_essay_questions": None,
        "about_the_school": None,
        "curriculum": None,
        "facilities": None,
        "insights": None,
        "school_address": None,
        "links": None,
    }

    # Merge SDN data if available
    if sdn_program:
        merged.update(
            {
                "average_dat": sdn_program.get("average_dat"),
                "average_gpa": sdn_program.get("average_gpa"),
                "tuition_in_state": sdn_program.get("tuition_in_state"),
                "tuition_out_of_state": sdn_program.get("tuition_out_of_state"),
                "website": sdn_program.get("website") or merged.get("website"),
                "interview_feedback_summary": sdn_program.get(
                    "interview_feedback_summary"
                ),
                "school_review_summary": sdn_program.get("school_review_summary"),
                "common_secondary_essay_questions": sdn_program.get(
                    "common_secondary_essay_questions"
                ),
                "about_the_school": sdn_program.get("about_the_school"),
                "curriculum": sdn_program.get("curriculum"),
                "facilities": sdn_program.get("facilities"),
                "insights": sdn_program.get("insights"),
                "school_address": sdn_program.get("school_address"),
                "links": sdn_program.get("links"),
            }
        )

    return merged


def create_dental_programs_collection(mongodb: MongoDBResource) -> Dict[str, Any]:
    """
    Create a new MongoDB collection called 'dental_programs' by merging data from
    'adea_pass_programs', 'adea_caapid_programs', and 'sdn_dental_schools' collections.

    The resulting collection contains all fields from all sources with fuzzy matching
    to identify programs that exist in multiple sources.

    Returns:
        Dict containing the operation result with status, message, and count
    """
    try:
        # Get the source collections
        adea_pass_collection = mongodb.get_collection("adea_pass_programs")
        adea_caapid_collection = mongodb.get_collection("adea_caapid_programs")
        sdn_collection = mongodb.get_collection("sdn_dental_schools")

        # Get the target collection
        dental_programs_collection = mongodb.get_collection("dental_programs")

        # Clear existing data in the target collection
        dental_programs_collection.delete_many({})

        # Fetch all programs from each source
        pass_programs = list(adea_pass_collection.find({}))
        caapid_programs = list(adea_caapid_collection.find({}))
        sdn_programs = list(sdn_collection.find({}))

        logger.info(f"Processing {len(pass_programs)} ADEA PASS programs")
        logger.info(f"Processing {len(caapid_programs)} ADEA CAAPID programs")
        logger.info(f"Processing {len(sdn_programs)} SDN dental schools")

        # Prepare SDN programs for matching (add type field)
        sdn_programs_with_type = []
        for program in sdn_programs:
            program_copy = program.copy()
            program_copy["type"] = "advanced_standing"
            sdn_programs_with_type.append(program_copy)

        merged_programs = []
        matched_sdn_programs = set()  # Track which SDN programs have been matched

        # Process ADEA PASS programs (residency programs)
        for program in pass_programs:
            # Try to find matching SDN program
            sdn_match = find_best_match(
                program.get("name", ""),
                "residency",
                sdn_programs_with_type,
                threshold=0.6,
            )

            if sdn_match:
                matched_sdn_programs.add(sdn_match["_id"])
                logger.info(
                    f"Matched ADEA PASS '{program.get('name', '')}' with SDN '{sdn_match.get('name', '')}'"
                )

            merged_program = merge_program_data(program, sdn_match)
            merged_programs.append(merged_program)

        # Process ADEA CAAPID programs (advanced standing programs)
        for program in caapid_programs:
            # Try to find matching SDN program
            sdn_match = find_best_match(
                program.get("name", ""),
                "advanced_standing",
                sdn_programs_with_type,
                threshold=0.6,
            )

            if sdn_match:
                matched_sdn_programs.add(sdn_match["_id"])
                logger.info(
                    f"Matched ADEA CAAPID '{program.get('name', '')}' with SDN '{sdn_match.get('name', '')}'"
                )

            merged_program = merge_program_data(program, sdn_match)
            merged_programs.append(merged_program)

        # Add unmatched SDN programs as standalone dental schools
        unmatched_sdn_count = 0
        for program in sdn_programs_with_type:
            if program["_id"] not in matched_sdn_programs:
                # Create a standalone SDN program entry
                standalone_program = {
                    "name": program.get("name", ""),
                    "state": normalize_state(program.get("state", "")),
                    "type": "advanced_standing",
                    "degree": program.get("degree", ""),
                    "speciality": None,
                    "description": program.get("about_the_school", ""),
                    "information": {},
                    "requirements": [],
                    "contact": {},
                    "adea_url": "",
                    "application_deadline": "",
                    "start_date": "",
                    "last_updated": program.get("last_updated", ""),
                    "average_dat": program.get("average_dat"),
                    "average_gpa": program.get("average_gpa"),
                    "tuition_in_state": program.get("tuition_in_state"),
                    "tuition_out_of_state": program.get("tuition_out_of_state"),
                    "website": program.get("website", ""),
                    "interview_feedback_summary": program.get(
                        "interview_feedback_summary"
                    ),
                    "school_review_summary": program.get("school_review_summary"),
                    "common_secondary_essay_questions": program.get(
                        "common_secondary_essay_questions"
                    ),
                    "about_the_school": program.get("about_the_school"),
                    "curriculum": program.get("curriculum"),
                    "facilities": program.get("facilities"),
                    "insights": program.get("insights"),
                    "school_address": program.get("school_address"),
                    "links": program.get("links"),
                }
                merged_programs.append(standalone_program)
                unmatched_sdn_count += 1

        # Insert merged programs into the new collection with deduplication
        if merged_programs:
            # Use deduplication logic to avoid duplicates
            result = upsert_dental_programs(mongodb, merged_programs)

            logger.info(
                f"Successfully created dental_programs collection with {len(merged_programs)} programs"
            )

            return {
                "status": result["status"],
                "message": result["message"],
                "count": result["total_processed"],
                "inserted": result["inserted"],
                "updated": result["updated"],
                "skipped": result["skipped"],
                "pass_programs_count": len(pass_programs),
                "caapid_programs_count": len(caapid_programs),
                "sdn_programs_count": len(sdn_programs),
                "matched_sdn_count": len(matched_sdn_programs),
                "unmatched_sdn_count": unmatched_sdn_count,
            }
        else:
            logger.warning("No programs found to merge")
            return {
                "status": "error",
                "message": "No programs found to merge",
                "count": 0,
                "inserted_ids": 0,
                "pass_programs_count": 0,
                "caapid_programs_count": 0,
                "sdn_programs_count": 0,
                "matched_sdn_count": 0,
                "unmatched_sdn_count": 0,
            }

    except Exception as e:
        logger.error(f"Error creating dental_programs collection: {e}")
        return {
            "status": "error",
            "message": f"Error creating dental_programs collection: {str(e)}",
            "count": 0,
            "inserted_ids": 0,
            "pass_programs_count": 0,
            "caapid_programs_count": 0,
            "sdn_programs_count": 0,
            "matched_sdn_count": 0,
            "unmatched_sdn_count": 0,
        }


def get_dental_programs_count(mongodb: MongoDBResource) -> int:
    """
    Get the count of programs in the dental_programs collection.

    Returns:
        int: Number of programs in the collection
    """
    try:
        collection = mongodb.get_collection("dental_programs")
        return collection.count_documents({})
    except Exception as e:
        logger.error(f"Error getting dental_programs count: {e}")
        return 0


def get_dental_programs_by_type(
    mongodb: MongoDBResource, program_type: str
) -> List[Dict[str, Any]]:
    """
    Get dental programs filtered by type (residency, advanced_standing, or dental_school).

    Args:
        program_type: Either "residency", "advanced_standing", or "dental_school"

    Returns:
        List of programs matching the specified type
    """
    try:
        collection = mongodb.get_collection("dental_programs")
        return list(collection.find({"type": program_type}))
    except Exception as e:
        logger.error(f"Error getting dental programs by type {program_type}: {e}")
        return []


def get_dental_programs_by_state(
    mongodb: MongoDBResource, state: str
) -> List[Dict[str, Any]]:
    """
    Get dental programs filtered by state.

    Args:
        state: State name or abbreviation

    Returns:
        List of programs in the specified state
    """
    try:
        collection = mongodb.get_collection("dental_programs")
        return list(collection.find({"state": {"$regex": state, "$options": "i"}}))
    except Exception as e:
        logger.error(f"Error getting dental programs by state {state}: {e}")
        return []


def search_dental_programs(
    mongodb: MongoDBResource,
    query: str,
    program_type: Optional[str] = None,
    state: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search dental programs by name with optional filters.

    Args:
        mongodb: MongoDB resource instance
        query: Search query for program name
        program_type: Optional program type filter
        state: Optional state filter

    Returns:
        List of matching programs
    """
    try:
        collection = mongodb.get_collection("dental_programs")

        # Build search criteria
        search_criteria = {"name": {"$regex": query, "$options": "i"}}

        if program_type:
            search_criteria["type"] = program_type

        if state:
            search_criteria["state"] = {"$regex": state, "$options": "i"}

        return list(collection.find(search_criteria))
    except Exception as e:
        logger.error(f"Error searching dental programs with query '{query}': {e}")
        return []


def get_dental_programs_with_sdn_data(mongodb: MongoDBResource) -> List[Dict[str, Any]]:
    """
    Get dental programs that have SDN data merged (non-null SDN fields).

    Returns:
        List of programs with SDN data
    """
    try:
        collection = mongodb.get_collection("dental_programs")
        return list(
            collection.find(
                {
                    "$or": [
                        {"average_dat": {"$ne": None}},
                        {"average_gpa": {"$ne": None}},
                        {"tuition_in_state": {"$ne": None}},
                        {"tuition_out_of_state": {"$ne": None}},
                        {"interview_feedback_summary": {"$ne": None}},
                        {"school_review_summary": {"$ne": None}},
                    ]
                }
            )
        )
    except Exception as e:
        logger.error(f"Error getting dental programs with SDN data: {e}")
        return []


def get_dental_programs_statistics(mongodb: MongoDBResource) -> Dict[str, Any]:
    """
    Get statistics about the dental programs collection.

    Returns:
        Dictionary with various statistics
    """
    try:
        collection = mongodb.get_collection("dental_programs")

        # Get total count
        total_count = collection.count_documents({})

        # Get counts by type
        type_counts = {}
        for program_type in ["residency", "advanced_standing"]:
            type_counts[program_type] = collection.count_documents(
                {"type": program_type}
            )

        # Get count of programs with SDN data
        sdn_data_count = collection.count_documents(
            {
                "$or": [
                    {"average_dat": {"$ne": None}},
                    {"average_gpa": {"$ne": None}},
                    {"tuition_in_state": {"$ne": None}},
                    {"tuition_out_of_state": {"$ne": None}},
                ]
            }
        )

        # Get state distribution
        state_pipeline = [
            {"$group": {"_id": "$state", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        state_distribution = list(collection.aggregate(state_pipeline))

        return {
            "total_programs": total_count,
            "by_type": type_counts,
            "with_sdn_data": sdn_data_count,
            "state_distribution": state_distribution,
        }
    except Exception as e:
        logger.error(f"Error getting dental programs statistics: {e}")
        return {}


def create_sdn_dental_schools_collection(
    mongodb: MongoDBResource, schools_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create a new MongoDB collection called 'sdn_dental_schools' from scraped SDN data.

    Args:
        mongodb: MongoDB resource instance
        schools_data: List of school data dictionaries from SDN scraping

    Returns:
        Dict containing the operation result with status, message, and count
    """
    try:
        # Get the target collection
        sdn_collection = mongodb.get_collection("sdn_dental_schools")

        # Clear existing data in the target collection
        sdn_collection.delete_many({})

        # Insert school data into the collection
        if schools_data:
            result = sdn_collection.insert_many(schools_data)

            logger.info(
                f"Successfully created sdn_dental_schools collection with {len(schools_data)} schools"
            )

            return {
                "status": "success",
                "message": f"Successfully created sdn_dental_schools collection with {len(schools_data)} schools",
                "count": len(schools_data),
                "inserted_ids": len(result.inserted_ids),
            }
        else:
            logger.warning("No SDN schools found to insert")
            return {
                "status": "error",
                "message": "No SDN schools found to insert",
                "count": 0,
                "inserted_ids": 0,
            }

    except Exception as e:
        logger.error(f"Error creating sdn_dental_schools collection: {e}")
        return {
            "status": "error",
            "message": f"Error creating sdn_dental_schools collection: {str(e)}",
            "count": 0,
            "inserted_ids": 0,
        }


def get_sdn_dental_schools_count(mongodb: MongoDBResource) -> int:
    """
    Get the count of schools in the sdn_dental_schools collection.

    Returns:
        int: Number of schools in the collection
    """
    try:
        collection = mongodb.get_collection("sdn_dental_schools")
        return collection.count_documents({})
    except Exception as e:
        logger.error(f"Error getting sdn_dental_schools count: {e}")
        return 0


def check_dental_programs_collection(mongodb: MongoDBResource) -> Dict[str, Any]:
    """Check if dental_programs collection exists and has data."""
    try:
        dental_programs_collection = mongodb.get_collection("dental_programs")
        count = dental_programs_collection.count_documents({})

        # Get a sample document to see the structure
        sample = dental_programs_collection.find_one({})

        logger.info(f"dental_programs collection has {count} documents")
        if sample:
            logger.info(f"Sample document keys: {list(sample.keys())}")
            logger.info(f"Sample name: {sample.get('name', 'N/A')}")
            logger.info(f"Sample type: {sample.get('type', 'N/A')}")

        return {
            "exists": True,
            "count": count,
            "sample_keys": list(sample.keys()) if sample else [],
            "sample_name": sample.get("name", "N/A") if sample else "N/A",
        }
    except Exception as e:
        logger.error(f"Error checking dental_programs collection: {e}")
        return {"exists": False, "error": str(e), "count": 0}


def create_dental_schools_collection(mongodb: MongoDBResource) -> Dict[str, Any]:
    """
    Create a new MongoDB collection called 'dental_schools' by aggregating programs
    from the 'dental_programs' collection and enriching with research criteria.

    This collection supports the research spreadsheet functionality by providing
    school-level data with comprehensive criteria for comparison.

    Returns:
        Dict containing the operation result with status, message, and count
    """
    try:
        logger.info("Starting dental_schools collection creation...")

        # First check if dental_programs collection exists and has data
        logger.info("Checking dental_programs collection...")
        programs_check = check_dental_programs_collection(mongodb)
        if not programs_check["exists"]:
            logger.error(
                f"dental_programs collection does not exist: {programs_check.get('error', 'Unknown error')}"
            )
            return {
                "status": "error",
                "message": f"dental_programs collection does not exist: {programs_check.get('error', 'Unknown error')}",
                "count": 0,
                "inserted_ids": 0,
            }

        if programs_check["count"] == 0:
            logger.error("dental_programs collection is empty")
            return {
                "status": "error",
                "message": "dental_programs collection is empty",
                "count": 0,
                "inserted_ids": 0,
            }

        # Get the source collection
        dental_programs_collection = mongodb.get_collection("dental_programs")
        dental_schools_collection = mongodb.get_collection("dental_schools")

        logger.info("Collections retrieved successfully")

        # Clear existing data
        logger.info("Clearing existing dental_schools data...")
        delete_result = dental_schools_collection.delete_many({})
        logger.info(f"Deleted {delete_result.deleted_count} existing documents")

        # Fetch all programs
        logger.info("Fetching programs from dental_programs collection...")
        programs = list(dental_programs_collection.find({}))
        logger.info(f"Processing {len(programs)} programs to create schools collection")

        if not programs:
            logger.warning("No programs found in dental_programs collection!")
            return {
                "status": "error",
                "message": "No programs found in dental_programs collection",
                "count": 0,
                "inserted_ids": 0,
            }

        # Group programs by school name
        schools_data = {}
        processed_count = 0
        skipped_count = 0

        logger.info("Starting to process programs and group by school...")

        for program in programs:
            try:
                school_name = program.get("name", "").strip()
                if not school_name:
                    skipped_count += 1
                    continue

                # Extract school name (remove program-specific suffixes)
                original_name = school_name
                school_name = normalize_school_name(school_name)

                if processed_count < 5:  # Log first few for debugging
                    logger.info(
                        f"Processing program: '{original_name}' -> '{school_name}'"
                    )
                    logger.info(f"Program keys: {list(program.keys())}")
                    logger.info(f"Program type: {program.get('type', 'N/A')}")
                    logger.info(
                        f"Program school_address: {program.get('school_address', 'N/A')}"
                    )
                    logger.info(
                        f"Program information: {program.get('information', 'N/A')}"
                    )

                if school_name not in schools_data:
                    # Safely get school_address, handling both dict and string cases
                    school_address = program.get("school_address")
                    if isinstance(school_address, dict):
                        city = school_address.get("city", "")
                    elif isinstance(school_address, str):
                        # Extract city from address string (first part before comma)
                        city = (
                            school_address.split(",")[0].strip()
                            if school_address
                            else ""
                        )
                    else:
                        city = ""

                    schools_data[school_name] = {
                        "school_name": school_name,
                        "city": city,
                        "state": program.get("state", ""),
                        "website": program.get("website", ""),
                        "programs": [],
                        "status": set(),
                        "program_types": set(),
                        "specialties": set(),
                        "degrees": set(),
                        # School-level aggregated data (will be calculated later)
                        "total_programs": 0,
                        "program_count_by_type": {},
                        "program_count_by_specialty": {},
                    }

                # Add program to school
                program_type = program.get("type", "")
                specialty = program.get("speciality", "")
                degree = program.get("degree", "")

                schools_data[school_name]["programs"].append(
                    {
                        "name": program.get("name", ""),
                        "type": program_type,
                        "specialty": specialty,
                        "degree": degree,
                        "description": program.get("description", ""),
                        "requirements": program.get("requirements", []),
                        "contact": program.get("contact", {}),
                        "adea_url": program.get("adea_url", ""),
                        # Program-level properties
                        "tuition_in_state": program.get("tuition_in_state"),
                        "tuition_out_of_state": program.get("tuition_out_of_state"),
                        "application_deadline": program.get("application_deadline", ""),
                        "start_date": program.get("start_date", ""),
                        "last_updated": program.get("last_updated", ""),
                        "average_dat": program.get("average_dat"),
                        "average_gpa": program.get("average_gpa"),
                        "interview_feedback_summary": program.get(
                            "interview_feedback_summary"
                        ),
                        "school_review_summary": program.get("school_review_summary"),
                        "about_the_school": program.get("about_the_school"),
                        "curriculum": program.get("curriculum"),
                        "facilities": program.get("facilities"),
                        "school_address": program.get("school_address"),
                        "links": program.get("links"),
                        "insights": program.get("insights"),
                        # Program-specific research criteria
                        "evaluation_requirements": {
                            "ece_required": True,  # Default for international programs
                            "wes_required": False,
                        },
                        "toefl_ielts_requirement": {
                            "toefl_minimum": 100,  # Default
                            "ielts_minimum": 7.0,
                        },
                        "clinical_experience_required": "2 years minimum",  # Default
                        "letter_of_recommendation": {
                            "count": 3,
                            "sources": ["faculty", "supervisor", "colleague"],
                        },
                        "bench_test_requirement": True,
                        "interview_type": "In-person",  # Default
                        "visa_requirements": "F-1 student visa",  # Default
                        "research_opportunities": [
                            "Basic science",
                            "Clinical research",
                        ],
                        "scholarships_financial_aid": {
                            "merit_based": True,
                            "need_based": True,
                            "international_eligible": True,
                        },
                        "class_size": 25,  # Default
                        "curriculum_structure": "Integrated clinical and didactic",
                        "clinical_training_opportunities": "Extensive patient exposure",
                        "acceptance_rates_competitiveness": {
                            "asp_seats_offered": 15,  # Default
                            "inbde_range": "85-95",
                            "gpa_range": "3.5-3.8",
                            "international_friendly": True,
                        },
                        "post_graduation_opportunities": {
                            "private_practice_rate": 0.7,
                            "specialization_rate": 0.3,
                            "residency_match_rate": 0.85,
                            "networking_opportunities": "Strong alumni network",
                        },
                    }
                )

                # Update sets for aggregation
                if program_type:
                    schools_data[school_name]["program_types"].add(program_type)
                    # Count programs by type
                    if (
                        program_type
                        not in schools_data[school_name]["program_count_by_type"]
                    ):
                        schools_data[school_name]["program_count_by_type"][
                            program_type
                        ] = 0
                    schools_data[school_name]["program_count_by_type"][
                        program_type
                    ] += 1

                if specialty:
                    schools_data[school_name]["specialties"].add(specialty)
                    # Count programs by specialty
                    if (
                        specialty
                        not in schools_data[school_name]["program_count_by_specialty"]
                    ):
                        schools_data[school_name]["program_count_by_specialty"][
                            specialty
                        ] = 0
                    schools_data[school_name]["program_count_by_specialty"][
                        specialty
                    ] += 1

                if degree:
                    schools_data[school_name]["degrees"].add(degree)

                # Determine status based on program type and other factors
                if program_type == "advanced_standing":
                    schools_data[school_name]["status"].add("Non-residents")
                elif program_type == "residency":
                    schools_data[school_name]["status"].add("Citizens & Residents")

                # Update total program count
                schools_data[school_name]["total_programs"] += 1

                processed_count += 1

            except Exception as e:
                logger.error(f"Error processing program {processed_count}: {e}")
                logger.error(f"Program data: {program}")
                skipped_count += 1
                continue

        logger.info(
            f"Processed {processed_count} programs, skipped {skipped_count} programs"
        )
        logger.info(f"Found {len(schools_data)} unique schools")

        # Convert sets to lists and add research criteria
        schools_list = []
        logger.info("Converting sets to lists and adding research criteria...")
        for school_name, school_data in schools_data.items():
            # Convert sets to lists
            school_data["status"] = list(school_data["status"])
            school_data["program_types"] = list(school_data["program_types"])
            school_data["specialties"] = list(school_data["specialties"])
            school_data["degrees"] = list(school_data["degrees"])

            # Add only school-level research criteria
            school_data.update(
                {
                    # School-level aggregated information
                    "total_programs": school_data.get("total_programs", 0),
                    "program_count_by_type": school_data.get(
                        "program_count_by_type", {}
                    ),
                    "program_count_by_specialty": school_data.get(
                        "program_count_by_specialty", {}
                    ),
                    # School-level research criteria (only what applies to the entire school)
                    "alumni_network": "Strong international network",
                    "student_support_services": [
                        "Academic advising",
                        "Career counseling",
                    ],
                    "study_life_balance_support": [
                        "Mental health services",
                        "Study groups",
                    ],
                    "career_development_resources": [
                        "Job placement",
                        "Residency matching",
                    ],
                    "externship_internship_options": [
                        "Local clinics",
                        "International rotations",
                    ],
                    "technology_facilities": "State-of-the-art simulation lab",
                    "location_cost_of_living": {
                        "city": school_data.get("city", ""),
                        "cost_of_living_index": 85.2,  # Default
                        "housing_avg": 1200,  # Default
                    },
                    "dual_degree_opportunities": ["DDS/PhD", "DDS/MPH"],
                    "leadership_opportunities": [
                        "Student government",
                        "Research leadership",
                    ],
                    "extracurricular_networking": [
                        "Dental societies",
                        "International groups",
                    ],
                    "student_reviews_feedback": {
                        "overall_rating": 4.2,  # Default
                        "pros": ["Great faculty", "Strong clinical training"],
                        "cons": ["High tuition", "Competitive"],
                    },
                    "school_mission_focus": {
                        "emphasis": "Clinical training",
                        "prioritization": "Public health",
                        "mission_alignment_score": 8.5,
                    },
                    "financial_aid_scholarships": {
                        "international_scholarships": True,
                        "research_assistantships": True,
                        "funding_partnerships": ["Fulbright", "Rotary"],
                    },
                }
            )

            schools_list.append(school_data)

        logger.info(f"Prepared {len(schools_list)} schools for insertion")

        # Insert schools into collection
        if schools_list:
            logger.info("Inserting schools into dental_schools collection...")
            result = dental_schools_collection.insert_many(schools_list)

            logger.info(
                f"Successfully created dental_schools collection with {len(schools_list)} schools"
            )
            logger.info(f"Inserted {len(result.inserted_ids)} documents")

            return {
                "status": "success",
                "message": f"Successfully created dental_schools collection with {len(schools_list)} schools",
                "count": len(schools_list),
                "inserted_ids": len(result.inserted_ids),
            }
        else:
            logger.warning("No schools found to insert")
            return {
                "status": "error",
                "message": "No schools found to insert",
                "count": 0,
                "inserted_ids": 0,
            }

    except Exception as e:
        logger.error(f"Error creating dental_schools collection: {e}")
        return {
            "status": "error",
            "message": f"Error creating dental_schools collection: {str(e)}",
            "count": 0,
            "inserted_ids": 0,
        }


def normalize_school_name(school_name: str) -> str:
    """
    Normalize school name by removing program-specific suffixes and standardizing format.

    Args:
        school_name: Raw school name from program data

    Returns:
        Normalized school name
    """
    # Remove common program suffixes
    suffixes_to_remove = [
        " School of Dentistry",
        " College of Dentistry",
        " School of Dental Medicine",
        " College of Dental Medicine",
        " - Advanced Standing Program",
        " - Residency Program",
        " Program",
        " Department",
    ]

    normalized = school_name
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break

    return normalized.strip()


def search_dental_schools(
    mongodb: MongoDBResource,
    filters: Dict[str, Any] = None,
    sort_by: str = "school_name",
    sort_order: int = 1,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Search dental schools based on various criteria.

    Args:
        mongodb: MongoDB resource instance
        filters: Dictionary of filter criteria
        sort_by: Field to sort by
        sort_order: 1 for ascending, -1 for descending
        limit: Maximum number of results

    Returns:
        List of matching schools
    """
    try:
        collection = mongodb.get_collection("dental_schools")

        # Build query from filters
        query = {}
        if filters:
            for key, value in filters.items():
                if key == "state" and value:
                    query["state"] = {"$regex": value, "$options": "i"}
                elif key == "city" and value:
                    query["city"] = {"$regex": value, "$options": "i"}
                elif key == "status" and value:
                    query["status"] = {
                        "$in": value if isinstance(value, list) else [value]
                    }
                elif key == "program_types" and value:
                    query["program_types"] = {
                        "$in": value if isinstance(value, list) else [value]
                    }
                elif key == "specialties" and value:
                    query["specialties"] = {
                        "$in": value if isinstance(value, list) else [value]
                    }
                elif key == "min_tuition" and value:
                    query["tuition_fees.out_of_state"] = {"$gte": value}
                elif key == "max_tuition" and value:
                    query["tuition_fees.out_of_state"] = {"$lte": value}
                elif key == "international_friendly" and value:
                    query["acceptance_rates_competitiveness.international_friendly"] = (
                        value
                    )
                elif key == "min_rating" and value:
                    query["student_reviews_feedback.overall_rating"] = {"$gte": value}

        # Execute query
        cursor = collection.find(query).sort(sort_by, sort_order).limit(limit)
        results = list(cursor)

        logger.info(f"Found {len(results)} schools matching criteria")
        return results

    except Exception as e:
        logger.error(f"Error searching dental schools: {e}")
        return []


def get_dental_schools_statistics(mongodb: MongoDBResource) -> Dict[str, Any]:
    """
    Get statistics about the dental schools collection.

    Returns:
        Dictionary containing various statistics
    """
    try:
        collection = mongodb.get_collection("dental_schools")

        # Basic counts
        total_schools = collection.count_documents({})

        # Count by state
        state_pipeline = [
            {"$group": {"_id": "$state", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        state_counts = list(collection.aggregate(state_pipeline))

        # Count by program types
        program_type_pipeline = [
            {"$unwind": "$program_types"},
            {"$group": {"_id": "$program_types", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        program_type_counts = list(collection.aggregate(program_type_pipeline))

        # Count by specialties
        specialty_pipeline = [
            {"$unwind": "$specialties"},
            {"$group": {"_id": "$specialties", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        specialty_counts = list(collection.aggregate(specialty_pipeline))

        return {
            "total_schools": total_schools,
            "by_state": state_counts,
            "by_program_type": program_type_counts,
            "by_specialty": specialty_counts,
        }

    except Exception as e:
        logger.error(f"Error getting dental schools statistics: {e}")
        return {}


def upsert_adea_programs(
    mongodb: MongoDBResource, programs: List[Dict[str, Any]], collection_name: str
) -> Dict[str, Any]:
    """
    Upsert ADEA programs to avoid duplicates based on name, type, and state combination.

    Args:
        mongodb: MongoDB resource instance
        programs: List of program dictionaries to upsert
        collection_name: Name of the collection to upsert to

    Returns:
        Dict containing operation results with counts of inserted, updated, and skipped programs
    """
    from dagster import get_dagster_logger

    dagster_logger = get_dagster_logger()

    try:
        collection = mongodb.get_collection(collection_name)

        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        duplicate_count = 0

        dagster_logger.info(
            f"Starting upsert process for {len(programs)} programs in {collection_name}"
        )

        # Log first few programs to verify data structure
        dagster_logger.info("Sample programs being processed:")
        for i, program in enumerate(programs[:3]):
            dagster_logger.info(
                f"  Program {i + 1}: {program.get('name', 'N/A')} ({program.get('type', 'N/A')}, {program.get('state', 'N/A')})"
            )

        for i, program in enumerate(programs):
            # Extract the unique identifier fields
            name = program.get("name", "").strip()
            program_type = program.get("type", "").strip()
            state = program.get("state", "").strip()

            if not name or not program_type or not state:
                dagster_logger.warning(
                    f"Skipping program {i + 1}/{len(programs)} with missing required fields - Name: '{name}', Type: '{program_type}', State: '{state}'"
                )
                skipped_count += 1
                continue

            # Create query to find existing program using more specific fields
            # Include program size and length to distinguish between different programs from same institution
            program_size = program.get("information", {}).get("size", "").strip()
            program_length = program.get("information", {}).get("length", "").strip()

            # Use ADEA URL as primary unique identifier since it's most specific
            adea_url = program.get("adea_url", "").strip()

            if adea_url:
                # Use ADEA URL as the primary unique identifier
                query = {"adea_url": adea_url}
            else:
                # Fallback to name + type + state + size + length for programs without ADEA URL
                query = {
                    "name": name,
                    "type": program_type,
                    "state": state,
                    "information.size": program_size,
                    "information.length": program_length,
                }

            # Check if program already exists
            existing_program = collection.find_one(query)

            if existing_program:
                # This is a duplicate - log detailed information
                duplicate_count += 1
                dagster_logger.warning(
                    f"DUPLICATE FOUND #{duplicate_count}: {name} ({program_type}, {state})"
                )
                dagster_logger.info(
                    f"  Existing program ID: {existing_program.get('_id')}"
                )
                dagster_logger.info(
                    f"  Existing program ADEA URL: {existing_program.get('adea_url', 'N/A')}"
                )
                dagster_logger.info(
                    f"  New program ADEA URL: {program.get('adea_url', 'N/A')}"
                )

                # Check if URLs are different (this would indicate a real issue)
                existing_url = existing_program.get("adea_url", "")
                new_url = program.get("adea_url", "")
                if existing_url != new_url:
                    dagster_logger.error(
                        f"  ⚠️  DIFFERENT URLs for same program! Existing: {existing_url}, New: {new_url}"
                    )

                # Update existing program with new data
                # Remove _id from program data to avoid conflicts
                program_data = {k: v for k, v in program.items() if k != "_id"}

                result = collection.update_one(query, {"$set": program_data})

                if result.modified_count > 0:
                    updated_count += 1
                    dagster_logger.info(
                        f"  ✅ Updated existing program: {name} ({program_type}, {state})"
                    )
                else:
                    skipped_count += 1
                    dagster_logger.info(
                        f"  ⏭️  No changes needed for program: {name} ({program_type}, {state})"
                    )
            else:
                # Insert new program
                result = collection.insert_one(program)
                if result.inserted_id:
                    inserted_count += 1
                    if (i + 1) % 100 == 0 or i == len(programs) - 1:
                        dagster_logger.info(
                            f"Inserted new program {i + 1}/{len(programs)}: {name} ({program_type}, {state})"
                        )
                else:
                    skipped_count += 1
                    dagster_logger.warning(
                        f"Failed to insert program: {name} ({program_type}, {state})"
                    )

        dagster_logger.info(
            f"Upsert completed - Inserted: {inserted_count}, Updated: {updated_count}, Skipped: {skipped_count}, Duplicates: {duplicate_count}"
        )

        return {
            "status": "success",
            "message": f"Upserted {len(programs)} programs to {collection_name}",
            "total_processed": len(programs),
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "duplicates": duplicate_count,
            "collection_name": collection_name,
        }

    except Exception as e:
        dagster_logger.error(f"Error upserting programs to {collection_name}: {e}")
        return {
            "status": "error",
            "message": f"Error upserting programs to {collection_name}: {str(e)}",
            "total_processed": len(programs) if programs else 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "duplicates": 0,
            "collection_name": collection_name,
        }


def upsert_dental_programs(
    mongodb: MongoDBResource, programs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Upsert dental programs to avoid duplicates based on name, type, and state combination.
    This function is specifically for the merged dental_programs collection.

    Args:
        mongodb: MongoDB resource instance
        programs: List of program dictionaries to upsert

    Returns:
        Dict containing operation results with counts of inserted, updated, and skipped programs
    """
    try:
        collection = mongodb.get_collection("dental_programs")

        inserted_count = 0
        updated_count = 0
        skipped_count = 0

        for program in programs:
            # Extract the unique identifier fields
            name = program.get("name", "").strip()
            program_type = program.get("type", "").strip()
            state = program.get("state", "").strip()

            if not name or not program_type or not state:
                logger.warning(
                    f"Skipping program with missing required fields: {program}"
                )
                skipped_count += 1
                continue

            # Create query to find existing program using more specific fields
            # Include program size and length to distinguish between different programs from same institution
            program_size = program.get("information", {}).get("size", "").strip()
            program_length = program.get("information", {}).get("length", "").strip()

            # Use ADEA URL as primary unique identifier since it's most specific
            adea_url = program.get("adea_url", "").strip()

            if adea_url:
                # Use ADEA URL as the primary unique identifier
                query = {"adea_url": adea_url}
            else:
                # Fallback to name + type + state + size + length for programs without ADEA URL
                query = {
                    "name": name,
                    "type": program_type,
                    "state": state,
                    "information.size": program_size,
                    "information.length": program_length,
                }

            # Check if program already exists
            existing_program = collection.find_one(query)

            if existing_program:
                # Update existing program with new data
                # Remove _id from program data to avoid conflicts
                program_data = {k: v for k, v in program.items() if k != "_id"}

                result = collection.update_one(query, {"$set": program_data})

                if result.modified_count > 0:
                    updated_count += 1
                    logger.info(
                        f"Updated existing dental program: {name} ({program_type}, {state})"
                    )
                else:
                    skipped_count += 1
                    logger.info(
                        f"No changes needed for dental program: {name} ({program_type}, {state})"
                    )
            else:
                # Insert new program
                result = collection.insert_one(program)
                if result.inserted_id:
                    inserted_count += 1
                    logger.info(
                        f"Inserted new dental program: {name} ({program_type}, {state})"
                    )
                else:
                    skipped_count += 1
                    logger.warning(
                        f"Failed to insert dental program: {name} ({program_type}, {state})"
                    )

        return {
            "status": "success",
            "message": f"Upserted {len(programs)} programs to dental_programs",
            "total_processed": len(programs),
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "collection_name": "dental_programs",
        }

    except Exception as e:
        logger.error(f"Error upserting dental programs: {e}")
        return {
            "status": "error",
            "message": f"Error upserting dental programs: {str(e)}",
            "total_processed": len(programs) if programs else 0,
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "collection_name": "dental_programs",
        }
