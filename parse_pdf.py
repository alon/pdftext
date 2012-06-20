# Via pdfshow (part of mupdf)
#
example_text="""BT

/F1 12 Tf

1 0 0 1 274.61 112.46 Tm

[<000300B4009F>-3<009F>4<00B0000300B3009A00B20003>-9<000F00B200AE009F>6<00AB000
300A9>-3<009F>4<00B200B30003001D>-2<00B2009F>4<00B300A3009A>] TJ

ET
"""

from pyparsing import *

def cvtInt(toks):
    t = toks[0]
    if t[:2] == '0x':
        return int(t, 16)
    return int(t)

bnf = None
def PDF_BNF():
    global bnf
    if bnf:
        return bnf
    text_start = Keyword("BT")
    text_end = Keyword("ET")
    font_name = Literal('/F') + Word(nums)
    font_directive = Keyword("Tf")
    lbrack = Literal("[").suppress()
    rbrack = Literal("]").suppress()
    lesserthen = Literal("<").suppress()
    greaterthen = Literal(">").suppress()
    text_string_directive = Keyword('TJ')
    text_matrix_directive = Keyword('Tm')
    # TODO - this doesn't parse float. Word is wrong, looks for word end. So is OneOrMore.
    _float = ( OneOrMore( nums+"+-", nums) + "." + Word(nums) | Word( nums+"+-", nums )  ).setName("float").setParseAction(lambda toks: float(toks[0]))
    integer = ( Combine( CaselessLiteral("0x") + Word( nums+"abcdefABCDEF" ) ) |
        Word( nums+"+-", nums ) ).setName("int").setParseAction(cvtInt)
    font = font_name + integer + font_directive
    matrix = _float * 6
    #text_string =
    #text = text_start + ZeroOrMore(font | matrix | text_string) + text_end
    bnf = font
    return bnf


def parse_text(snippet):
    """
    """
    bnf = PDF_BNF()
    parts = bnf.parseString(snippet)
    for p in parts:
        # TODO
        print p
