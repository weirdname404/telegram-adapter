FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]
