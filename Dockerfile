FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN python3 --version
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR .
COPY . .