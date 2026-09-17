
lint:
	poetry run flake8 content_size_limit_asgi tests

test:
	poetry run pytest -vsx --cov=content_size_limit_asgi --cov-report=term-missing --pdb

black:
	poetry run black content_size_limit_asgi
