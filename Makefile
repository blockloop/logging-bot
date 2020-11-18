

TEST_FILES := $(wildcard *_test.py)
SRC_FILES := $(filter-out $(TEST_FILES), $(wildcard *.py))

test: $(SRC_FILES) $(TEST_FILES)
	pytest --cov=bot

lint: target/lint.txt
target/lint.txt: $(SRC_FILES) $(TEST_FILES)
	pylint $?
	pyflakes $?
	flake8 $?
	touch $@

run: $(SRC_FILES)
	python app.py
