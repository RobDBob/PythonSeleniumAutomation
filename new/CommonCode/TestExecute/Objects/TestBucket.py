import copy


class TestBucket:
    """
    Bucket of tests designed as a container for parallel test execution
    Each bucket contains related tests from the same ADO TEST SUITE
    """
    _unitTestSuite = None
    _adoTestData = None

    def __init__(self, unitTestSuite, adoTestData):
        self._unitTestSuite = unitTestSuite
        self._adoTestData = adoTestData

    @property
    def testSuiteForExecution(self):
        return copy.deepcopy(self.unitTestSuite)

    @property
    def unitTestSuite(self):
        return self._unitTestSuite
    
    @property
    def unitTestSuiteTests(self):
        return self._unitTestSuite._tests
    
    @property
    def adoTestData(self):
        return self._adoTestData
