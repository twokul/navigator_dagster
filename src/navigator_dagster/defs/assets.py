import dagster as dg
from .resources import MongoDBResource
from .mongo_utils import create_dental_programs_collection


@dg.asset(
    deps=["adea_pass_programs_website", "adea_caapid_programs_website"],
    description="Merged dental programs collection from ADEA PASS and CAAPID programs",
)
def dental_programs(mongodb: MongoDBResource):
    return create_dental_programs_collection(mongodb)


@dg.asset_check(asset="dental_programs")
def dental_programs_check(mongodb: MongoDBResource) -> dg.AssetCheckResult:
    collection = mongodb.get_collection("dental_programs")
    adea_pass_collection = mongodb.get_collection("adea_pass_programs")
    adea_caapid_collection = mongodb.get_collection("adea_caapid_programs")

    adea_pass_row_count = adea_pass_collection.count_documents({})
    adea_caapid_row_count = adea_caapid_collection.count_documents({})
    row_count = collection.count_documents({})
    sum_row_count = adea_pass_row_count + adea_caapid_row_count

    if row_count == 0 or row_count != sum_row_count:
        return dg.AssetCheckResult(
            passed=False,
            metadata={"message": "Dental programs check failed"},
        )

    return dg.AssetCheckResult(
        passed=True, metadata={"message": "Dental programs check passed"}
    )


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
