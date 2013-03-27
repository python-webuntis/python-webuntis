import mock
import webuntis
from webuntis.tests import WebUntisTestCase, stub_session_parameters, \
        mock_results

class BasicUsage(WebUntisTestCase):
    def test_login_repeat_not_logged_in(self):
        s = webuntis.Session(**stub_session_parameters)
        retry_amount = 5
        calls = []

        expected_calls = (
            ['getCurrentSchoolyear', 'logout', 'authenticate']
            * (retry_amount + 1)
        )[:-2]

        def authenticate(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
            }

        def getCurrentSchoolyear(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'error': {'code': -8520, 'message': 'Not logged in!'}
            }

        def logout(url, jsondata, headers):
            calls.append(jsondata['method'])
            return {
                'result': {'bla': 'blub'}  # shouldn't matter
            }
        methods = {
            'authenticate': authenticate,
            'getCurrentSchoolyear': getCurrentSchoolyear,
            'logout': logout
        }

        with mock_results(methods):
            with mock.patch.dict(
                s.config,
                {'login_repeat': retry_amount}
            ):
                self.assertRaises(webuntis.errors.NotLoggedInError,
                                  s._request,
                                  'getCurrentSchoolyear')

        self.assertEqual(calls, expected_calls)

    def test_logout_not_logged_in(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']

        s = webuntis.Session(**session_params)

        self.assertRaises(webuntis.errors.NotLoggedInError, s.logout)
        s.logout(suppress_errors=True)

    def test_login_no_creds(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']
        del session_params['username']
        del session_params['password']

        s = webuntis.Session(**session_params)
        self.assertRaises(webuntis.errors.AuthError, s.login)

    def test_login_successful(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']

        s = webuntis.Session(**session_params)

        with mock.patch(
            'webuntis.Session._request',
            return_value={'sessionId': '123456'}
        ) as mock_obj:
            s.login()
            self.assertEqual(s.config['jsessionid'], '123456')
            self.assertEqual(mock_obj.call_count, 1)

    def test_login_no_response(self):
        session_params = dict(stub_session_parameters)
        del session_params['jsessionid']

        s = webuntis.Session(**session_params)

        with mock.patch(
            'webuntis.Session._request',
            return_value={}
        ) as mock_obj:
            self.assertRaises(webuntis.errors.AuthError, s.login)
