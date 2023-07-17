test:
	python3 sle.py docs/pinos.sle
	gvim pinos.txt pinos.csv

railroad:
	python3 sle.py -o docs

markdown:
	python3 -m markdown docs/slepy.md -o html -f docs/slepy.md.html

clean:
	rm pinos.txt pinos.csv docs/slepy.md.html

static1:
	python3 -m pycodestyle sle.py

static2:
	python3 -m pyflakes sle.py

static3:
	python3 -m pylint sle.py
