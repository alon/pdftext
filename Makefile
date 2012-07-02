CXXFLAGS=$(shell pkg-config --cflags poppler) -g
LDFLAGS=$(shell pkg-config --libs poppler)

all: dump_text test-dump_text

ROOT=../

.PHONY: test-dump_text

test-dump_text: dump_text
	./dump_text $(ROOT)/poppler-is-evil/evidence/cp_wrong/m03055.pdf 0 30 > m03055.pdf.text

debug: dump_text
	cgdb --args ./dump_text $(ROOT)/poppler-is-evil/evidence/cp_wrong/m03055.pdf 0 30
