
test:
	pytest --cov=bot

lint:
	pylint *.py
	pyflakes *.py
	flake8 *.py

run:
	python app.py
