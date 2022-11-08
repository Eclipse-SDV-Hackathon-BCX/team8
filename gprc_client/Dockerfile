FROM python:3.10-slim-bullseye

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

COPY . .
RUN pip install -r requirements.txt

CMD [ "python", "./grpc_client.py" ]
