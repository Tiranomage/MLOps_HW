if [[ -z "${VIRTUAL_ENV}" ]]; then
  echo "Error: Virtual environment is not activated. Please activate it first."
  exit 1
fi

# Укажите параметры
ENDPOINT_URL="http://localhost:9000"
ACCESS_KEY="minioadmin"
SECRET_KEY="minioadmin"
BUCKET_NAME="mlops-hw"
INPUT_S3_KEY="titanic.csv"
OUTPUT_S3_KEY="processed_titanic.csv"
LOCAL_INPUT_PATH="data/raw/titanic.csv"
LOCAL_OUTPUT_PATH="data/processed/titanic_processed.csv"

mkdir -p data/raw data/processed

python -m src.your_project_name.main_pipeline \
    --endpoint-url "$ENDPOINT_URL" \
    --access-key "$ACCESS_KEY" \
    --secret-key "$SECRET_KEY" \
    --bucket-name "$BUCKET_NAME" \
    --input-s3-key "$INPUT_S3_KEY" \
    --output-s3-key "$OUTPUT_S3_KEY" \
    --local-input-path "$LOCAL_INPUT_PATH" \
    --local-output-path "$LOCAL_OUTPUT_PATH"

if [ $? -eq 0 ]; then
    echo "Pipeline executed successfully!"
else
    echo "Pipeline failed!"
    exit 1
fi