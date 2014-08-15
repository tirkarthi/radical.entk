#!/usr/bin/env python

"""This module defines and implements the Kernel class.
"""

__author__    = "Ole Weider <ole.weidner@rutgers.edu>"
__copyright__ = "Copyright 2014, http://radical.rutgers.edu"
__license__   = "MIT"

from radical.ensemblemd.engine import Engine
from radical.ensemblemd.exceptions import TypeError


# ------------------------------------------------------------------------------
#
class Kernel(object):
    
    #---------------------------------------------------------------------------
    #
    def __init__(self, kernel, args):
        """Create a new Kernel object.
        """
        if type(kernel) != str:
            raise TypeError(
                expected_type=str, 
                actual_type=type(kernel))

        if type(args) != list:
            raise TypeError(
                expected_type=list, 
                actual_type=type(args))

        self._engine = Engine()
        self._kernel = self._engine.get_kernel_plugin(kernel)

        # Call the validate_args() method of the plug-in.
        self._kernel.validate_args(args)

    #---------------------------------------------------------------------------
    #
    def get_args(self):
        """Returns the arguments that were passsed to the kernel during 
           creation.
        """
        return self._kernel.get_args()