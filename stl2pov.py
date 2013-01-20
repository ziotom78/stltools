#! /usr/bin/env python
# -*- python coding: utf-8 -*-
# Copyright © 2012 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# $Date$
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""Program for converting an STL file into a POV-ray mesh or mesh2."""

import argparse
import sys
import os
import time
from brep import stl

ver = ('stl2pov [ver. ' + '$Revision$'[11:-2] + 
       '] ('+'$Date$'[7:17]+')')


def mesh1(rf):
    """Returns a string containing the facet list s as a POV-ray mesh
    object."""
    ms = "# declare m_{} = mesh {{\n".format(rf.name.replace(' ', '_'))
    sot = "  triangle {\n"
    fc = "    <{1}, {0}, {2}>,\n"
    fct = "    <{1}, {0}, {2}>\n"
    for f in rf.facets:
        ms += sot
        ms += fc.format(f[0][0], f[0][1], f[0][2])
        ms += fc.format(f[1][0], f[1][1], f[1][2])
        ms += fct.format(f[2][0], f[2][1], f[2][2])
        ms += "  }\n"
    ms += "}\n"
    return ms


def mesh2(s):
    """Returns a string containing the stl.IndexedMesh s as a POV-ray
    mesh2 object."""
    ms = "# declare m_{} = mesh2 {{\n".format(s.name)
    ms += '  vertex_vectors {\n'
    ms += '    {},\n'.format(len(s.points))
    for p in s.points:
        ms += '    <{1}, {0}, {2}>,\n'.format(p[0], p[1], p[2])
    ms = ms[:-2]
    ms += '\n  }\n'
    ms += '  face_indices {\n'
    ms += '    {},\n'.format(len(s.ifacets))
    for ((a, b, c), ni, li) in s.ifacets:  #pylint: disable=W0612
        ms += '    <{}, {}, {}>,\n'.format(a, b, c)
    ms = ms[:-2]
    ms += '\n  }\n}\n'
    return ms


def main(argv):
    """Main program.

    Keyword arguments:
    argv -- command line arguments (without program name!)
    """
    parser = argparse.ArgumentParser(description=__doc__)
    argtxt = 'generate a mesh2 object (slow on big files)'
    parser.add_argument('-2,' '--mesh2', action='store_true', 
                        help=argtxt, dest='mesh2')
    parser.add_argument('file', nargs='*', help='one or more file names')
    args = parser.parse_args(argv)
    if not args.file:
        parser.print_help()
        sys.exit(0)
    for fn in args.file:
        root, ext = os.path.splitext(fn)  #pylint: disable=W0612
        outfn = os.path.basename(root) + '.inc'
        try:
            rf = stl.fromfile(fn)
        except ValueError as e:
            print fn + ':', e
        outs = "// Generated by {}\n// on {}.\n".format(ver, time.asctime())
        outs += "// Source file name: '{}'\n".format(fn)
        if args.mesh2:
            s = stl.make_indexed_mesh(rf)
            outs += s.stats('// ') + '\n'
            outs += mesh2(s)
        else:
            outs += rf.stats('// ') + '\n'
            outs += mesh1(rf)
        try:
            with open(outfn, 'w+') as of:
                of.write(outs)
        except:
            print "Cannot write output file '{}'".format(outfn)
            sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
