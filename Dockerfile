FROM python:3-alpine

RUN pip install fastapi uvicorn aiofiles tqdm

EXPOSE 8001

RUN mkdir -p /app/piano_scales
RUN mkdir -p /app/static
COPY piano_scales /app/piano_scales
COPY static /app/static
COPY server.py /app/
WORKDIR /app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--ssl-certfile", "fullchain.pem", "--ssl-keyfile", "privkey.pem"]
