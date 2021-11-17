python = python3.9

stream:
	$(python) -m musictools.daw video

run:
	uvicorn server:app --host 0.0.0.0 --port 8001 --reload

run_with_midi:
	MIDI_DEVICE='IAC Driver Bus 1' uvicorn server:app --host 0.0.0.0 --port 8001 --reload

lint:
	$(python) -m no_init musictools tests
	$(python) -m force_absolute_imports musictools tests
	$(python) -m isort --force-single-line-imports musictools tests
	$(python) -m autoflake --recursive --in-place musictools tests
	$(python) -m autopep8 --in-place --recursive --aggressive --ignore=E221,E401,E402,E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictools/util/wavfile.py musictools tests
	$(python) -m unify --recursive --in-place musictools tests
	$(python) -m flake8 musictools tests

clean:
	rm -f logs/*

test:
	$(python) -m pytest -v --cov=musictools tests

test_video:
	# $(python) -m pytest -v -k test_main
	$(python) -m musictools.daw video_test

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

file:
	$(python) -m musictools.daw video_file 4

docker_stream:
	docker run --pull=always --rm -it -v $$PWD/credentials.py:/app/credentials.py tandav/musictools-stream

upload_creds_makefile:
	scp credentials.py Makefile cn2:~/musictools

messages:
	git log --pretty='%ad %h %s' --date=unix > static/messages.txt

build_push_streaming:
	make messages
	docker build -t tandav/musictools-stream -f ./Dockerfile-stream .
	docker push tandav/musictools-stream

#profile:
# 	$(python) -m cProfile -o logs/profile.txt -m musictools.daw video
#	$(python) -m gprof2dot -f pstats logs/profile.txt | dot -Tsvg -o logs/callgraph.svg
