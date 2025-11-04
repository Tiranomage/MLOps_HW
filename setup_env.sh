set -e # Выход при ошибке

VENV_NAME="venv"

echo "Создание виртуального окружения..."
python -m venv $VENV_NAME

echo "Активация виртуального окружения..."
source $VENV_NAME/bin/activate

echo "Установка зависимостей разработки..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Установка pre-commit хуков..."
pre-commit install

echo "Окружение настроено! Не забудьте активировать его: source $VENV_NAME/bin/activate"