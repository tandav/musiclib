LINTING_DIRS := musictool tests

.PHONY: check-lint
check-lint:
	#python -m no_init --allow-empty $(LINTING_DIRS)
	python -m force_absolute_imports $(LINTING_DIRS)
	python -m isort --check-only $(LINTING_DIRS)
	python -m autoflake --recursive $(LINTING_DIRS)
	python -m autopep8 --diff $(LINTING_DIRS)
	python -m flake8 $(LINTING_DIRS)

.PHONY: fix-lint
fix-lint:
	python -m autoflake --recursive --in-place $(LINTING_DIRS)

.PHONY: check-mypy
mypy:
	python -m mypy $(LINTING_DIRS)

.PHONY: test
test:
	pytest

.PHONY: check
check: check-lint mypy test

.PHONY: coverage
coverage:
	python -m pytest --asyncio-mode=strict --cov=musictool --cov-report=html tests
	open htmlcov/index.html

.PHONY: midi_html
midi_html:
	#python -m musictool.daw.midi.html static/midi/vespers-04.mid
	python -m musictool.daw.midi.html static/midi/vespers-04.mid
	#open logs/vespers-04
	#open logs/vespers-04/index.html

.PHONY: profile
profile:
	python -m cProfile -o logs/profile.txt -m musictool.daw video
	python -m gprof2dot -f pstats logs/profile.txt | dot -Tsvg -o logs/callgraph.svg

.PHONY: bumpver
bumpver:
	# usage: make bumpver PART=minor
	bumpver update --no-fetch --$(PART)
