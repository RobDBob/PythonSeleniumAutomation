import re
from os import environ
import certifi
from jira import JIRA
from jira.exceptions import JIRAError
from requests.exceptions import ConnectTimeout, JSONDecodeError
from retry import retry
from urllib3 import exceptions
from CommonCode.TestExecute.Logging import PrintMessage

JIRA_URL = 'https://portal.fnz.com/jira'


class JiraWrapper:
    _jiraInterface = None
    _allJiraIssueStatuses = {}

    def __init__(self):
        self.jiraPAT = environ.get("JIRA_PAT")

    def getJiraTickets(self, tags: str):
        jiraIssueStatuses = {}
        for jiraIssueId in re.findall(r"(SLP-\d{6})", tags.replace(" ", ""), re.IGNORECASE):
            if jiraIssueId not in self._allJiraIssueStatuses:
                jiraIssue = self.getIssue(jiraIssueId)

                # maintain overall list of jira issues to avoid overhitting jira server
                if jiraIssue:
                    self._allJiraIssueStatuses[jiraIssueId] = jiraIssue.fields.status
                else:
                    self._allJiraIssueStatuses[jiraIssueId] = None

            jiraIssueStatuses[jiraIssueId] = self._allJiraIssueStatuses[jiraIssueId]

        return jiraIssueStatuses

    @retry(exceptions=JSONDecodeError, tries=5, delay=5, backoff=3)
    def getIssue(self, issueId):

        try:
            if self.jiraInterface:
                return self.jiraInterface.issue(id=issueId)
            return None
        except JIRAError:
            PrintMessage(f"No details found for id: '{issueId}'")
            return None

    @property
    def jiraInterface(self):
        try:
            if self._jiraInterface is None:
                self._jiraInterface = JIRA(options={'server': JIRA_URL, 'verify': certifi.where()}, token_auth=self.jiraPAT)
            return self._jiraInterface
        except (exceptions.ConnectTimeoutError, ConnectTimeout):
            PrintMessage("Failed to connect to JIRA server")
            return None
