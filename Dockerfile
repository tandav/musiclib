FROM python:3

RUN pip install fastapi uvicorn aiofiles Pillow tqdm

EXPOSE 8001

COPY ./piano_scales /piano_scales
COPY *.pem /certs/
WORKDIR /piano_scales
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--ssl-certfile", "/certs/fullchain.pem", "--ssl-keyfile", "/certs/privkey.pem"]
