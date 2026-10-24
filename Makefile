.PHONY: build test serve
build:
	PYTHONPATH=src python -m agent_observatory.pipeline
test:
	PYTHONPATH=src python -m unittest discover -s tests -v
serve:
	python -m http.server 8000 --bind 127.0.0.1 --directory dashboard
