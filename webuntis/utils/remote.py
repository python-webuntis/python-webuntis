"""
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
"""
from webuntis import errors
from webuntis.utils import log
from webuntis.utils.userinput import unicode_string, bytestring
from webuntis.utils.third_party import json

import datetime
import requests

_errorcodes = {
    -32601: errors.MethodNotFoundError,
    -8504: errors.BadCredentialsError,
    -8520: errors.NotLoggedInError,
    -7004: errors.DateNotAllowed,
    -8507: errors.DateNotAllowed,
}
'''The API-errorcodes python-webuntis is able to interpret, together with the
exception that will be thrown.'''


def rpc_request(config, method, params):
    """
    A method for sending a JSON-RPC request.

    :param config: A dictionary containing ``useragent``, ``server``,
        ``school``, ``username`` and ``password``
    :type config: dict or FilterDict

    :param method: The JSON-RPC method to be executed
    :type method: str

    :param params: JSON-RPC parameters to the method (should be JSON
        serializable)
    :type params: dict
    """
    server = config['server']
    school = config['school']
    useragent = config['useragent']

    assert isinstance(method, unicode_string)
    assert isinstance(server, unicode_string)
    assert isinstance(school, unicode_string)
    assert isinstance(useragent, unicode_string)

    for v in params.values():
        assert not isinstance(v, bytestring)

    url = server + u'?school=' + school

    headers = {
        u'User-Agent': useragent,
        u'Content-Type': u'application/json'
    }

    request_body = {
        u'id': _request_getid(),
        u'method': method,
        u'params': params,
        u'jsonrpc': u'2.0'
    }

    if method != u'authenticate':
        if 'jsessionid' in config:
            assert isinstance(config['jsessionid'], unicode_string)
            headers['Cookie'] = u'JSESSIONID=' + config['jsessionid']
        else:
            raise errors.NotLoggedInError(
                'Don\'t have JSESSIONID. Did you already log out?')

    log('debug', 'Making new request:')
    log('debug', 'URL: ' + url)
    if method != u'authenticate':
        # user credentials will not be logged - fixing #14
        log('debug', 'DATA: ' + str(request_body))

    if '_http_session' not in config:
        config['_http_session'] = requests.session()
    http_session = config['_http_session']

    result_body = _send_request(
        url,
        request_body,
        headers,
        http_session
    )
    return _parse_result(request_body, result_body)


def _request_getid():
    """
    calculate the id field for the request -- use current date

    If you want to get a fixed id for tests:
       import webuntis.utils.remote
       webuntis.utils.remote._request_getid = lambda: "12345678910"

    :return: id field for request
    :rtype: str
    """
    return str(datetime.datetime.today())


def _parse_result(request_body, result_body):
    """A subfunction of rpc_request, that, given the decoded JSON result,
    handles the error codes or, if everything went well, returns the result
    attribute of it. The request data has to be given too for logging and
    ID validation.

    :param request_body: The not-yet-encoded body of the request sent.
    :param result_body: The decoded body of the result received.
    """

    if request_body[u'id'] != result_body[u'id']:
        raise errors.RemoteError(
            'Request ID was not the same one as returned. %s -- %s' % (request_body[u'id'], result_body[u'id']))

    try:
        return result_body[u'result']
    except KeyError:
        _parse_error_code(request_body, result_body)


def _parse_error_code(request_body, result_body):
    """A helper function for handling JSON error codes."""
    log('error', result_body)
    try:
        error = result_body[u'error']
        code, message = error[u'code'], error[u'message']
    except KeyError:
        code = None  # None doesn't exist in_errorcodes
        message = ('Some error happened and there is no information provided '
                   'what went wrong.')

    exc = _errorcodes.get(code, errors.RemoteError)(message)
    exc.request = request_body
    exc.result = result_body
    exc.code = code
    raise exc


def _send_request(url, data, headers, http_session=None):
    """Sends a POST request given the endpoint URL, JSON-encodable data,
    a dictionary with headers and, optionally, a session object for requests.
    """

    if http_session is None:
        http_session = requests.session()

    r = http_session.post(url, data=json.dumps(data), headers=headers)
    result = r.text
    # this will eventually raise errors, e.g. on timeout

    try:
        result_data = json.loads(result, )
        log('debug', 'Valid JSON found')
        log('debug', '  Got data' + str(result)[:100])
    except ValueError:
        raise errors.RemoteError('Invalid JSON', result)
    else:
        return result_data
