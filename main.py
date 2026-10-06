from NetworkSecurity.components.data_ingestion import DataIngestion 
from NetworkSecurity.components.data_validation import DataValidation
from NetworkSecurity.exception_handling.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.entity.config_entity import( DataIngestionConfig , TrainingPipelineConfig)
from NetworkSecurity.entity.config_entity import DataValidationConfig 
import sys


if __name__ == '__main__':

    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        data_ingestion=DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestionj")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        print(dataingestionconfig)
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Initiate the data Validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("data Validation Completed")
        print(data_validation_artifact)
        
    except Exception as e:
        raise NetworkSecurityException(e, sys)

