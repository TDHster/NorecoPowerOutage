FROM python:3.11-slim

# for healthcheck via pgrep need procps
RUN apt-get update && apt-get install -y --no-install-recommends procps \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# For effective caching dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (except.dockerignore)
COPY . .

CMD ["python", "main.py"]
