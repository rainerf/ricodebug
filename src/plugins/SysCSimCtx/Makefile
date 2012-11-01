TARGETS = ui_syscsimctxwidget.py

all: $(TARGETS)

ui_%.py: ui/%.ui
	 pyuic4 $^ > $@
