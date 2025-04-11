# Use Python 3.12.2 image based on Debian Bullseye in its slim variant as the base image
FROM python:3.12.2-slim-bullseye

ENV PYTHONBUFFERED=1
ENV PORT=8000

WORKDIR /app
COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run with Uvicorn instead of Gunicorn
CMD uvicorn escapeGame.asgi:application --host 0.0.0.0 --port ${PORT}

EXPOSE ${PORT}
