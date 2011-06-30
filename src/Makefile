TARGETS = views/ui_mainwindow.py resources_rc.py

all: $(TARGETS)

views/ui_mainwindow.py: views/mainwindow.ui
	 pyuic4 $^ > $@

resources_rc.py: resources.qrc
	pyrcc4 $^ > $@

.PHONY: clean pylint
clean:
	rm -f $(TARGETS)
	find -name '*.pyc' | xargs rm -fr

pylint:
	pylint --include-ids=y --disable=W0312,C0103,C0111,C0301 *.py
