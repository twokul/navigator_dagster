import dagster as dg
from .resources import MongoDBResource
from .mongo_utils import (
    create_dental_programs_collection,
    create_sdn_dental_schools_collection,
    create_dental_schools_collection,
    get_dental_schools_statistics,
)
from .utils import scrape_sdn_dental_schools

logger = dg.get_dagster_logger()


@dg.asset(
    deps=[
        "adea_pass_programs_website",
        "adea_caapid_programs_website",
        "sdn_dental_schools_website",
    ],
    description="Merged dental programs collection from ADEA PASS and CAAPID programs",
)
def dental_programs(mongodb: MongoDBResource):
    return create_dental_programs_collection(mongodb)


@dg.asset_check(asset="dental_programs")
def dental_programs_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("dental_programs")
    adea_pass_collection = mongodb.get_collection("adea_pass_programs")
    adea_caapid_collection = mongodb.get_collection("adea_caapid_programs")
    sdn_collection = mongodb.get_collection("sdn_dental_schools")

    adea_pass_row_count = adea_pass_collection.count_documents({})
    adea_caapid_row_count = adea_caapid_collection.count_documents({})
    sdn_row_count = sdn_collection.count_documents({})
    row_count = collection.count_documents({})
    sum_row_count = adea_pass_row_count + adea_caapid_row_count

    if row_count == 0 or sum_row_count == 0:
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "message": "Dental programs check failed - missing ADEA programs",
                "dental_programs_count": row_count,
                "adea_pass_count": adea_pass_row_count,
                "adea_caapid_count": adea_caapid_row_count,
                "sdn_count": sdn_row_count,
            },
        )

    return dg.AssetCheckResult(
        passed=True,
        metadata={
            "message": "Dental programs check passed",
            "dental_programs_count": row_count,
            "adea_pass_count": adea_pass_row_count,
            "adea_caapid_count": adea_caapid_row_count,
            "sdn_count": sdn_row_count,
        },
    )


@dg.asset_check(asset="adea_pass_programs_website")
def adea_pass_programs_website_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("adea_pass_programs")

    row_count = collection.count_documents({})

    # based on the number of programs in the ADEA PASS website
    if row_count != 808:
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "message": "ADEA PASS programs website check failed",
                "row_count": row_count,
            },
        )

    return dg.AssetCheckResult(
        passed=True,
        metadata={
            "message": "ADEA PASS programs website check passed",
            "row_count": row_count,
        },
    )


@dg.asset_check(asset="adea_caapid_programs_website")
def adea_caapid_programs_website_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("adea_caapid_programs")

    row_count = collection.count_documents({})

    # based on the number of programs in the ADEA CAAPID website
    if row_count != 43:
        return dg.AssetCheckResult(
            passed=False,
            metadata={
                "message": "ADEA PASS programs website check failed",
                "row_count": row_count,
            },
        )

    return dg.AssetCheckResult(
        passed=True,
        metadata={
            "message": "ADEA PASS programs website check passed",
            "row_count": row_count,
        },
    )


@dg.asset(
    description="Student Doctor Network website",
)
def sdn_dental_schools_website(mongodb: MongoDBResource):
    url = "https://www.studentdoctor.net/schools-database/schools/index/dental-school"

    # Scrape the data
    schools_data = scrape_sdn_dental_schools(url)

    # Store in MongoDB
    result = create_sdn_dental_schools_collection(mongodb, schools_data)

    return result


@dg.asset(
    deps=["dental_programs"],
    description="Dental schools collection for research and comparison",
)
def dental_schools(mongodb: MongoDBResource):
    logger.info("Starting dental_schools asset execution...")
    result = create_dental_schools_collection(mongodb)
    logger.info(f"Dental schools asset completed with result: {result}")
    return result


@dg.asset_check(asset="dental_schools")
def dental_schools_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    """Check that dental schools collection was created successfully."""
    try:
        stats = get_dental_schools_statistics(mongodb)
        school_count = stats.get("total_schools", 0)

        if school_count == 0:
            return dg.AssetCheckResult(
                passed=False,
                description="No schools found in dental_schools collection",
            )

        return dg.AssetCheckResult(
            passed=True,
            description=f"Successfully created dental_schools collection with {school_count} schools",
            metadata={
                "total_schools": school_count,
                "by_state": len(stats.get("by_state", [])),
                "by_program_type": len(stats.get("by_program_type", [])),
                "by_specialty": len(stats.get("by_specialty", [])),
            },
        )
    except Exception as e:
        return dg.AssetCheckResult(
            passed=False,
            description=f"Error checking dental_schools collection: {str(e)}",
        )


@dg.asset_check(asset="sdn_dental_schools_website")
def sdn_dental_schools_website_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("sdn_dental_schools")

    row_count = collection.count_documents({})

    # based on the number of schools in the SDN dental schools website
    if row_count != 86:
        return dg.AssetCheckResult(
            passed=False,
            metadata={"message": "SDN dental schools website check failed"},
        )

    return dg.AssetCheckResult(
        passed=True, metadata={"message": "SDN dental schools website check passed"}
    )
