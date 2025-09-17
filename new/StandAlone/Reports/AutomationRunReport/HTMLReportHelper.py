RESULT_HEADER_ROW = """<tr><th>Owner</th><th>Test Case</th><th>Test Result</th>
<th>Test Execution History</th><th>{0}Count Last Month</th><th>Tags</th><th>Jira Issues</th></tr>"""

RESULT_DATA_ROW = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td></tr>"


def wrapInHyperlink(linkText, linkUrl):
    return f"<a href='{linkUrl}'>{linkText}</a>"


def getJiraTicketStatusAsText(jiraIssueStatuses: dict):
    textValue = ""
    for jiraIssueKey, jiraIssueValue in jiraIssueStatuses.items():
        if textValue:
            textValue += "<br>"
        textValue += f"{jiraIssueKey}:{jiraIssueValue}"
    return textValue


def getResultTableRow(entity: dict, testTypeCount):
    testCaseId = entity.get("testCaseId")
    testCaseName = entity.get('testCaseName').replace(f"test_C{testCaseId}_", "")
    return RESULT_DATA_ROW.format(entity.get("author"),
                                  f"{wrapInHyperlink(testCaseId, entity.get('urlTestCase'))}: {testCaseName[:40]}",
                                  wrapInHyperlink("Current Result", entity.get("urlResult")),
                                  wrapInHyperlink("Historic Results", entity.get("urlExecutionHistory")),
                                  entity.get(testTypeCount),
                                  entity.get("tags"),
                                  getJiraTicketStatusAsText(entity.get("jiraIssueStatuses")))


def getResultsTableRowsHTML(entities, testTypeCount):
    tableRows = []
    for entity in entities:
        tableRows.append(getResultTableRow(entity, testTypeCount))
    return "".join(tableRows)


def generateReportFailedTests(reportData: dict, runId: str, runTitleTrimmed: str):
    tableRowsFailedTests = getResultsTableRowsHTML(reportData.get("failedTests", []), "failCount")
    tableRowsBlockedTests = getResultsTableRowsHTML(reportData.get("blockedTests", []), "blockedCount")
    styles = "table, th, td { border:1px solid black;border-collapse: collapse;}"
    runURL = reportData.get("urlTestRun", "Test Run URL not available")
    runName = reportData.get("runName", "Test Run Name not available")

    htmlFailed = f"""
    <h2> Failed tests:</h2>
    <table style="width:100%">{RESULT_HEADER_ROW.format('Fail')}{tableRowsFailedTests}</table>
    """ if tableRowsFailedTests else ""

    htmlBlocked = f"""
    <h2> Blocked tests:</h2>
    <table style="width:100%">{RESULT_HEADER_ROW.format('Blocked')}{tableRowsBlockedTests}</table>
    """ if tableRowsBlockedTests else ""

    html = f'''
        <html>
            <style>{styles}</style>
            <body>
                <h1>Test results for {runName}, run Id: {runId}</h1>
                {htmlFailed}
                {htmlBlocked}
                <div>See run details : {wrapInHyperlink('run', runURL)}</div>
            </body>
        </html>
        '''

    reportFailedTestsName = f"Report_{runTitleTrimmed}.html"
    with open(reportFailedTestsName, 'w', encoding="utf-8") as f:
        f.write(html)

    # this is to set environment variable in ADO Pipelines
    print(f"##vso[task.setvariable variable=FAILED_TESTS_REPORT_NAME;]{reportFailedTestsName}")
