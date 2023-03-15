# FROM python:3.8.12-slim
# FROM ultralytics/ultralytics
FROM ultralytics/ultralytics:latest-cpu

ENV PORT=5000
EXPOSE 5000

# --- start to install backend-end stuff
RUN mkdir -p /app
WORKDIR /app

# --- Install Python requirements.
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements-docker.txt ./
RUN pip install --no-cache-dir -r requirements-docker.txt

# --- Copy project files
COPY ["API_client_server.py", "./"]
COPY ["api_internals/*.py", "./api_internals/"]
COPY ["models/*", "./models/"]

# --- Start server
# ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:$PORT", "API_client_server:app"]
CMD gunicorn API_client_server:app --bind 0.0.0.0:$PORT --timeout=60 --threads=2
