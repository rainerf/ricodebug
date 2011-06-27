TARGETS = views/ui_mainwindow.py resources_rc.py

all: $(TARGETS)

views/ui_mainwindow.py: views/mainwindow.ui
	 pyuic4 $^ > $@

resources_rc.py: resources.qrc
	pyrcc4 $^ > $@

.PHONY: clean pylint
clean:
	rm $(TARGETS)
	rm *.pyc
	rm controllers/*.pyc
	rm helpers/*.pyc
	rm models/*.pyc
	rm views/*.pyc
	rm variables/*.pyc
	rm datagraph/*.pyc
	rm plugins/*/*.pyc

pylint:
	pylint --include-ids=y --disable=W0312,C0103,C0111,C0301 *.py
