TEE ?= | tee

default: 00 01 02 03 04

00:
	mkdir -p dst/$@/
	python execute.py -s src/$@*/schema.json src/$@*/ng.json ${TEE} dst/$@/ng.json.output
	python execute.py -s src/$@*/schema.json src/$@*/ng.yaml ${TEE} dst/$@/ng.yaml.output
01:
	mkdir -p dst/$@/
	python execute.py -s src/$@*/schema.json src/$@*/ng.json ${TEE} dst/$@/ng.json.output
	python execute.py -s src/$@*/schema.json src/$@*/ng.yaml ${TEE} dst/$@/ng.yaml.output
02:
	mkdir -p dst/$@/
	python execute.py -s src/$@*/schema.json src/$@*/ng.json ${TEE} dst/$@/ng.json.output
	python execute.py -s src/$@*/schema.json src/$@*/ng.yaml ${TEE} dst/$@/ng.yaml.output
03:
	mkdir -p dst/$@/
	python execute.py -s src/$@*/schema.json src/$@*/ng.yaml ${TEE} dst/$@/ng.yaml.output
04:
	mkdir -p dst/$@/
	python execute.py -s src/$@*/schema.json src/$@*/ng.yaml ${TEE} dst/$@/ng.yaml.output
