install:
	curl -sSf https://rye-up.com/get | RYE_INSTALL_OPTION="--yes" bash
	%HOMEPATH%\.rye\shims\rye $(PYTHON_VERSION)
	%HOMEPATH%\.rye\shims\rye sync

test:
	%HOMEPATH%\.rye\shims\rye run pytest tests/

lint:
	%HOMEPATH%\.rye\shims\rye lint -q -- --select I --fix 

format:
	%HOMEPATH%\.rye\shims\rye fmt

run:
	%HOMEPATH%\.rye\shims\rye run python megamania.py
	
all: install lint test