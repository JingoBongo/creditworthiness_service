import __init__
import json

import requests
from utils import constants as c
from utils import db_utils


# TODO: what headers do we want/need?


# TODO add to config ability to lock sending requests to other sites or even fuses

# TODO probably add conversion from xml/other stuff into json  (low priority)

# TODO I need response type headers. maybe even as a wrapper-decorator thingy. I NEED IT
# ::: for this task I saw Flask can return 'Response(xml, mimetype='text/xml')', meaning we just specify response type in
# ::: header and wrap return of inner function with Response(response, mimetype='decorator_content_type')

# TODO. Think about authorization. like seriously tho (low priority)

# TODO. make decorator that will count times an endpoint was used for statistics and possible anti-DOS functionality
# in DOS scenario, somehow I want hide-in-shell scenario, when fuse can be re-opened through secured connection only


def check_context(context: str):
    if context:
        if (not isinstance(context, str)) or \
                ('=' in context or not context.startswith('/') or (len(context) > 1 and context.endswith('/'))):
            return True
    return False


def handle_string_as_file_path(data, claimed_data_type):
    arg_name = 'files'
    remade_data = {'file': open(data, 'rb')}
    confirmed_data_type = claimed_data_type
    return arg_name, confirmed_data_type, remade_data


def handle_string_as_file_content(data, claimed_data_type, detected_data_type_category):
    arg_name = 'files'
    ext = detected_data_type_category[claimed_data_type['Content-Type']].split('/')[-1]
    confirmed_data_type = claimed_data_type
    remade_data = {'file': (f"data.{ext}", data)}
    return arg_name, confirmed_data_type, remade_data


def handle_not_string_but_file(data, claimed_data_type):
    arg_name = 'files'
    remade_data = {'file': data}
    confirmed_data_type = claimed_data_type
    return arg_name, confirmed_data_type, remade_data


def recognize_data_type(data, claimed_data_type) -> ('arg_name', 'confirmed_data_type', 'remade_data'):
    arg_name = None
    confirmed_data_type = None
    remade_data = None
    content_type_json_kv_pair = {'Content-Type': 'application/json'}

    # so, if we get a dict, try to treat is as json; or at least if we get a str and claimed data type is json.
    if isinstance(data, dict):
        arg_name = 'json'
        confirmed_data_type = content_type_json_kv_pair
        remade_data = data
        return arg_name, confirmed_data_type, remade_data
    elif claimed_data_type == content_type_json_kv_pair and isinstance(data, str):
        arg_name = 'json'
        confirmed_data_type = content_type_json_kv_pair
        try:
            remade_data = json.loads(data)
        except:
            remade_data = {'content': data}
        return arg_name, confirmed_data_type, remade_data

    # return just string if there is no claimed type
    if not claimed_data_type and isinstance(data, str):
        arg_name = 'json'
        confirmed_data_type = {'Content-Type': 'text/string'}
        remade_data = data
        return arg_name, confirmed_data_type, remade_data

    # if we get a string + claimed data type, we check depending on claimed data type;

    # text section
    # code file section
    # not sure about c libs tho
    if c.text_data_types.get(claimed_data_type['Content-Type'], None) is not None:
        if isinstance(data, str):
            if '.' in data:
                return handle_string_as_file_path(data, claimed_data_type)
            else:
                return handle_string_as_file_content(data, claimed_data_type, c.text_data_types)
        else:
            return handle_not_string_but_file(data, claimed_data_type)

    if c.mm_data_types.get(claimed_data_type['Content-Type'], None) is not None:
        if isinstance(data, str):
            if '.' in data:
                return handle_string_as_file_path(data, claimed_data_type)
            else:
                return handle_string_as_file_content(data, claimed_data_type, c.mm_data_types)
        else:
            return handle_not_string_but_file(data, claimed_data_type)

    if c.application_data_types.get(claimed_data_type['Content-Type'], None) is not None:
        if isinstance(data, str):
            if '.' in data:
                return handle_string_as_file_path(data, claimed_data_type)
            else:
                return handle_string_as_file_content(data, claimed_data_type, c.application_data_types)
        else:
            return handle_not_string_but_file(data, claimed_data_type)

    # if we get array of bytes, lets treat as a file, shall we?
    arg_name = 'files'
    remade_data = {'file': data}
    confirmed_data_type = {'Content-Type': 'unknown'}
    return arg_name, confirmed_data_type, remade_data


# this is a lower level function called from init_send_request
def send_request(url: str, context=None, request_type='GET', headers=None, data=None, params=None, cookies=None,
                 claimed_data_type=None):
    # TODO: this was planned to be a lower leve requests caller, so in case variable checks here duplicate checks from the above method in the
    # end, remove them

    # we need to prepare data somehow. let's say get MUST HAVE headers, make sure we have cookie session or whatever
    # TODO: how to authenticate in other fuses?

    # TODO: if we send a file, try to send it in chunks? So, if data is a string and is a path, send a file
    # files = {'file': open('report.xls', 'rb')}
    # r = requests.post(url, files=files)
    # OR
    # files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}
    # we can avoid creating a file, but passing a string and filename instead

    # some good info about cookies: https://requests.readthedocs.io/en/latest/user/quickstart/

    # SESSION OBJECTS (cookies) will help track user and return him only tasks he needs
    # https://requests.readthedocs.io/en/latest/user/advanced/#advanced
    # TODO: this means fuse will give session cookies to whoever requests it and check session cookie later

    url = str(url)
    # prepare request type
    if request_type not in c.supported_request_types:
        raise Exception(f"Incorrect request method used: {request_type}")
    # prepare params
    # method that will choose url should also treat context. here we just check it is a dict
    if params and not isinstance(params, dict):
        raise Exception(f"Params should be a dict: {params}")

    # prepare context... if we find equals there we assume previous method of getting params out of there made an oopsie
    # also context should start with / and not finish with it
    if check_context(context):
        raise Exception(f"Incorrect context used: {context}")

    if request_type == c.request_type_post or request_type == c.request_type_patch or request_type == c.request_type_put:
        kwarg_name, confirmed_data_type, remade_data = recognize_data_type(data, claimed_data_type)
        headers.update(confirmed_data_type)
        resp: requests.Response = requests.request(request_type, **{kwarg_name: remade_data}, url=url + context,
                                                   params=params, cookies=cookies)

    else:
        kwarg_name, confirmed_data_type, remade_data = None, None, None
        resp: requests.Response = requests.request(request_type, url=url + context,
                                                   params=params, cookies=cookies)
    resp.raise_for_status()
    return resp


def local_fuse_has_needed_service(service: str):
    rows1 = db_utils.select_from_table_by_one_column(c.sys_services_table_name, 'name', service, 'String')
    rows2 = db_utils.select_from_table_by_one_column(c.business_services_table_name, 'name', service, 'String')
    rows1.extend(rows2)
    if len(rows1) >= 1:
        return rows1
    return False


def provide_url_from_service(service: str):
    if not service or not isinstance(service, str):
        raise Exception(f"Service variable should be a str, but got {service} : {type(service)}")
    # url 'always' has dot, fuse service/node is a name, supposedly without '/' etc
    if '.' in service:  # we assume that it is an url. We will also try to clean the url
        if not service.startswith('http'):  # thing is, we can try to add http, and proper servers will try
            service = "http://" + service  # to redirect http requests to https automatically
        return service
    else:  # it should be a fuse node name then, first try to find it locally then try to address other fuses
        # TODO: after multi-instanced services are implemented, add load balanced
        if services_from_db := local_fuse_has_needed_service(service):  # return False OR list of acceptable services
            # address to local + load banalnce
            if len(services_from_db) > 1:  # need to load balance
                raise Exception('Implement me')
            # so if locally such service exists, return localhost + port
            # TODO: [FFD-35] https for fuse
            port = services_from_db[0]['port']
            return f"http://localhost:{port}"
        # the only case left is the one where local fuse needs to call foreign fuse
        raise Exception("Implement me")


def get_params_from_context_after_question_mark(raw_string: str):
    return [{s.split('=')[0]: s.split('=')[1]} for s in raw_string.split('&')]


def cleanup_context(context: str):
    if not context or not isinstance(context, str):
        return '/'
    if not context.startswith('/'):  # we can try to just add it
        context = '/' + context
    #  it appears that here I actually check length of correct context.
    #  I really want to re-ask myself and my thought process while writing this code
    if len(context.split('?')[0]) > 1 and context.split('?')[0].endswith('/'):
        # we can try to just remove '/' in the end of context if unneeded slash exists
        context = context.replace(context.split('?')[0], context.split('?')[0][:-1])
        # this way we do no accidentally touch parameters
    if '?' in context:  # everything before is a context, everything after ARE params
        context, raw_string_of_params = context.split('?')
        # it will probably fail if we have more than 1 '?' which is totally fine with me
        params = get_params_from_context_after_question_mark(raw_string_of_params)
        return context, params
    return context, None


def cleanup_request_type(request_type: str):
    if not request_type or not isinstance(request_type, str):
        raise Exception(f"Invalid request type variable")
    if request_type.upper() not in c.supported_request_types:
        raise Exception(f"Incorrect request method used: {request_type}")
    return request_type.upper()


def prepare_headers(headers):
    if headers and not isinstance(headers, dict):
        raise Exception(f"Headers should be a dict: {headers}")
    return headers


def prepare_parameters(params, possible_params):
    # there are a lot of ifs here BECAUSE we cannot use update() if any of vars is None
    if not params and not possible_params:
        return None
    if params and not isinstance(params, dict):
        raise Exception(f"Params variable should be a dict, but got {type(params)}")
    if possible_params and not isinstance(possible_params, dict):
        raise Exception(f"Possible params variable should be a dict, but got {type(possible_params)}")
    if params and not possible_params:
        return params
    if not params and possible_params:
        return possible_params
    params.update(possible_params)
    return params


def prepare_cookies(cookies):
    # once again, i want None cookies to be accepted
    if cookies and not isinstance(cookies, dict):
        raise Exception(
            f"Cookies variables should be a dict, but got {type(cookies)}")  # I hope this line itself doesnt fall
    return cookies


# this should be a method that anyone uses
def init_send_request(service, context=None, request_type='GET', headers=None, data=None, params=None, cookies=None,
                      claimed_data_type=None):
    # first, check if url is for local, other fuse or just a url
    url = provide_url_from_service(service)
    context, possible_params = cleanup_context(context)
    request_type = cleanup_request_type(request_type)
    headers = prepare_headers(headers)
    # data should be prepared in a lower level function. why? here we have init checks, only after them data can be properly processed
    params = prepare_parameters(params, possible_params)
    cookies = prepare_cookies(cookies)

    return send_request(url=url, context=context, request_type=request_type, headers=headers, data=data, params=params,
                        cookies=cookies, claimed_data_type=claimed_data_type)
