.PHONY: typehint
typehint:
	pytype $(file)

.PHONY: black
black:
	black --diff $(file)

.PHONY: pytest
test:
	python3 -m pytest


.PHONY: checklist
checklist: typehint black

.PHONY: test
test: pytest