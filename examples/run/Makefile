default: 00 01 02

00:
	python -m schemalint src/$@*/ok.yaml --always-success
	python -m schemalint src/$@*/ng.yaml --always-success
01:
	python -m schemalint src/$@*/ok.yaml -s src/$@*/schema.yaml --always-success
	python -m schemalint src/$@*/ng.yaml -s src/$@*/schema.yaml --always-success
02:
	python -m schemalint src/$@*/ok.yaml --guess-schema --always-success
	python -m schemalint src/$@*/ng.yaml --guess-schema --always-success
