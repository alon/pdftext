import os

__all__ = ['pdf_to_data']

import pdb
def pdb_assert(cond):
    if not cond:
        import pdb; pdb.set_trace()


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

def pdf_to_data(filename, start=0, end=-1, maxchars=-1):
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
