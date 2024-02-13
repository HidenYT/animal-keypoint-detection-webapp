FROM python:3.9.0-slim as python-base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get install ffmpeg libsm6 libxext6 -y

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]