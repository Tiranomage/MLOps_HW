import argparse
import logging
import os
import tempfile
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from .s3_handler import S3Manager
from pathlib import Path
from typing import Any, Dict


logger = logging.getLogger(__name__)


def load_data_from_s3(s3_manager: S3Manager, bucket_name: str, s3_key: str) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        temp_path = tmp_file.name

    try:
        s3_manager.download_file(bucket_name, s3_key, Path(temp_path))
        df = pd.read_csv(temp_path)
        logger.info(f"Loaded data from s3://{bucket_name}/{s3_key}")
        return df
    finally:
        os.unlink(temp_path)


def train_and_log_model(
        config: Dict[str, Any], input_s3_path: str, s3_artifact_bucket: str
        ) -> None:
    logger.info(f"Starting training with config: {config}")

    s3_endpoint = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000")
    s3_access_key = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    s3_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    s3_manager = S3Manager(endpoint_url=s3_endpoint,
                           access_key=s3_access_key,
                           secret_key=s3_secret_key)

    bucket_name, s3_key = input_s3_path.split('/', 1)
    df = load_data_from_s3(s3_manager, bucket_name, s3_key)

    target_col = 'Survived'
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset.")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    mask = y.notna()
    X = X[mask]
    y = y[mask]

    X = X.select_dtypes(include=['number'])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.get('random_state', 42)
    )

    model = RandomForestClassifier(
        n_estimators=config.get('n_estimators', 100),
        max_depth=config.get('max_depth', 10),
        max_features=config.get('max_features', 'sqrt'),
        random_state=config.get('random_state', 42)
    )

    experiment_name = config.get('experiment_name', 'DefaultExperiment')
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name=config.get('run_name', 'training_run')):
        for key, value in config.items():
            if key not in ['experiment_name', 'run_name']:
                mlflow.log_param(key, value)

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        mlflow.sklearn.log_model(
            sk_model=model, artifact_path="model", conda_env="./environment.yml"
        )

        model_s3_key = f"{experiment_name}/{mlflow.active_run().info.run_id}/model.pkl"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_model_file:
            import pickle
            pickle.dump(model, tmp_model_file)
            tmp_model_path = Path(tmp_model_file.name)

        try:
            s3_manager.upload_file(tmp_model_path, s3_artifact_bucket, model_s3_key)
            logger.info(f"Model saved to S3: s3://{s3_artifact_bucket}/{model_s3_key}")
        finally:
            os.unlink(tmp_model_path)

        logger.info("Training completed and logged to MLflow.")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Train an ML model and log to MLflow.")
    parser.add_argument(
        "--config-file", type=str, required=True,
        help="Path to the config JSON file."
    )
    parser.add_argument(
        "--input-s3-path", type=str, required=True,
        help="S3 path to the input dataset (format: bucket/key)."
    )
    parser.add_argument(
        "--artifact-bucket", type=str, default="mlflow-artifacts",
        help="S3 bucket name for artifacts/models."
    )

    args = parser.parse_args()

    import json
    with open(args.config_file, 'r') as f:
        config = json.load(f)

    mlflow.set_tracking_uri("http://localhost:5000")

    train_and_log_model(config, args.input_s3_path, args.artifact_bucket)
