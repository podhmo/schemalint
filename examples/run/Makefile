default: 00 01 02 03

# load error
00:
	python -m schemalint src/$@*/ok.yaml --always-success
	python -m schemalint src/$@*/ng.yaml --always-success

# schema validation error
01:
	python -m schemalint src/$@*/ok.yaml -s src/$@*/schema.yaml --always-success
	python -m schemalint src/$@*/ng.yaml -s src/$@*/schema.yaml --always-success

# guess-schema
02:
	python -m schemalint src/$@*/ok.yaml --guess-schema --always-success
	python -m schemalint src/$@*/ng.yaml --guess-schema --always-success

# guess-schema is failed
03:
	python -m schemalint src/00*/ok.yaml --always-success -g
