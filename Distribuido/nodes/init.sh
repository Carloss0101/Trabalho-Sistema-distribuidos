#!/usr/bin/sh

python3.15t broker.py &

for i in {1..5}; do

	python3.15t worker.py  &
	sleep 0.2s

done

PYTHON_GIL=0 python3.15t master.py 1000 1000 100 0.01 0.05 0.1 2 0
