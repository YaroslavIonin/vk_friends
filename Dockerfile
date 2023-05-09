FROM python:3.10-slim

WORKDIR /code

EXPOSE 8000

COPY requirements.txt .

RUN python3 -m pip install --no-cache -r requirements.txt

COPY . .

RUN python api_friends/manage.py makemigrations

RUN python api_friends/manage.py migrate

CMD ["python", "api_friends/manage.py", "runserver", "0.0.0.0:8000"]