#!/usr/bin/sh

for count in 100 200 300 400 500; do

	for inf in 0.01 0.02 0.03 0.04 0.05; do

		for esp in 0.05 0.06 0.07 0.08 0.09 0.1; do

			for limiar in {1..8}; do

				python3.15t ../FakeNews.py "$count" "$count" 100 "$inf" "$esp" 0.1 "$limiar"

			done

		done

	done

done
