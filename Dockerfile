FROM python:3.11

# Установка зависимостей
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода в контейнер
COPY . /app

CMD ["python", "main.py"]
