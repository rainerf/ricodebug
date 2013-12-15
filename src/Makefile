TARGETS = views/ui_mainwindow.py views/ui_logviewtab.py views/ui_mitraceview.py views/ui_notificationframe.py views/ui_breakpointwidget.py resources_rc.py

all: $(TARGETS)

views/ui_%.py: views/%.ui
	 pyuic4 $^ > $@

resources_rc.py: resources.qrc
	pyrcc4 -py3 $^ > $@

.PHONY: clean pylint
clean:
	rm -f $(TARGETS)
	find . \( -name '__pycache__' -o -name '*.pyc' \) -prune -exec rm -fr {} \;

pylint:
	pylint --include-ids=y --disable=W0312,C0103,C0111,C0301 --ignored-classes=Icons --output=colorized **/*.py

coverage:
	python-coverage run ricodebug.py
	python-coverage report **/*.py
	python-coverage html
	xdg-open htmlcov/index.html
