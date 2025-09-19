from typing import List, Dict, Any, Optional
import logging
import re
from difflib import SequenceMatcher
from .resources import MongoDBResource

logger = logging.getLogger(__name__)

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

        # Insert merged programs into the new collection
        if merged_programs:
            result = dental_programs_collection.insert_many(merged_programs)

            logger.info(
                f"Successfully created dental_programs collection with {len(merged_programs)} programs"
            )

            return {
                "status": "success",
                "message": f"Successfully created dental_programs collection with {len(merged_programs)} programs",
                "count": len(merged_programs),
                "inserted_ids": len(result.inserted_ids),
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
