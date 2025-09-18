import dagster as dg
from .resources import MongoDBResource
from .utils import scrape_adea_programs


@dg.asset
def adea_pass_programs_website(mongodb: MongoDBResource) -> dict:
    """Scrape ADEA PASS programs and store them in MongoDB."""
    # Scrape the programs data
    programs = scrape_adea_programs()

    if not programs:
        return {"status": "error", "message": "No programs scraped", "count": 0}

    # Get the MongoDB collection
    collection = mongodb.get_collection("adea_pass_programs")

    # Insert the new programs data
    result = collection.insert_many(programs)

    return {
        "status": "success",
        "message": f"Successfully scraped and stored {len(programs)} programs",
        "count": len(programs),
        "inserted_ids": len(result.inserted_ids),
    }


@dg.asset_check(asset="adea_pass_programs_website")
def adea_pass_programs_website_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("adea_pass_programs")

    row_count = collection.count_documents({})

    if row_count == 0:
        return dg.AssetCheckResult(
            passed=False,
            metadata={"message": "ADEA PASS programs website check failed"},
        )

    return dg.AssetCheckResult(
        passed=True, metadata={"message": "ADEA PASS programs website check passed"}
    )
