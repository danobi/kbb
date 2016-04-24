all: run-gui

run-gui:
		python3 -m gui.gui

test:
	  py.test tests/

.PHONY: clean
clean:
	  find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
