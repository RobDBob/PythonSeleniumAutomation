import re
from os import environ
import certifi
from jira import JIRA
from jira.exceptions import JIRAError
from requests.exceptions import ConnectTimeout, JSONDecodeError
from retry import retry
from urllib3 import exceptions
from CommonCode.CustomExceptions import APIException
from CommonCode.TestExecute.Logging import PrintMessage

JIRA_URL = 'https://portal.fnz.com/jira'


class JiraWrapper:
    _jiraInterface = None
    _allJiraIssueStatuses = {}

    def __init__(self):
        self.jiraPAT = environ.get("JIRA_PAT")

    def getJiraTicketsStatuses(self, tags: str):
        jiraTicketStatuses = {}
        for jiraIssueId in re.findall(r"(SLP-\d{6})", tags.replace(" ", ""), re.IGNORECASE):
            if jiraIssueId not in self._allJiraIssueStatuses:
                PrintMessage(f"Getting jira details for ticket: '{jiraIssueId}'")
                jiraIssue = self.getIssue(jiraIssueId)
                PrintMessage(f"Getting jira details for ticket: '{jiraIssueId}' - Done")

                # maintain overall list of jira issues to avoid overhitting jira server
                if jiraIssue:
                    self._allJiraIssueStatuses[jiraIssueId] = jiraIssue.fields.status.name
                else:
                    self._allJiraIssueStatuses[jiraIssueId] = None

            jiraTicketStatuses[jiraIssueId] = self._allJiraIssueStatuses[jiraIssueId]

        return jiraTicketStatuses

    @retry(exceptions=(JSONDecodeError, JIRAError, APIException), tries=5, delay=15, backoff=3)
    def getIssue(self, issueId):
        if self.jiraInterface:
            return self.jiraInterface.issue(id=issueId)
        raise APIException("No connection to JIRA established")

    @property
    def jiraInterface(self):
        try:
            if self._jiraInterface is None:
                self._jiraInterface = JIRA(options={'server': JIRA_URL, 'verify': certifi.where()}, token_auth=self.jiraPAT)
            return self._jiraInterface
        except (exceptions.ConnectTimeoutError, ConnectTimeout):
            PrintMessage("Failed to connect to JIRA server")
            self._jiraInterface = None
            return self._jiraInterface
