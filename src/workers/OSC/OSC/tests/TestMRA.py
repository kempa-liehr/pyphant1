# -*- coding: utf-8 -*-

# Copyright (c) 2008, Rectorate of the University of Freiburg
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

u"""Provides unittest classes TestMRA and TestMRADiscontinuousDiscretisation.
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$


import sys,copy
import unittest
sys.path.append("..")

import pkg_resources

pkg_resources.require("Pyphant")
pkg_resources.require("Pyphant_OSC")

import os.path

import numpy, scipy, scipy.optimize
import Scientific.Physics.PhysicalQuantities as pq
import OSC.MRA as MRA
from pyphant.core import DataContainer as DC
from TestExtremumFinder import fixedPoints

class TestMRA(unittest.TestCase):
    """Sets up a mirror symmetric bistable potential with a continuous
    distretisation and computes its local extrema and the respective
    curvatures."""
    def setUp(self):
        self.n = 1000
        self.u = numpy.linspace(-1.5,1.5,self.n)
        self.LAMBDA = 0.5
        self.kappa1=0.0
        self.xField = DC.FieldContainer(self.u,
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        self.V = DC.FieldContainer(-self.LAMBDA/2* self.u**2 + self.u**4/4-self.u*self.kappa1,
                                   unit='1 V',dimensions=[self.xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi')
        
    def testMinima(self):
        """Test the correct computation of all local minima for a bistable potential."""
        #Predict result
        x0,curv,mask = fixedPoints(numpy.array([self.LAMBDA]),kappa1=self.kappa1)
        expectedResult = DC.FieldContainer(numpy.extract(curv[0]>0,x0[0]),
                                           unit = self.xField.unit,
                                           longname = 'position of the local minima of electric potential',
                                           shortname = 'x_0')
        #Retrieve result from worker
        w = MRA.MRA(None)
        w.paramScale.value = "1.0m"
        result = w.mra(self.V)
        #Testing
        numpy.testing.assert_array_almost_equal(result.data,expectedResult.data,4)
        
class TestExtremumFinderTable(unittest.TestCase):
    """Sets up a mirror symmetric bistable potential with a continuous
    distretisation and computes its local extrema and the respective
    curvatures."""
    def setUp(self):
        self.n = 1000
        self.m = 10
        self.kappa1=0.0
        self.errLevelPos = 2
        self.errLevelCurv= 5
        self.test = DC.assertEqual

    def prepareDimensions(self):
        X,LAMB = scipy.meshgrid(numpy.linspace(-1.5,1.5,self.n),
                                numpy.linspace(-1.0,1.0,self.m))
        self.lambDim = LAMB[:,0]
        self.xDim = X

    def testRoots(self):
        """Test the correct computation of all local extrema for a bistable potential."""
        #Prepare dimensions
        self.prepareDimensions()
        lambField = DC.FieldContainer(self.lambDim,
                                      unit = '1 V / m**3',
                                      longname='parameter',
                                      shortname='\lambda')
        xField = DC.FieldContainer(self.xDim[0],
                                   unit = '1 m',
                                   longname = 'position',
                                   shortname = 'x')
        #Prepare potential
        V = []
        for i in xrange(len(lambField.data)):
            u = xField.data
            V.append(-lambField.data[i]/2* u**2 + u**4/4-u*self.kappa1)
        self.V = DC.FieldContainer(numpy.array(V),unit='1 V',dimensions=[lambField,xField],
                                   longname = 'electric potential',
                                   shortname=r'\varphi')
        #Predict result
        x0,curv,mask = fixedPoints(lambField.data,kappa1=self.kappa1)
        x0 = numpy.where(curv>0, x0, numpy.NaN)
        data = x0[:,::2]
        dims = [lambField, DC.generateIndex(0,2)]
        expectedResult = DC.FieldContainer(data,
                                           unit = xField.unit,
                                           mask = numpy.isnan(data),
                                           dimensions = dims,
                                           longname = 'position of the local extrema of electric potential',
                                           shortname = 'x_0')
        #Configure worker
        w = MRA.MRA(None)
        w.paramScale.value = "1.0m"
        #Retrieve result from worker
        result = copy.deepcopy(w.mra(self.V))
        result.error=None
        self.test(result,expectedResult,1e-2,1e-2)

if __name__ == '__main__':
    unittest.main()
