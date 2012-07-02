#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import os
import logging
import sys
from mypdf2text import pdf_to_data

logger = logging.Logger('test')
logger.level = 0
logger.addHandler(logging.StreamHandler(sys.stdout))
log = logger.info

svg_template = u"""<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg xmlns="http://www.w3.org/2000/svg" version="1.1"
      width="%(width)d" height="%(height)d" viewBox="%(viewBox)s">
%(contents)s
</svg>
"""

def quote(txt):
    def quote_char(c):
        if c == '&':
            return '&amp;'
        return c
    return ''.join(quote_char(c) for c in txt)

def text_node(x, y, txt, font_size=10):
    return u'<text font-size="%d" x="%f" y="%f">%s</text>' % (font_size, x, y, quote(txt))

def to_svg(data, width, height, viewBox):
    #width="540" height="200" viewBox="0 0 270 100"
    nodes = []
    assert(len(viewBox) == 4)
    viewBox = ' '.join(map(str, viewBox))
    tagged = 0
    for c in data:
        nodes.append(text_node(c.x, c.y, c.uni))
        if len(c.code_points) == 1:
            u = c.code_points[0]
            if u == 32: # or (ord(u'ת') >= u >= ord(u'א')):
                continue
        nodes.append(text_node(c.x, c.y_mid , str(c.code), font_size=2))
        tagged += 1
    log('tagged %d chars' % tagged)
    return (svg_template % dict(width=width, height=height, viewBox=viewBox,
            contents='\n'.join(nodes))).encode('utf-8')

def multitude(xs):
    s = dict()
    ret = []
    for x in xs:
        if x in s:
            ret[s[x]] += 1
        else:
            s[x] = len(ret)
            ret.append((x, 0))
    return ret

def tag_with_line_offsets(data):
    ys = [c.y for c in data]
    #repeats = multitude(ys)
    ys = sorted(set(ys))
    ys_next = dict([(ys[i], ys[i+1]) for i in xrange(len(ys)-1)])
    ys_next[ys[-1]] = ys[-1] + (ys[-1] - ys[-2])
    for c in data:
        c.y_delta = ys_next[c.y] - c.y
        c.y_mid = c.y + c.y_delta / 2

def data_to_svg(data, out_filename):
    width, height, viewBox = data_to_enclosure(data)
    with open(out_filename, 'w+') as fd:
        fd.write(to_svg(data=data, width=width, height=height, viewBox=viewBox))

def data_to_enclosure(data):
    first = data[0]
    x0, y0, x1, y1 = first.x, first.y, first.x, first.y
    for c in data:
        x0 = min(c.x, x0)
        y0 = min(c.y, y0)
        x1 = max(c.x, x1)
        y1 = max(c.y, y1)
    width = x1 - x0
    height = y1 - y0
    viewBox = [x0, y0, x1, y1]
    return width, height, viewBox

def drop_spaces(data):
    delete = []
    for i, c in enumerate(data):
        if c.code_points == [32]:
            delete.append(i)
    for i in reversed(delete):
        del data[i]
    print "dropped %d spaces" % len(delete)

import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument('--filename', default='/images/openknesset/poppler_is_evil/evidence/cp_wrong/m03055.pdf')
parser.add_argument('--startpage', default=1, type=int)
parser.add_argument('--endpage', default=2, type=int)
parser.add_argument('--output', default='output.svg')
parser.add_argument('--maxchars', default=-1, type=int)
args = parser.parse_args(sys.argv[1:])
data = pdf_to_data(args.filename, args.startpage, args.endpage, args.maxchars)
drop_spaces(data)
tag_with_line_offsets(data)
data_to_svg(data, args.output)
os.system('inkscape %s &' % args.output)
#os.system('xdg-open %s &' % args.output)
