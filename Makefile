dev:
	uvicorn piano_scales.server:app --host 0.0.0.0 --port 8001 --reload

clean:
	docker rmi piano_scales

run:
	git pull
	docker build -t piano_scales .
	docker run --rm -p 8001:8001 piano_scales

lint:
	python3 -m isort --force-single-line-imports piano_scales
	python3 -m flake8 --ignore E203,E221,E251,E501,E701,E704 piano_scales

test:
	python3 -m pytest tests
