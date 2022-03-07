python := python3.10

.PHONY: lint
lint:
	$(python) -m no_init musictool tests
	$(python) -m force_absolute_imports --in-place musictool tests
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
	$(python) -m pytest -s -vv --cov=musictool --asyncio-mode=strict tests

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
