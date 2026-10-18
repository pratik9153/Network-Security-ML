
import os
import sys
import certifi
import pymongo
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from uvicorn import run as app_run

from NetworkSecurity.utils.ML_Utils.model.estimator import NetworkModel
from NetworkSecurity.exception_handling.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.pipeline.training_pipeline import TrainingPipeline
from NetworkSecurity.utils.main_utils.utils import load_object
from NetworkSecurity.constant.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)




# Load environment variables
load_dotenv()

mongo_db_url = os.getenv("MONGO_DB_URL")

if not mongo_db_url:
    raise ValueError("MONGO_DB_URL is not set in the .env file")


# MongoDB connection
ca = certifi.where()
client = pymongo.MongoClient(
    mongo_db_url,
    tlsCAFile=ca,
    serverSelectionTimeoutMS=5000,
)

database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]


# FastAPI application
app = FastAPI(title="NetworkSecurity API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="./templates")


# Home route
@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


# Training route
@app.get("/train")
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()

        return {"message": "Training was successful"}

    except Exception as e:
        logging.exception("Training failed")
        raise NetworkSecurityException(e, sys) from e


# Prediction route
@app.post("/predict")
async def predict_route(
    request: Request,
    file: UploadFile = File(...),
):
    try:
        # Validate uploaded file
        if not file.filename or not file.filename.lower().endswith(".csv"):
            return Response(
                content="Please upload a valid CSV file.",
                status_code=400,
                media_type="text/plain",
            )

        # Read uploaded CSV
        df = pd.read_csv(file.file)

        if df.empty:
            return Response(
                content="The uploaded CSV file is empty.",
                status_code=400,
                media_type="text/plain",
            )

        # Load trained preprocessing object and model
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")

        # Create prediction model
        network_model = NetworkModel(
            preprocessor=preprocessor,
            model=final_model,
        )

        # Generate predictions
        y_pred = network_model.predict(df)

        # Add predictions to the original DataFrame
        df["predicted_column"] = y_pred

        # Create output directory if it does not exist
        os.makedirs("prediction_output", exist_ok=True)

        # Save predictions
        output_path = os.path.join(
            "prediction_output",
            "output.csv",
        )
        df.to_csv(output_path, index=False)

        # Convert DataFrame into HTML table
        table_html = df.to_html(
            index=False,
            classes="table table-striped",
            border=0,
        )

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={"table": table_html},
        )

    except Exception as e:
        logging.exception("Prediction failed")
        raise NetworkSecurityException(e, sys) from e

    finally:
        await file.close()


# Run application
if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)
