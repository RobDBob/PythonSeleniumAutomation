import json
from types import SimpleNamespace
import requests
from retry import retry
from CommonCode.CustomExceptions import APIException
from CommonCode.TestExecute.Logging import PrintMessage

requests.urllib3.disable_warnings()


class TestEMailRequests:
    TEST_MAIL_URL = "https://api.testmail.app/api/json"
    # Details from https://testmail.app/console/

    # Admins: Robert Deringer, Paul Ingham
    # robert.deringer@aberdeenplc.com
    TEST_MAIL_API_KEY = "9d8b4551-258d-4ed1-abbf-e9ce004cf007"
    TEST_MAIL_NAMESPACE = "7eyli"

    def getEmails(self, params: dict):
        session = requests.Session()

        params.update({
            "apikey": TestEMailRequests.TEST_MAIL_API_KEY,
            "namespace": TestEMailRequests.TEST_MAIL_NAMESPACE
        })

        response = session.request("GET", TestEMailRequests.TEST_MAIL_URL, params=params, verify=False)
        responseObj = json.loads(response.text, object_hook=lambda d: SimpleNamespace(**d))

        PrintMessage(f"TestMailRequests > getEmails > Request state: {responseObj.result}")

        if responseObj.count > 0:
            return responseObj.emails[0]
        return None

    def getMostRecentEmail(self, tag):
        params = {"tag": tag}
        return self.getEmails(params)

    @retry(exceptions=(APIException, AttributeError), delay=5, tries=24)
    def getEmailReceivedFromTimeStamp(self, tag, timestampMilliseconds):
        PrintMessage(f"Test Email Requests > waiting for email to arrive on/after timestamp: {timestampMilliseconds}")
        params = {"tag": tag, "timestamp_from": int(timestampMilliseconds)}
        email = self.getEmails(params)

        if email is None:
            raise APIException("Email not yet arrived")
        return email


if __name__ == "__main__":
    from time import time
    obj = TestEMailRequests()
    emails1 = obj.getMostRecentEmail("tc1476011")
    print(emails1.subject)

    emails2 = obj.getEmailReceivedFromTimeStamp("tc1476011", time() * 1000)
    print(emails2)
