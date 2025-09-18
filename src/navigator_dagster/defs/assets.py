import dagster as dg
from .resources import MongoDBResource


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


@dg.asset_check(asset="adea_caapid_programs_website")
def adea_caapid_programs_website_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("adea_caapid_programs")

    row_count = collection.count_documents({})

    if row_count == 0:
        return dg.AssetCheckResult(
            passed=False,
            metadata={"message": "ADEA PASS programs website check failed"},
        )

    return dg.AssetCheckResult(
        passed=True, metadata={"message": "ADEA PASS programs website check passed"}
    )
