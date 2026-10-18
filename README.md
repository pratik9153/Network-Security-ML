# NetworkSecurity: Phishing Detection ML Pipeline

An end-to-end machine learning project that classifies phishing-related records using website and URL features. The project includes a modular training pipeline and a FastAPI application for generating predictions from uploaded CSV files.

<img width="1840" height="1032" alt="Screenshot 2026-10-18 175720" src="https://github.com/user-attachments/assets/f3e00e7b-8675-4f5d-8f32-37a326fe8900" />

<img width="1797" height="896" alt="Screenshot 2026-10-18 160525" src="https://github.com/user-attachments/assets/e2d2cd12-1f24-4911-99da-c711d56b732a" />


## Overview

The pipeline is organized into independent stages:

1. **Data ingestion** — reads labelled data from MongoDB and creates training and testing datasets.
2. **Data validation** — checks the dataset against a YAML schema and generates a data-drift report.
3. **Data transformation** — handles missing values and prepares features for model training.
4. **Model training** — trains and evaluates classification models.
5. **Model persistence** — saves the trained model and preprocessing object.
6. **Prediction API** — accepts a CSV upload through FastAPI and runs inference.
7. **Prediction output** — adds a `predicted_column` to the input data and returns the result according to the API response configured in `app.py`.

## Technology Stack

- **Language:** Python
- **Data processing:** Pandas, NumPy
- **Machine learning:** scikit-learn
- **Database:** MongoDB, PyMongo
- **Schema/configuration:** YAML
- **API:** FastAPI, Uvicorn
- **HTML results:** Jinja2, HTML, CSS
- **Model persistence:** Pickle
- **Experiment tracking:** MLflow integration
- **Containerization:** Docker
- **Cloud infrastructure:** AWS S3, Amazon ECR, Amazon EC2
- **Automation:** GitHub Actions
- **Version control:** Git, GitHub

> The repository contains deployment configuration for Docker and AWS. A configured workflow does not, by itself, prove that a cloud deployment is live.

## Architecture

```text
MongoDB
   |
   v
Data Ingestion
   |
   v
Data Validation ----> Schema checks / Drift report
   |
   v
Data Transformation
   |
   v
Model Training and Evaluation
   |
   v
Saved Model + Preprocessor
   |
   v
FastAPI /predict
   |
   v
Upload CSV -> Preprocess -> Predict
   |
   v
Predicted output CSV or HTML response
```

## Project Structure

```text
END-TO-END-NETWORK/
├── app.py
├── main.py
├── push_data.py
├── test_mongodb.py
├── networksecurity/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   ├── constant/
│   │   └── training_pipeline/
│   ├── entity/
│   │   ├── config_entity.py
│   │   └── artifact_entity.py
│   ├── pipeline/
│   │   ├── training_pipeline.py
│   │   └── batch_prediction.py
│   ├── utils/
│   │   ├── main_utils/
│   │   └── ml_utils/
│   │       ├── metric/
│   │       └── model/
│   │           └── estimator.py
│   ├── cloud/
│   │   └── s3_syncer.py
│   ├── exception/
│   │   └── exception.py
│   └── logging/
│       └── logger.py
├── data_schema/
│   └── schema.yaml
├── Network_Data/
│   └── phisingData.csv
├── final_model/
│   ├── model.pkl
│   └── preprocessor.pkl
├── templates/
│   └── table.html
├── Artifacts/
├── prediction_output/
├── logs/
├── requirements.txt
├── setup.py
├── Dockerfile
├── .dockerignore
├── .gitignore
└── .github/
    └── workflows/
        └── main.yml
```

Generated folders such as `Artifacts/`, `logs/`, and `prediction_output/` may be created or updated while running the application.

## Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd END-TO-END-NETWORK
```

Replace `<YOUR_REPOSITORY_URL>` with your repository URL.

### 2. Create and activate a virtual environment

```bash
python -m venv venvN
```

Windows Command Prompt:

```bat
venvN\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install python-multipart
```

`python-multipart` is required by FastAPI for file uploads. If it is not already in `requirements.txt`, add it there.

### 4. Configure environment variables

Create a local `.env` file and set the MongoDB connection variable expected by your source code. Use one consistent variable name throughout the project.

Example:

```env
MONGO_DB_URL=your_mongodb_connection_string
```

The exact variable name must match the `os.getenv(...)` call in your current code. Do not commit `.env` or real credentials to GitHub.

### 5. Start the API

```bash
uvicorn app:app --reload
```

Open the interactive API documentation:

**http://127.0.0.1:8000/docs**

## Generate Predictions

1. Open `/docs`.
2. Expand `POST /predict`.
3. Click **Try it out** and upload a CSV file.
4. Click **Execute**.
5. The application preprocesses the uploaded data and runs the trained model.
6. The prediction is added as `predicted_column`.

The endpoint's response depends on the current `app.py` implementation: it can return a downloadable CSV using `FileResponse` or an HTML table using the Jinja2 template. If CSV download is intended, ensure the endpoint returns the generated file with `media_type="text/csv"` and a download filename.

The input CSV must contain the feature columns expected by the saved preprocessor. Confirm whether the target column `Result` should be omitted from prediction input based on the training and inference implementation.

## Train the Model

Use the `/train` route or the project's supported training-pipeline entry point. Training requires a working MongoDB connection, access to the configured collection, and a valid schema. Review the logs and generated artifacts to confirm that each stage completed successfully.

## Deployment

The repository includes configuration for Docker and an AWS/GitHub Actions workflow.

Typical deployment components:

- **Docker** packages the API and its dependencies.
- **Amazon ECR** stores the built container image.
- **Amazon EC2** runs the container.
- **Amazon S3** can store or synchronize model and pipeline artifacts.
- **GitHub Actions** can automate checks, image builds and deployment steps.

Before deployment, verify that the Docker image includes the required model and preprocessor files, templates, and dependencies. Configure environment variables securely, restrict inbound network access, and test `/docs` and `/predict` on the deployed service. Do not claim the service is publicly deployed until the endpoint has been tested.

## Security Notes

- Never commit `.env` files, database connection strings, cloud credentials or other secrets.
- Do not include virtual environments or unnecessary large datasets in the repository.
- Only load pickle artifacts from trusted sources.
- Restrict CORS origins and protect training endpoints before exposing the API publicly.
- Avoid returning internal stack traces or secret values to API clients.

## Current Project Status

The local FastAPI prediction endpoint has returned `200 OK` during testing. Evaluate the model on a held-out dataset and report measured metrics before making performance claims. Docker/AWS configuration should be tested separately before describing cloud deployment as complete.




