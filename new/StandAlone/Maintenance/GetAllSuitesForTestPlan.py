from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests

def writeTestSuiteNames(testPlanId, envName):
    adoRequests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN)
    testSuites = adoRequests.testSuitesGet(testPlanId)

    with open(f"{envName}suites.csv", "w") as fp:
        testSuiteNames = [testSuite["name"] + "\n" for testSuite in testSuites] 
        fp.writelines(testSuiteNames)
     
def saveAllTestSuitesToCSVFile():
    writeTestSuiteNames(1365253, "TE5")
    writeTestSuiteNames(1463138, "UE1")
    writeTestSuiteNames(1510710, "DE68")


def findDiffInTestSuites():
    adoRequests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN)
    te5Suites = [k["name"] for k in adoRequests.testSuitesGet(1365253)]
    ue1Suites = [k["name"] for k in adoRequests.testSuitesGet(1463138)]
    de68Suites = [k["name"] for k in adoRequests.testSuitesGet(1510710)]

    print(1)


if __name__ == "__main__":
    # saveAllTestSuitesToCSVFile()
    findDiffInTestSuites()