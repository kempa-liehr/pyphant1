#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) 2006-2009, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""Provides unittest classes for AutoFocus worker.
"""

__id__ = "$Id$".replace('$','')
__author__ = "$Author$".replace('$','')
__version__ = "$Revision$".replace('$','')
# $Source$

import unittest
import pkg_resources
pkg_resources.require("pyphant")
from pyphant.quantities.PhysicalQuantities import PhysicalQuantity as PQ
from pyphant.core.DataContainer import FieldContainer, SampleContainer,\
     assertEqual
from ImageProcessing import AutoFocus as AF
import numpy


class CubeTestCase(unittest.TestCase):
    def setUp(self):
        self.cube1 = AF.Cube([slice(0, 10),
                              slice(0, 10),
                              slice(0, 10)])
        self.cube2 = AF.Cube([slice(3, 5),
                              slice(4, 6),
                              slice(-5, 7)])
    def tearDown(self):
        pass

    def testEq(self):
        cube1c = AF.Cube(self.cube1.slices)
        assertEqual(self.cube1, cube1c)
        assert not self.cube1.__eq__(self.cube2, 0, 0)

    def testAnd(self):
        expected = AF.Cube([slice(3, 5), slice(4, 6), slice(0, 7)])
        assertEqual(self.cube1 & self.cube2, expected)

    def testOr(self):
        expected = AF.Cube([slice(0, 10), slice(0, 10), slice(-5, 10)])
        assertEqual(self.cube1 | self.cube2, expected)

    def testVolume(self):
        assert self.cube1.getVolume() == 1000
        assert self.cube2.getVolume() == 48
        assert AF.Cube([slice(0, 0),
                       slice(0, 1000),
                       slice(0, 1000)]).getVolume() == 0

    def testSubCube(self):
        expected = AF.Cube([slice(3,5 ), slice(-5, 7)])
        assertEqual(self.cube2.getSubCube([0, 2]), expected)

    def testGetEdgeLength(self):
        assert self.cube2.getEdgeLength(0) == 2
        assert self.cube2.getEdgeLength(1) == 2
        assert self.cube2.getEdgeLength(2) == 12

    def testSub(self):
        expected = AF.Cube([slice(-3, 7),
                            slice(-4, 6),
                            slice(5, 15)])
        assertEqual(self.cube1 - self.cube2, expected)



class ZTubeTestCase(unittest.TestCase):
    def setUp(self):
        slices = [slice(0, 10), slice(0, 10)]
        mask = numpy.zeros((10, 10), dtype=bool) # TODO
        fslice = AF.FocusSlice(slices, 10.0, mask, 1)
        self.ztube = AF.ZTube(fslice, 0, 1, 0.5, 0.5)
        testslices1 = [slice(3, 12), slice(2, 9)]
        testmask1 = numpy.zeros((9, 7), dtype=bool)
        self.testfslice1 = AF.FocusSlice(testslices1, 12.0, testmask1, 2)
        testslices2 = [slice(7, 17), slice(8, 16)]
        testmask2 = numpy.zeros((10, 8), dtype=bool)
        self.testfslice2 = AF.FocusSlice(testslices2, 8.0, testmask2, 3)

    def tearDown(self):
        pass

    def testMatching(self):
        assert self.ztube.match(self.testfslice1, 1)
        assert not self.ztube.match(self.testfslice2, 1)
        assert self.testfslice1 in self.ztube
        assert self.testfslice2 not in self.ztube
        expectedyx = AF.Cube([slice(0, 12),
                              slice(0, 10)])
        expectedz = AF.Cube([slice(-1, 2)])
        assertEqual(self.ztube.yxCube, expectedyx)
        assertEqual(self.ztube.zCube, expectedz)
        assert self.ztube.mask.shape == (12, 10)
        assert self.ztube.focusedIndex == 1

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(
            eval(sys.argv[1:][0]))
        unittest.TextTestRunner().run(suite)
