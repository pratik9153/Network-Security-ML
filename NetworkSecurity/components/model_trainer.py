
import os
import sys

from NetworkSecurity.exception_handling.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging

from NetworkSecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)

from NetworkSecurity.entity.config_entity import ModelTrainerConfig

from NetworkSecurity.utils.main_utils.utils import (
    save_object,
    load_object,
    load_numpy_array_data,
    evaluate_models
)

from NetworkSecurity.utils.ML_Utils.metrics.classification_metrics import (
    get_classification_score
)

from NetworkSecurity.utils.ML_Utils.model.estimator import NetworkModel

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)


class ModelTrainer:

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, X_train, y_train, X_test, y_test):
        try:
            models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier()
            }

            params = {
                "Decision Tree": {
                    "criterion": ["gini", "entropy", "log_loss"]
                },

                "Random Forest": {
                    "n_estimators": [8, 16, 32, 128, 256]
                },

                "Gradient Boosting": {
                    "learning_rate": [0.1, 0.01, 0.05, 0.001],
                    "subsample": [0.6, 0.7, 0.75, 0.85, 0.9],
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                },

                "Logistic Regression": {},

                "AdaBoost": {
                    "learning_rate": [0.1, 0.01, 0.001],
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                }
            }

            # Evaluate models and select the best one
            model_report = evaluate_models(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=models,
                param=params
            )

            if not model_report:
                raise Exception("Model evaluation returned no results.")

            best_model_score = max(model_report.values())

            best_model_name = next(
                name
                for name, score in model_report.items()
                if score == best_model_score
            )

            best_model = models[best_model_name]

            logging.info(
                f"Best model: {best_model_name}, "
                f"Score: {best_model_score}"
            )

            # Calculate training metrics
            y_train_pred = best_model.predict(X_train)

            classification_train_metric = get_classification_score(
                y_true=y_train,
                y_pred=y_train_pred
            )

            # Calculate testing metrics
            y_test_pred = best_model.predict(X_test)

            classification_test_metric = get_classification_score(
                y_true=y_test,
                y_pred=y_test_pred
            )

            # Load the fitted preprocessing object
            preprocessor = load_object(
                file_path=(
                    self.data_transformation_artifact
                    .transformed_object_file_path
                )
            )

            # Create the directory for the trained model
            model_dir_path = os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            )

            os.makedirs(model_dir_path, exist_ok=True)

            # Combine the preprocessor and trained model
            network_model = NetworkModel(
                preprocessor=preprocessor,
                model=best_model
            )

            # Save the complete model object
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=network_model
            )

            # Create and return the model trainer artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=(
                    self.model_trainer_config.trained_model_file_path
                ),
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

            logging.info(
                f"Model training completed successfully: {model_trainer_artifact}"
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            # Get the transformed train and test file paths
            train_file_path = (
                self.data_transformation_artifact.transformed_train_file_path
            )

            test_file_path = (
                self.data_transformation_artifact.transformed_test_file_path
            )

            # Load the transformed NumPy arrays
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            # Separate features (X) and target (y)
            X_train = train_arr[:, :-1]
            y_train = train_arr[:, -1]

            X_test = test_arr[:, :-1]
            y_test = test_arr[:, -1]

            # Train models and receive the artifact
            model_trainer_artifact = self.train_model(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)