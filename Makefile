python := python3.10

LINTING_DIRS := musictool tests


.PHONY: check-lint
check-lint:
	$(python) -m no_init --allow-empty $(LINTING_DIRS)
	$(python) -m force_absolute_imports $(LINTING_DIRS)
	$(python) -m isort --check-only --force-single-line-imports $(LINTING_DIRS)
	$(python) -m autoflake --recursive $(LINTING_DIRS)
	$(python) -m autopep8 --diff --recursive --aggressive --ignore=E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictool/util/wavfile.py $(LINTING_DIRS)
	$(python) -m unify --recursive $(LINTING_DIRS)
	$(python) -m flake8 $(LINTING_DIRS)
	#$(python) -m darglint --docstring-style numpy --verbosity 2 $(LINTING_DIRS)
	#$(python) -m black --diff --check --config pyproject.toml $(LINTING_DIRS)

.PHONY: fix-lint
fix-lint:
	$(python) -m force_absolute_imports --in-place $(LINTING_DIRS)
	$(python) -m isort --force-single-line-imports $(LINTING_DIRS)
	$(python) -m autoflake --recursive --in-place $(LINTING_DIRS)
	$(python) -m autopep8 --in-place --recursive --aggressive --ignore=E501,W503,E701,E704,E721,E741,I100,I201,W504 --exclude=musictool/util/wavfile.py $(LINTING_DIRS)
	$(python) -m unify --recursive --in-place $(LINTING_DIRS)
	#$(python) -m black --config pyproject.toml $(LINTING_DIRS)

.PHONY: check-mypy
mypy:
	$(python) -m mypy --config-file pyproject.toml $(LINTING_DIRS)

.PHONY: test
test:
	$(python) -m pytest -vv tests

.PHONY: check
check: check-lint mypy test

.PHONY: coverage
coverage:
	$(python) -m pytest --asyncio-mode=strict --cov=musictool --cov-report=html tests
	open htmlcov/index.html

.PHONY: midi_html
midi_html:
	#$(python) -m musictool.daw.midi.html static/midi/vespers-04.mid
	$(python) -m musictool.daw.midi.html static/midi/vespers-04.mid
	#open logs/vespers-04
	#open logs/vespers-04/index.html

.PHONY: profile
profile:
	$(python) -m cProfile -o logs/profile.txt -m musictool.daw video
	$(python) -m gprof2dot -f pstats logs/profile.txt | dot -Tsvg -o logs/callgraph.svg
