import dagster as dg
from ..defs.resources import MongoDBResource
from ..defs.utils import scrape_adea_programs
from ..defs.mongo_utils import upsert_adea_programs


class ETL(dg.Model):
    url: str
    name: str
    collection_name: str
    description: str


class AdeaWebsite(dg.Component, dg.Model, dg.Resolvable):
    steps: list[ETL]

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        assets = []

        for etl in self.steps:
            # Create a factory function to avoid closure issues
            def create_asset(etl_step):
                @dg.asset(
                    name=etl_step.name,
                    description=etl_step.description,
                )
                def _collection(mongodb: MongoDBResource):
                    programs = scrape_adea_programs(etl_step.url)

                    if not programs:
                        return {
                            "status": "error",
                            "message": "No programs scraped",
                            "count": 0,
                        }

                    # Use upsert to avoid duplicates based on name, type, and state
                    result = upsert_adea_programs(
                        mongodb, programs, etl_step.collection_name
                    )

                    return {
                        "status": result["status"],
                        "message": result["message"],
                        "total_processed": result["total_processed"],
                        "inserted": result["inserted"],
                        "updated": result["updated"],
                        "skipped": result["skipped"],
                        "collection_name": result["collection_name"],
                    }

                return _collection

            assets.append(create_asset(etl))

        return dg.Definitions(
            assets=assets,
        )
