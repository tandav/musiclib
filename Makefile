run:
	uvicorn piano_scales.server:app --host 0.0.0.0 --port 8001 --reload

run_with_midi:
	MIDI_DEVICE='IAC Driver Bus 1' uvicorn piano_scales.server:app --host 0.0.0.0 --port 8001 --reload

lint:
	python3 -m isort --force-single-line-imports piano_scales
	python3 -m isort --force-single-line-imports tests
	python3 -m flake8 --ignore E221,E501,W503,E701,E704,I100,I201 piano_scales
	python3 -m flake8 --ignore E221,E501,W503,E701,E704,I100,I201 tests

test:
	python3 -m pytest -v --cov=piano_scales tests

coverage_report:
	python3 -m pytest -v --cov=piano_scales --cov-report=html tests
	open htmlcov/index.html

clean_docker:
	docker rmi piano_scales

run_docker:
	git pull
	docker build -t piano_scales .
	docker run --rm -p 8001:8001 piano_scales
