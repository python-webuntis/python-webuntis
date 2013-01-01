'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals
from webuntis import errors
from webuntis.utils import log
from webuntis.utils.third_party import json, urlrequest

import datetime


_errorcodes = {
    -32601: errors.MethodNotFoundError,
    -8504: errors.BadCredentialsError,
    -8520: errors.NotLoggedInError
}
'''The API-errorcodes python-webuntis is able to interpret, together with the
exception that will be thrown.'''


def rpc_request(config, method, params):
    '''
    A method for sending a JSON-RPC request.

    :param config: A dictionary containing ``useragent``, ``server``,
        ``school``, ``username`` and ``password``
    :type config: dict

    :param method: The JSON-RPC method to be executed
    :type method: str

    :param params: JSON-RPC parameters to the method (should be JSON
        serializable)
    :type params: dict
    '''

    url = config['server'] + \
        '?school=' + \
        config['school']

    headers = {
        'User-Agent': config['useragent'],
        'Content-Type': 'application/json'
    }

    request_body = {
        'id': str(datetime.datetime.today()),
        'method': method,
        'params': params,
        'jsonrpc': '2.0'
    }

    if method != 'authenticate':
        if 'jsessionid' not in config:
            raise errors.NotLoggedInError(
                'Don\'t have JSESSIONID. Did you already log out?')
        else:
            headers['Cookie'] = 'JSESSIONID=' + \
                config['jsessionid']

    log('debug', 'Making new request:')
    log('debug', 'URL: ' + url)
    log('debug', 'DATA: ' + str(request_body))

    result_body = _send_request(
        url,
        request_body,
        headers
    )
    return _parse_result(request_body, result_body)


def _parse_result(request_body, result_body):
    '''A subfunction of request, that, given the decoded JSON result,
    handles the error codes or, if everything went well, returns the result
    attribute of it. The request data has to be given too for logging and
    ID validation.

    :param request_body: The not-yet-encoded body of the request sent.
    :param result_body: The decoded body of the result recieved.
    '''

    if request_body['id'] != result_body['id']:
        raise errors.RemoteError(
            'Request ID was not the same one as returned.')

    try:
        return result_body['result']
    except KeyError:
        _parse_error_code(request_body, result_body)


def _parse_error_code(request_body, result_body):
    '''A helper function for handling JSON error codes.'''
    log('error', result_body)
    try:
        error = result_body['error']
        exc = _errorcodes[error['code']](error['message'])
    except KeyError:
        exc = errors.RemoteError(
            ('Some JSON-RPC-ish error happened. Please report this to the '
                'developer so he can implement a proper handling.'),
            str(result_body),
            str(request_body)
        )

    raise exc


def _send_request(url, data, headers):
    '''Sends a POST request given the endpoint URL, JSON-encodable data and
    a dictionary with headers.
    '''

    request = urlrequest.Request(url, json.dumps(data).encode(), headers)
    # this will eventually raise errors, e.g. if there's an unexpected http
    # status code
    result_obj = urlrequest.urlopen(request)
    result = result_obj.read().decode('utf-8')

    try:
        result_data = json.loads(result)
        log('debug', 'Valid JSON found')
    except ValueError:
        raise errors.RemoteError('Invalid JSON', str(result))
    else:
        return result_data
