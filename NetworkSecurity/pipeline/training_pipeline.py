
import sys

from NetworkSecurity.exception_handling.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging

from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.components.data_validation import DataValidation
from NetworkSecurity.components.data_transformation import DataTransformation
from NetworkSecurity.components.model_trainer import ModelTrainer

from NetworkSecurity.constant.training_pipeline import (
    TRAINING_BUCKET_NAME,
    SAVED_MODEL_DIR,
)

from NetworkSecurity.cloud.s3Sync import S3Sync

from NetworkSecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from NetworkSecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)


class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync()

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info("Starting data ingestion")

            data_ingestion_config = DataIngestionConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            data_ingestion = DataIngestion(
                data_ingestion=data_ingestion_config
            )

            data_ingestion_artifact = (
                data_ingestion.initiate_data_ingestion()
            )

            logging.info(
                f"Data ingestion completed: {data_ingestion_artifact}"
            )
            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def start_data_validation(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
    ) -> DataValidationArtifact:
        try:
            logging.info("Starting data validation")

            data_validation_config = DataValidationConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config,
            )

            data_validation_artifact = (
                data_validation.initiate_data_validation()
            )

            logging.info(
                f"Data validation completed: {data_validation_artifact}"
            )
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def start_data_transformation(
        self,
        data_validation_artifact: DataValidationArtifact,
    ) -> DataTransformationArtifact:
        try:
            logging.info("Starting data transformation")

            data_transformation_config = DataTransformationConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            data_transformation = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                data_transformation_config=data_transformation_config,
            )

            data_transformation_artifact = (
                data_transformation.initiate_data_transformation()
            )

            logging.info(
                "Data transformation completed: "
                f"{data_transformation_artifact}"
            )
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def start_model_trainer(
        self,
        data_transformation_artifact: DataTransformationArtifact,
    ) -> ModelTrainerArtifact:
        try:
            logging.info("Starting model training")

            model_trainer_config = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            model_trainer = ModelTrainer(
                data_transformation_artifact=data_transformation_artifact,
                model_trainer_config=model_trainer_config,
            )

            model_trainer_artifact = (
                model_trainer.initiate_model_trainer()
            )

            logging.info(
                f"Model training completed: {model_trainer_artifact}"
            )
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = (
                f"s3://{TRAINING_BUCKET_NAME}/artifact/"
                f"{self.training_pipeline_config.timestamp}"
            )

            logging.info(
                f"Syncing artifacts to S3: {aws_bucket_url}"
            )

            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.artifact_dir,
                aws_bucket_url=aws_bucket_url,
            )

            logging.info("Artifact directory synced to S3 successfully")

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = (
                f"s3://{TRAINING_BUCKET_NAME}/final_model/"
                f"{self.training_pipeline_config.timestamp}"
            )

            logging.info(
                f"Syncing saved model to S3: {aws_bucket_url}"
            )

            self.s3_sync.sync_folder_to_s3(
                folder=SAVED_MODEL_DIR,
                aws_bucket_url=aws_bucket_url,
            )

            logging.info(
                "Saved model directory synced to S3 successfully"
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def run_pipeline(self) -> ModelTrainerArtifact:
        try:
            logging.info(
                "Starting the NetworkSecurity training pipeline"
            )

            data_ingestion_artifact = self.start_data_ingestion()

            data_validation_artifact = self.start_data_validation(
                data_ingestion_artifact=data_ingestion_artifact
            )

            data_transformation_artifact = (
                self.start_data_transformation(
                    data_validation_artifact=data_validation_artifact
                )
            )

            model_trainer_artifact = self.start_model_trainer(
                data_transformation_artifact=data_transformation_artifact
            )

            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()

            logging.info(
                "NetworkSecurity training pipeline completed successfully"
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
