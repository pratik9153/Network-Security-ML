
import os
import sys

import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from NetworkSecurity.exception_handling.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.entity.config_entity import DataIngestionConfig
from NetworkSecurity.entity.artifact_entity import DataIngestionArtifact


load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class DataIngestion:

    def __init__(self, data_ingestion: DataIngestionConfig):
        try:
            self.data_ingestion = data_ingestion

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        try:
            if not MONGO_DB_URL:
                raise ValueError(
                    "MONGO_DB_URL is missing. Please configure it in your .env file."
                )

            database_name = self.data_ingestion.database_name
            collection_name = self.data_ingestion.collection_name

            with pymongo.MongoClient(
                MONGO_DB_URL,
                serverSelectionTimeoutMS=10000,
            ) as mongo_client:

                # Verify that MongoDB is reachable.
                mongo_client.admin.command("ping")

                collection = mongo_client[database_name][collection_name]
                dataframe = pd.DataFrame(list(collection.find({})))

            if "_id" in dataframe.columns:
                dataframe.drop(columns=["_id"], inplace=True)

            dataframe.replace({"na": np.nan}, inplace=True)

            logging.info(
                f"Loaded {len(dataframe)} records from MongoDB collection "
                f"'{collection_name}'."
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_data_into_feature_store(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        try:
            feature_store_file_path = (
                self.data_ingestion.feature_store_file_path
            )

            directory_path = os.path.dirname(feature_store_file_path)

            if directory_path:
                os.makedirs(directory_path, exist_ok=True)

            dataframe.to_csv(
                feature_store_file_path,
                index=False,
                header=True,
            )

            logging.info(
                f"Feature store data saved at: {feature_store_file_path}"
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def split_data_as_train_test(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        try:
            if len(dataframe) < 2:
                raise ValueError(
                    "At least two records are required for train-test splitting."
                )

            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion.train_test_split_ratio,
                random_state=42,
            )

            training_file_path = self.data_ingestion.training_file_path
            testing_file_path = self.data_ingestion.testing_file_path

            for file_path in (training_file_path, testing_file_path):
                directory_path = os.path.dirname(file_path)

                if directory_path:
                    os.makedirs(directory_path, exist_ok=True)

            train_set.to_csv(
                training_file_path,
                index=False,
                header=True,
            )

            test_set.to_csv(
                testing_file_path,
                index=False,
                header=True,
            )

            logging.info(
                f"Training data saved at: {training_file_path}"
            )
            logging.info(
                f"Testing data saved at: {testing_file_path}"
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info("Initiating data ingestion")

            dataframe = self.export_collection_as_dataframe()

            if dataframe.empty:
                raise ValueError(
                    "MongoDB returned no records. Check the database "
                    "name, collection name, and source data."
                )

            dataframe = self.export_data_into_feature_store(dataframe)

            self.split_data_as_train_test(dataframe)

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion.training_file_path,
                test_file_path=self.data_ingestion.testing_file_path,
            )

            logging.info(
                f"Data ingestion completed: {data_ingestion_artifact}"
            )

            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
