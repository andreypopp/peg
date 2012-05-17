benchmark-pypy:
	@echo 'benchmarking pypy with peg sql grammar'
	@(cd examples; PYTHONPATH=../ pypy -m timeit \
		-n 2000 \
		-s 'from sql import stmt' \
		'stmt.parse("select a, b, c from a join b using(c) join d using(f) where a and d < c or e")')

benchmark-python:
	@echo 'benchmarking python with peg sql grammar'
	@(cd examples; PYTHONPATH=../ python -m timeit \
		-n 2000 \
		-s 'from sql import stmt' \
		'stmt.parse("select a, b, c from a join b using(c) join d using(f) where a and d < c or e")')

benchmark: benchmark-pypy benchmark-python
