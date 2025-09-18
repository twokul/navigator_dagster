from typing import List, Dict, Any
import logging
from .resources import MongoDBResource

logger = logging.getLogger(__name__)


def create_dental_programs_collection(mongodb: MongoDBResource) -> Dict[str, Any]:
    """
    Create a new MongoDB collection called 'dental_programs' by merging data from
    'adea_pass_programs' and 'adea_caapid_programs' collections.

    The resulting collection contains:
    - name: Program name
    - state: State where the program is located
    - type: "advanced_standing" for adea_caapid_programs, "residency" for adea_pass_programs
    - degree: Degree type (only for adea_caapid_programs, null for adea_pass_programs)
    - speciality: Specialty type (only for adea_pass_programs, null for adea_caapid_programs)
    - description: Program description
    - information: Additional program information
    - requirements: Program requirements
    - contact: Contact information

    Returns:
        Dict containing the operation result with status, message, and count
    """
    try:
        # Get the source collections
        adea_pass_collection = mongodb.get_collection("adea_pass_programs")
        adea_caapid_collection = mongodb.get_collection("adea_caapid_programs")

        # Get the target collection
        dental_programs_collection = mongodb.get_collection("dental_programs")

        # Clear existing data in the target collection
        dental_programs_collection.delete_many({})

        merged_programs = []

        # Process adea_pass_programs (residency programs)
        pass_programs = list(adea_pass_collection.find({}))
        logger.info(f"Processing {len(pass_programs)} ADEA PASS programs")

        for program in pass_programs:
            merged_program = {
                "name": program.get("name", ""),
                "state": program.get("state", ""),
                "type": "residency",
                "degree": None,
                "speciality": program.get(
                    "type", ""
                ),  # type field from adea_pass_programs
                "description": program.get("description", ""),
                "information": program.get("information", {}),
                "requirements": program.get("requirements", []),
                "contact": program.get("contact", {}),
            }
            merged_programs.append(merged_program)

        # Process adea_caapid_programs (advanced standing programs)
        caapid_programs = list(adea_caapid_collection.find({}))
        logger.info(f"Processing {len(caapid_programs)} ADEA CAAPID programs")

        for program in caapid_programs:
            merged_program = {
                "name": program.get("name", ""),
                "state": program.get("state", ""),
                "type": "advanced_standing",
                "degree": program.get(
                    "type", ""
                ),  # type field from adea_caapid_programs
                "speciality": None,
                "description": program.get("description", ""),
                "information": program.get("information", {}),
                "requirements": program.get("requirements", []),
                "contact": program.get("contact", {}),
            }
            merged_programs.append(merged_program)

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
    Get dental programs filtered by type (residency or advanced_standing).

    Args:
        program_type: Either "residency" or "advanced_standing"

    Returns:
        List of programs matching the specified type
    """
    try:
        collection = mongodb.get_collection("dental_programs")
        return list(collection.find({"type": program_type}))
    except Exception as e:
        logger.error(f"Error getting dental programs by type {program_type}: {e}")
        return []


def create_sdn_dental_schools_collection(mongodb: MongoDBResource, schools_data: List[Dict[str, Any]]) -> Dict[str, Any]:
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
