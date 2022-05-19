REPORT_TEMPLATE = """<html>
    <head></head>
    <body style='font-family:Calibri; font-size:90%'>
        <style type='text/css'>
            <!--
                .tab {{ margin-left: 40px; }}
            -->
        </style>
        <p>Hello<br><br>Automation finished running and I am an Automated Test Report.<br></p>
        <p>{0}</p>
        {1}{2}
    </body>
</html>"""

STATS_TEMPLATE = """Total Test Cases in this Run = {0}
<p class='tab'>
    Passed = {1}<br>
    Failed = {2}<br>
    Blocked = {3}<br>
</p>
Total Executed = {1} + {2} = {4}<br>
Pass Rate = {1} / {4} = {5}%<br>
Run Time: {6}<br>
{7}"""

TABLE_TEMPLATE_FAILURES = """<p>List of failed tests</p>
<p><table style="width:100%; font-family:Calibri; font-size:90%">
  <tr>
    <td>ID</td>
    <td>Title</td>
    <td>Bug ID</td>
    <td>Last 7 runs</td>
    <td>History</td>
  </tr>
  {0}
</table></p>"""

ROW_TEMPLATE_FAILURES = """<tr>
<td>{0}</td>
<td>{1}</td>
<td>{2}</td>
<td bgcolor="#ff3300">Failed {3}x</td>
<td>{4}</td>
</tr>"""

TABLE_TEMPLATE_ALL_RESULTS = """<p>List of all test results</p>
<p><table style="width:100%; font-family:Calibri; font-size:90%">
  <tr>
    <td>ID</td>
    <td>Title</td>
    <td>Status</td>
  </tr>
  {0}
</table></p>"""

ROW_TEMPLATE_ALL_RESULTS = """<tr>
<td>{0}</td>
<td>{1}</td>
<td bgcolor="{2}">{3}</td>
</tr>"""

ROW_TEMPLATE_SECTION = """<tr><th colspan=4>{0}</th></tr>"""

RESULT_HISTORY = """<table style="width:50%">{0}</table>"""
RESULT_HISTORY_ENTRY = """<td bgcolor="{0}"></td>"""

TEST_TITLE = '<a href="https://testrail.prod.company.com/index.php?/tests/view/{0}">{1}</a>'
BUG_ID = '<a href="https://SomeJira.com/jira/browse/{0}">{0}</a>'
EMAIL_TITLE = '{0}, Pass rate {1}% ({2}/{3}) - {4} build {5}'
TIME_TAKEN = '{0} hours {1} minutes'
