import json

import requests
from CommonCode.TestExecute.Logging import PrintMessage, LoggingLevel
from CommonCode.TestExecute.TestContext import Test_Context
from requests import cookies


class TokenExpiredException(Exception):
    pass


class WMRequests(object):
    def __init__(self):
        self.automation_config = Test_Context.run_config.load('TestAutomation')

    def _set_identity(self, forced=False):
        if Test_Context.api_session_token and not forced:
            return

        headers = {'Content-Type': 'application/json'}
        data = {"username": Test_Context.test_user['SITE_USER'],
                "password": Test_Context.test_user['SITE_PASSWORD']}

        request_result = self._execute_request(url=self.automation_config['TOKEN_URL'],
                                               data=data,
                                               headers=headers)
        Test_Context.api_session_token = request_result['sessionToken']

    def _get_header(self):
        return {'Content-Type': 'application/json',
                'origin': self.automation_config['ORIGIN_URL']}

    def _get_cookies(self, forced=False):
        self._set_identity(forced=forced)
        cookie = requests.cookies.RequestsCookieJar()
        cookie.set(name='iPlanetDirectoryPro',
                   value=Test_Context.api_session_token,
                   domain='company.com')

        return cookie

    @staticmethod
    def _handle_error(response):
        PrintMessage("API non-200 response, reason: {0}".format(response.text))

        error_content = json.loads(response.content)

        if not isinstance(error_content, list):
            error_content = [error_content]

        for error in error_content:
            if 'error' in error and error['error'] == 'Session expired':
                raise TokenExpiredException()

    def _execute_request(self, url, data, headers, request_cookies=None):
        json_data = json.dumps(data)
        PrintMessage("Sending request to URL: {0}".format(url))
        PrintMessage("Request data: \n{0}\n".format(json_data), LoggingLevel.debug)

        #  trust_env works around issue with proxy in windows
        #  so far it does not have any negative impact on vagrant test execution
        #  https://stackoverflow.com/questions/28521535/requests-how-to-disable-bypass-proxy
        session = requests.Session()
        session.trust_env = False
        response = session.post(url=url, data=json_data, headers=headers, cookies=request_cookies)

        if response.status_code != 200:
            self._handle_error(response)

        response_data = response.json()
        PrintMessage("Request response data: \n{0}\n".format(response_data), LoggingLevel.debug)

        return response_data

    def post(self, url, data):
        full_url = self.automation_config['API_URL'] + url
        headers = self._get_header()
        request_cookies = self._get_cookies()

        try:
            return self._execute_request(url=full_url, data=data, headers=headers, request_cookies=request_cookies)
        except TokenExpiredException:
            #  We potentially have an expired token situation
            #  Re-set auth token
            request_cookies = self._get_cookies(forced=True)
            return self._execute_request(url=full_url, data=data, headers=headers, request_cookies=request_cookies)
