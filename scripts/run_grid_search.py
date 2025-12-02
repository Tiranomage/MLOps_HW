import argparse
import json
import subprocess
import itertools
import logging
import os
import tempfile
from typing import Any, Dict, List


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_configs(
        base_config_path: str, grid_params: Dict[str, List[Any]]
        ) -> List[Dict[str, Any]]:
    with open(base_config_path, 'r') as f:
        base_config: Dict[str, Any] = json.load(f)

    keys, values = zip(*grid_params.items())
    combinations = itertools.product(*values)

    configs: List[Dict[str, Any]] = []
    for combo in combinations:
        config = base_config.copy()
        config.update(dict(zip(keys, combo)))
        run_name_parts = [f"{k}={v}" for k, v in zip(keys, combo)]
        config['run_name'] = f"grid_search_{'_'.join(run_name_parts)}"
        configs.append(config)

    return configs


def run_training(
        config: Dict[str, Any], script_path: str, input_s3_path: str, artifact_bucket: str
        ) -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_config_file:
        json.dump(config, temp_config_file)
        temp_config_path = temp_config_file.name

    try:
        cmd = [
            "python", script_path,
            "--config-file", temp_config_path,
            "--input-s3-path", input_s3_path,
            "--artifact-bucket", artifact_bucket
        ]
        logger.info(f"Running training: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Training completed for config {config['run_name']}. Stdout: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Training failed for config {config['run_name']}. Stderr: {e.stderr}")
        raise
    finally:
        os.unlink(temp_config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run grid search for ML model training.")
    parser.add_argument(
        "--base-config-file", type=str, required=True,
        help="Path to the base config JSON file."
    )
    parser.add_argument(
        "--input-s3-path", type=str, required=True,
        help="S3 path to the input dataset (format: bucket/key)."
    )
    parser.add_argument(
        "--artifact-bucket", type=str, default="mlflow-artifacts",
        help="S3 bucket name for artifacts/models."
    )
    parser.add_argument(
        "--train-script", type=str, default="../src/mlops/train_model.py",
        help="Path to the training script."
    )

    args = parser.parse_args()

    grid_params: Dict[str, List[Any]] = {
        "n_estimators": [50, 100],
        "max_depth": [5, 10, None],
        "max_features": ["sqrt", "log2"]
    }

    configs = generate_configs(args.base_config_file, grid_params)
    logger.info(f"Generated {len(configs)} configurations for grid search.")

    for config in configs:
        run_training(config, args.train_script, args.input_s3_path, args.artifact_bucket)
