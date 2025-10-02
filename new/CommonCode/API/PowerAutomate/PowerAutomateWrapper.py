import json
import requests


class PowerAutomateWrapper:
    HEADERS = {"Content-Type": "application/json",
               "Accept": "*/*",
               "Accept-Encoding": "gzip, deflate, br"}

    powerAutomateURL: str = None

    def sendToPowerAutomateFlow(self, jsonLoad):
        assert self.powerAutomateURL, "expected URL to power automate to be set"
        with requests.session() as session:
            response = session.request("POST", self.powerAutomateURL, data=json.dumps(jsonLoad), headers=PowerAutomateWrapper.HEADERS)
            if response.status_code != 202:
                print(response.text)
