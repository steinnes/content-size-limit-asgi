
lint:
	poetry run flake8 content_size_limit tests

test:
	poetry run pytest -vsx --cov=content_size_limit --cov-report=term-missing --pdb
