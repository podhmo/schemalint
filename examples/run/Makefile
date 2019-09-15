default: 00 01

00:
	python -m schemalint src/$@*/ok.yaml
	python -m schemalint src/$@*/ng.yaml
01:
	python -m schemalint src/$@*/ok.yaml -s src/$@*/schema.yaml
	python -m schemalint src/$@*/ng.yaml -s src/$@*/schema.yaml
