import argparse
from pathlib import Path
import logging
from .s3_handler import S3Manager
from .data_processor import process_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline: Download from S3 -> Process -> Upload to S3"
    )
    parser.add_argument(
        "--endpoint-url", required=True,
        help="S3 Endpoint URL (e.g., http://localhost:9000)"
    )
    parser.add_argument(
        "--access-key", required=True,
        help="S3 Access Key"
    )
    parser.add_argument(
        "--secret-key", required=True,
        help="S3 Secret Key"
    )
    parser.add_argument(
        "--bucket-name", required=True,
        help="S3 Bucket Name"
    )
    parser.add_argument(
        "--input-s3-key", required=True,
        help="S3 Key for input file"
    )
    parser.add_argument(
        "--output-s3-key", required=True,
        help="S3 Key for output file"
    )
    parser.add_argument(
        "--local-input-path", type=Path, required=True,
        help="Local path to save input file"
    )
    parser.add_argument(
        "--local-output-path", type=Path, required=True,
        help="Local path to save processed file"
    )

    args = parser.parse_args()

    logger.info("Starting pipeline...")

    s3 = S3Manager(
        endpoint_url=args.endpoint_url,
        access_key=args.access_key,
        secret_key=args.secret_key
    )

    s3.download_file(args.bucket_name, args.input_s3_key, args.local_input_path)

    process_data(args.local_input_path, args.local_output_path)

    s3.upload_file(args.local_output_path, args.bucket_name, args.output_s3_key)

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
