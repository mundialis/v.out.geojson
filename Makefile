MODULE_TOPDIR = ../..

PGM = v.out.geojson

include $(MODULE_TOPDIR)/include/Make/Script.make

python-requirements:
	pip install -r requirements.txt

default: python-requirements script
