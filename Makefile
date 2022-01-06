python = python3.10

.PHONY: stream
stream:
	$(python) -m musictool.daw video

.PHONY: run
run:
	$(python) -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

.PHONY: run_with_midi
run_with_midi:
	MIDI_DEVICE='IAC Driver Bus 1' uvicorn server:app --host 0.0.0.0 --port 8001 --reload

#[flake8]
#ignore = E221,E501,W503,E701,E704,E741,I100,I201,W504
#exclude = musictool/util/wavfile.py

.PHONY: lint
lint:
	$(python) -m no_init musictool tests
	$(python) -m force_absolute_imports musictool tests
	$(python) -m isort --force-single-line-imports musictool tests
	$(python) -m autoflake --recursive --in-place musictool tests
	$(python) -m autopep8 --in-place --recursive --aggressive --ignore=E221,E401,E402,E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictool/util/wavfile.py musictool tests
	$(python) -m unify --recursive --in-place musictool tests
	$(python) -m flake8 --ignore=E221,E501,W503,E701,E704,E741,I100,I201,W504 --exclude=musictool/util/wavfile.py musictool tests

.PHONY: clean
clean:
	rm -f logs/*

.PHONY: test
test:
	$(python) -m pytest -v --cov=musictool tests

.PHONY: test_video
test_video:
	# $(python) -m pytest -v -k test_main
	$(python) -m musictool.daw video_test

.PHONY: coverage_report
coverage_report:
	$(python) -m pytest -v --cov=musictool --cov-report=html tests
	open htmlcov/index.html

.PHONY: clean_docker
clean_docker:
	docker rmi musictool

.PHONY: run_docker
run_docker:
	docker build -t musictool .
	docker run --name musictool -d --rm -p 8001:8001 musictool

.PHONY: daw
daw:
	$(python) -m musictool.daw

.PHONY:  file
file:
	$(python) -m musictool.daw video_file 4

.PHONY: docker_stream
docker_stream:
	docker run --pull=always --rm -it -v $$PWD/credentials.py:/app/credentials.py tandav/musictool-stream

.PHONY: upload_creds_makefile
upload_creds_makefile:
	#scp credentials.py Makefile cn2:~/musictool
	scp credentials.py Makefile or3:~/musictool

.PHONY: messages
messages:
	git log --pretty='%ad %h %s' --date=unix > static/messages.txt

.PHONY: build_push_stream
build_push_stream: messages
	make messages
	#docker buildx build --platform linux/arm64/v8,linux/amd64 --tag tandav/musictool-stream -f ./Dockerfile-stream --push .
	docker build --tag tandav/musictool-stream -f ./Dockerfile-stream .
	docker push tandav/musictool-stream

.PHONY: midi_html
midi_html:
	#$(python) -m musictool.daw.midi.html static/midi/vespers-04.mid
	$(python) -m musictool.daw.midi.html static/midi/vespers-04.mid
	#open logs/vespers-04
	#open logs/vespers-04/index.html

#.PHONY: profile
#profile:
# 	$(python) -m cProfile -o logs/profile.txt -m musictool.daw video
#	$(python) -m gprof2dot -f pstats logs/profile.txt | dot -Tsvg -o logs/callgraph.svg
