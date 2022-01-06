FROM python:3.10-alpine

RUN pip install fastapi uvicorn aiofiles tqdm mido pipe21

EXPOSE 8001

RUN mkdir -p /app/musictool
RUN mkdir -p /app/static
COPY musictool /app/musictool
COPY static /app/static
COPY server.py /app/
WORKDIR /app
# CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--ssl-certfile", "fullchain.pem", "--ssl-keyfile", "privkey.pem"]
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
