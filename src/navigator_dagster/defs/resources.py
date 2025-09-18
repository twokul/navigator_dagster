import dagster as dg
from pymongo import MongoClient
import os
from pydantic import Field


class MongoDBResource(dg.ConfigurableResource):
    """MongoDB resource for connecting to MongoDB databases."""

    connection_string: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection string from environment variable",
    )
    database_name: str = Field(
        default="navigator_db", description="Name of the MongoDB database to connect to"
    )
    collection_name: str = Field(
        default="documents", description="Name of the default MongoDB collection to use"
    )

    def create_resource(self, context: dg.InitResourceContext) -> "MongoDBResource":
        """Create and return the MongoDB resource."""
        # Test the connection
        try:
            client = MongoClient(self.connection_string)
            client.admin.command("ping")
            context.log.info(
                f"Successfully connected to MongoDB database: {self.database_name}"
            )
            client.close()
        except Exception as e:
            context.log.error(f"Failed to connect to MongoDB: {e}")
            raise

        return self

    def teardown_for_execution(self, context: dg.InitResourceContext) -> None:
        context.log.info("MongoDB resource teardown completed.")

    def get_client(self) -> MongoClient:
        """Get a MongoDB client."""
        return MongoClient(self.connection_string)

    def get_database(self):
        """Get the configured database from the client."""
        client = self.get_client()
        return client[self.database_name]

    def get_collection(self, collection_name: str):
        """Get the default collection from the configured database."""
        client = self.get_client()
        db = client[self.database_name]
        return db[collection_name]


def resources() -> dict:
    """Return the resources configuration."""
    return {
        "mongodb": MongoDBResource(
            connection_string=os.getenv(
                "MONGODB_CONNECTION_STRING", "mongodb://localhost:27017"
            ),
            database_name=os.getenv("MONGO_DB_NAME", "navigator_db"),
            collection_name=os.getenv("MONGO_DB_COLLECTION", "documents"),
        )
    }
