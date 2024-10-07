import glob
import os
import unittest

import sys

from lyra.engine.forward import ForwardInterpreter
from lyra.semantics.statistical_type_semantics import StatisticalTypeSemantics
from lyra.statistical.statistical_type_domain import StatisticalTypeState
from lyra.unittests.runner import TestRunner
import warnings

# TODO: Check correctness and update tests

class StatisticalTypeTest(TestRunner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, StatisticalTypeSemantics(), 3, warning_level="possible")

    def state(self):
        return StatisticalTypeState(self.variables)


def forward():
    suite = unittest.TestSuite()
    name = os.getcwd() + '/statistical/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(StatisticalTypeTest(path))
    name = os.getcwd() + '/statistical/*/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            suite.addTest(StatisticalTypeTest(path))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        result = runner.run(forward())
        if len(ws)>=1:
            print("Warnings:")
            for w in ws:
                print(str(w.category).split(".")[-1][:-2] + ": " + str(w.message))
    success = result.wasSuccessful()
    if not success:
        if result.errors:
            print('Errors in tests:')
            for test, trace in result.errors:
                print(test.path)
        if result.failures:
            print("Failures in tests:")
            for test, trace in result.failures:
                print(test.path)
        sys.exit(1)
