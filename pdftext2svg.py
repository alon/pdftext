#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import os
import logging
import sys

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

import pdb
def pdb_assert(cond):
    if not cond:
        import pdb; pdb.set_trace()

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

class Char(object):
    def __init__(self, string_id, x, y, dx, dy, code_points, code):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.string_id = string_id
        self.code_points = code_points
        self.code = code
        self.uni = u''.join(map(unichr, code_points))

def pdf_to_data(filename, start, end, maxchars):
    data = []
    string_id = 0
    count = 0
    for line in os.popen('./dump_text %s %d %d ' % (filename, start, end)).readlines():
        line = line.strip()
        if line.startswith('beginString,'):
            string_id += 1
        elif line.startswith('drawChar,'):
            parts = line.split(',')
            x, y, dx, dy, originX, originY = map(float, parts[1:7])
            code, nBytes, uLen = map(int, parts[7:10])
            u = map(int, parts[10:])
            pdb_assert(len(u) == uLen)
            data.append(Char(string_id=string_id, x=x, y=y, dx=dx, dy=dy, code_points=u,
                             code=code))
            count += uLen
            if maxchars != -1 and count >= maxchars:
                break
        elif line.startswith('endString,'):
            pass
    return data

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
