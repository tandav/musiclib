FROM python:3

RUN pip install fastapi uvicorn aiofiles Pillow tqdm

EXPOSE 8001

RUN mkdir -p /app/piano_scales
COPY piano_scales /app/piano_scales
WORKDIR /app
CMD ["uvicorn", "piano_scales.server:app", "--host", "0.0.0.0", "--port", "8001"]
