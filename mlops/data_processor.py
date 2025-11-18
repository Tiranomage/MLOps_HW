import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def process_data(input_path: Path, output_path: Path) -> None:
    logger.info(f"Processing data from {input_path} to {output_path}")
    df = pd.read_csv(input_path)

    if 'Age' in df.columns:
        mean_age = df['Age'].mean()
        df['Age_normalized'] = (df['Age'] - mean_age) / df['Age'].std()

    df.to_csv(output_path, index=False)
    logger.info(f"Processed data saved to {output_path}")
