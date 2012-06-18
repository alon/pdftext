CXXFLAGS=$(shell pkg-config --cflags poppler) -g
LDFLAGS=$(shell pkg-config --libs poppler)

all: poppler test-poppler

.PHONY: test-poppler

test-poppler: poppler
	./poppler /images/openknesset/poppler_is_evil/evidence/cp_wrong/m03055.pdf
