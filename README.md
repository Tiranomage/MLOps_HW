# mlops_hw

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

MLOps homework

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         mlops and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── mlops   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes mlops a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

## Установка и настройка окружения (с использованием uv)

1.  Клонируйте репозиторий:
    ```bash
    git clone https://github.com/Tiranomage/MLOps_HW.git
    cd MLOps_HW
    ```

2.  Установите зависимости разработки с помощью `uv`:
    ```bash
    uv venv  
    source .venv/bin/activate
    uv pip install -e .[dev]
    ```

3.  Установите pre-commit хуки:
    ```bash
    pre-commit install
    ```

## Запуск пайплайна с S3 (MinIO)

1.  Убедитесь, что у вас установлен Docker и Docker Compose.
2.  Запустите MinIO в контейнере:
    ```bash
    ./scripts/start_minio.sh
    ```
3.  Создайте bucket (например, `mlops-hw`) в MinIO Console ([http://localhost:9001](http://localhost:9001), логин: `minioadmin`, пароль: `minioadmin`).
4.  Загрузите ваш датасет в созданный bucket через веб-интерфейс или `aws-cli`/`s3cmd`.
5.  Убедитесь, что виртуальное окружение активировано (см. раздел "Установка и настройка окружения").
6.  Запустите пайплайн:
    ```bash
    ./run_pipeline.sh
    ```
    Скрипт скачает файл из S3, выполнит обработку (см. `src/mlops/data_processor.py`) и загрузит результат обратно в S3 в тот же bucket.
7.  После завершения работы остановите MinIO:
    ```bash
    ./scripts/stop_minio.sh
    ```