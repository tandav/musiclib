python = python3.9

run:
	uvicorn server:app --host 0.0.0.0 --port 8001 --reload

run_with_midi:
	MIDI_DEVICE='IAC Driver Bus 1' uvicorn server:app --host 0.0.0.0 --port 8001 --reload

lint:
	$(python) -m isort --force-single-line-imports musictools tests
	$(python) -m autoflake --recursive --in-place musictools tests
	$(python) -m autopep8 --verbose --in-place --recursive --aggressive --ignore=E221,E401,E402,E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictools/util/wavfile.py musictools tests
	$(python) -m unify --recursive --in-place musictools
	$(python) -m flake8 musictools tests

clean:
	rm -f logs/*

test:
	rm -f logs/*
	$(python) -m pytest -v --cov=musictools tests

coverage_report:
	$(python) -m pytest -v --cov=musictools --cov-report=html tests
	open htmlcov/index.html

clean_docker:
	docker rmi musictools

run_docker:
	docker build -t musictools .
	docker run --name musictools -d --rm -p 8001:8001 musictools

daw:
	$(python) -m musictools.daw

stream:
	$(python) -m musictools.daw video

run_streaming:
	docker run --rm -it tandav/musictools-stream

build_push_streaming:
	docker build -t tandav/musictools-stream -f ./Dockerfile-stream .
	#docker build --no-cache -t tandav/musictools-stream -f ./Dockerfile-stream .
	docker push tandav/musictools-stream
