import dagster as dg
from ..defs.resources import MongoDBResource
from ..defs.utils import scrape_adea_programs


class ETL(dg.Model):
    url: str
    name: str
    collection_name: str


class AdeaWebsite(dg.Component, dg.Model, dg.Resolvable):
    steps: list[ETL]

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        assets = []

        for etl in self.steps:

            @dg.asset(
                name=etl.name,
            )
            def _collection(mongodb: MongoDBResource):
                programs = scrape_adea_programs(etl.url)

                if not programs:
                    return {
                        "status": "error",
                        "message": "No programs scraped",
                        "count": 0,
                    }

                # Get the MongoDB collection
                collection = mongodb.get_collection(etl.collection_name)

                result = collection.insert_many(programs)

                return {
                    "status": "success",
                    "message": f"Successfully scraped and stored {len(programs)} programs",
                    "count": len(programs),
                    "inserted_ids": len(result.inserted_ids),
                }

            assets.append(_collection)

        return dg.Definitions(
            assets=assets,
        )
