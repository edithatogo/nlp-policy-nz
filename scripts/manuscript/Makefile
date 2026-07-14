PDF=main.pdf

all: $(PDF)

$(PDF): main.tex macros.tex references.bib
	latexmk -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -C
