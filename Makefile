all: run-gui

run-gui:
		python3 -m gui.gui

test:
		py.test tests/

test-cov:
	  py.test --cov-report term-missing --cov=kbb tests/

.PHONY: clean
clean:
		find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
