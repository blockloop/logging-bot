
test:
	pytest

lint:
	pylint *.py
	pyflakes *.py
	flake8 *.py

run:
	python app.py
