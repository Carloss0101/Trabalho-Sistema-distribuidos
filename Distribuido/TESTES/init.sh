#!/usr/bin/sh

for count in 100 200 300 400 500; do

	for inf in 0.01 0.02 0.03 0.04 0.05; do

		for esp in 0.05 0.06 0.07 0.08 0.09; do

			for limiar in {1..8}; do

				PYTHON_GIL=0 python3.15t ../nodes/broker.py &
				sleep 1s

				broker_port=$(cat broker_port.txt)

				for worker in {1..5}; do

					PYTHON_GIL=0 python3.15t ../nodes/worker.py "$broker_port" &

					sleep 0.15

				done

				PYTHON_GIL=0 python3.15t ../nodes/master.py "$count" "$count" 100 "$inf" "$esp" 0.1 "$limiar" 0 "$broker_port"

			done

		done

	done

done
