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


.PHONY: bumpver-dev-start
bumpver-dev-start:
	# usage: make bumpver-dev PART=minor
	# don't forget to pass PART
	bumpver update --no-fetch --tag dev --no-commit --no-tag-commit --$(PART)

.PHONY: bumpver-dev-stop
bumpver-dev-stop:
	# PART is not passed here
	bumpver update --no-fetch --tag final --no-commit --no-tag-commit
