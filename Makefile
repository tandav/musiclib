.PHONY: test
test:
	pytest

.PHONY: coverage
coverage:
	python -m pytest --cov=musiclib --cov-report=html tests
	open htmlcov/index.html

.PHONY: profile
profile:
	python -m cProfile -o logs/profile.txt -m musiclib.daw video
	python -m gprof2dot -f pstats logs/profile.txt | dot -Tsvg -o logs/callgraph.svg

.PHONY: bumpver
bumpver:
	# usage: make bumpver PART=minor
	bumpver update --no-fetch --$(PART)
