import __init__
import json

import requests
from utils import constants as c
from utils import db_utils


# TODO: what headers do we want/need?

# TODO add to config ability to lock sending requests to other sites or even
# fuses

# TODO probably add conversion from xml/other stuff into json  (low priority)

# TODO I need response type headers. maybe even as a wrapper-decorator thingy.
# I NEED IT
# ::: for this task I saw Flask can return 'Response(xml, mimetype='text/xml')',
# meaning we just specify response type in
# ::: header and wrap return of inner function with
# Response(response, mimetype='decorator_content_type')

# TODO. Think about authorization. like seriously tho (low priority)

# TODO. make decorator that will count times an endpoint was used for 
# statistics and possible anti-DOS functionality
# in DOS scenario, somehow I want hide-in-shell scenario, when fuse can be 
# re-opened through secured connection only


def check_context(context: str):
    """check context to be valid via verification series like checking if there is 
    no '=' sign and that it starts with '/', not ends with it
    """
    if context:
        if (not isinstance(context, str)) or \
                ('=' in context or
                 not context.startswith('/') or
                 (len(context) > 1 and context.endswith('/'))):
            return True
    return False


def handle_string_as_file_path(data: str, claimed_data_type):
    """given data is considered as a path to file, therefore, read given file and
    return back arg name, found data type and file content
    """
    arg_name = 'files'
    remade_data = {'file': open(data, 'rb')}
    confirmed_data_type = claimed_data_type
    return arg_name, confirmed_data_type, remade_data


def handle_string_as_file_content(data: str, claimed_data_type, detected_data_type_category):
    """considering that given data is a file content, extract detected data type category,
    then give back arg name, found data type and adapted data
    """
    arg_name = 'files'
    ext = detected_data_type_category[claimed_data_type['Content-Type']].split('/')[-1]
    confirmed_data_type = claimed_data_type
    remade_data = {'file': (f"data.{ext}", data)}
    return arg_name, confirmed_data_type, remade_data


def handle_not_string_but_file(data, claimed_data_type):
    """consider that given data is a file itself (binary format), then adapt it,
    and return arg name, claimed data type and adapted file data
    """
    arg_name = 'files'
    remade_data = {'file': data}
    confirmed_data_type = claimed_data_type
    return arg_name, confirmed_data_type, remade_data


def recognize_data_type(data, claimed_data_type) -> ('arg_name', 'confirmed_data_type', 'remade_data'):
    """check data type and return adapted version of the given data
    """
    arg_name = None
    confirmed_data_type = None
    remade_data = None
    content_type_json_kv_pair = {'Content-Type': 'application/json'}

    #   if given data is a dict or string with specification of JSON data type - try to process as JSON
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

    #   if no data type provided, then process just as a string text
    if not claimed_data_type and isinstance(data, str):
        arg_name = 'json'
        confirmed_data_type = {'Content-Type': 'text/string'}
        remade_data = data
        return arg_name, confirmed_data_type, remade_data

    #   if data is given as string and data type is given - check claimed data type

    # text section
    # code file section
    # not sure about c libs tho
    #   check if given data type is text related
    if c.text_data_types.get(claimed_data_type['Content-Type'], None) is not None:
        if isinstance(data, str):
            if '.' in data:
                return handle_string_as_file_path(data, claimed_data_type)
            else:
                return handle_string_as_file_content(data, claimed_data_type, c.text_data_types)
        else:
            return handle_not_string_but_file(data, claimed_data_type)

    #   check if given data type is multimedia related
    if c.mm_data_types.get(claimed_data_type['Content-Type'], None) is not None:
        if isinstance(data, str):
            if '.' in data:
                return handle_string_as_file_path(data, claimed_data_type)
            else:
                return handle_string_as_file_content(data, claimed_data_type, c.mm_data_types)
        else:
            return handle_not_string_but_file(data, claimed_data_type)

    #   check if given data type is application related
    if c.application_data_types.get(claimed_data_type['Content-Type'], None) is not None:
        if isinstance(data, str):
            if '.' in data:
                return handle_string_as_file_path(data, claimed_data_type)
            else:
                return handle_string_as_file_content(data, claimed_data_type, c.application_data_types)
        else:
            return handle_not_string_but_file(data, claimed_data_type)

    #   if as data was given array of bytes, process a binary of a file
    arg_name = 'files'
    remade_data = {'file': data}
    confirmed_data_type = {'Content-Type': 'unknown'}
    return arg_name, confirmed_data_type, remade_data


# this is a lower level function called from init_send_request
def send_request(url: str, context=None, request_type='GET', headers=None, data=None, params=None, cookies=None,
                 claimed_data_type=None):
    # TODO: this was planned to be a lower leve requests caller, so in case
    # variable checks here duplicate checks from the above method in the
    # end, remove them

    # we need to prepare data somehow. let's say get MUST HAVE headers, make
    # sure we have cookie session or whatever
    # TODO: how to authenticate in other fuses?

    # TODO: if we send a file, try to send it in chunks? So, if data is a
    # string and is a path, send a file
    # files = {'file': open('report.xls', 'rb')}
    # r = requests.post(url, files=files)
    # OR
    # files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}
    # we can avoid creating a file, but passing a string and filename instead

    # some good info about cookies: 
    # https://requests.readthedocs.io/en/latest/user/quickstart/

    # SESSION OBJECTS (cookies) will help track user and return him only 
    # tasks he needs
    # https://requests.readthedocs.io/en/latest/user/advanced/#advanced
    # TODO: this means fuse will give session cookies to whoever requests 
    # it and check session cookie later

    url = str(url)
    
    #   make sure that request type is one of the supported
    if request_type not in c.supported_request_types:
        raise Exception(f"Incorrect request method used: {request_type}")
    
    #   make sure that parameteres are given in a dict form
    if params and not isinstance(params, dict):
        raise Exception(f"Params should be a dict: {params}")
    
    #   make sure context is right as expected and there are no troubles
    if check_context(context):
        raise Exception(f"Incorrect context used: {context}")

    #   make sure request type is one of the POST, PATCH and PUT type
    # in this case we need to put the remade data
    if request_type in (c.request_type_post, c.request_type_patch, 
                        c.request_type_put):
        # if request_type == c.request_type_post or \
        #         request_type == c.request_type_patch or \
        #         request_type == c.request_type_put:
        kwarg_name, confirmed_data_type, remade_data = recognize_data_type(
            data, claimed_data_type
        )
        headers.update(confirmed_data_type)
        resp: requests.Response = requests.request(
            request_type, **{kwarg_name: remade_data},
            url=url + context, params=params,
            cookies=cookies
        )

    else:
        resp: requests.Response = requests.request(
            request_type, url=url + context, params=params, 
            cookies=cookies
        )
    resp.raise_for_status()
    return resp


def local_fuse_has_needed_service(service: str):
    """check if Fuse has service with a given name, returns
    service data if one was found and False if nothing. In
    case if there are many instances of the same service,
    give all of them for further load balancing
    """
    rows1 = db_utils.select_from_table_by_one_column(
        c.sys_services_table_name, 'name', service, 'String'
    )
    rows2 = db_utils.select_from_table_by_one_column(
        c.business_services_table_name, 'name', service, 'String'
    )
    rows1.extend(rows2)
    if len(rows1) >= 1:
        return rows1
    return False


def provide_url_from_service(service: str):
    """Try to find specified service and return address of found one.
    Also should check remote Fuse instances to find required service,
    in this case will be given a remote URL
    """
    if not service or not isinstance(service, str):
        raise Exception(f"Service variable should be a str, but got \
                        {service} : {type(service)}")

    #   URL "always" has dot, Fuse service is a name, without '/', etc
    #   we assume that given string is an URL. Therefore, try to clean the URL,
    # fix incorrect beginning of the URL if there is one. Further it's possible
    # to make https connection redirection
    if '.' in service:
        if not service.startswith('http'):
            service = "http://" + service
        return service

    #   if there is no URL pattern found, then it's a Fuse node. So, try to
    # find it locally, then try to address other fuses. If there is such
    # service locally, return localhost + port.
    #   TODO: in case of many instances of the same service it's required
    # to make load balance. In case of no service found, implement search
    # of the service on remote Fuse nodes
    else:
        if services_from_db := local_fuse_has_needed_service(service):
            if len(services_from_db) > 1:
                raise Exception('Implement Load Balance')
            # TODO: [FFD-35] https for fuse
            port = services_from_db[0]['port']
            return f"http://localhost:{port}"
        raise Exception(f"Implement me ({provide_url_from_service.__name__})")


def get_params_from_context_after_question_mark(raw_string: str):
    """return parameters written after '?' symbol in the given context
    """
    return [{s.split('=')[0]: s.split('=')[1]} for s in raw_string.split('&')]


def cleanup_context(context: str):
    #   either initialize context or fix it in case of error
    if not context or not isinstance(context, str):
        return '/'
    if not context.startswith('/'):  # we can try to just add it
        context = '/' + context

    #   check if context contains params. If there is definition 
    # of params, then separate context from params, remove
    # redundant "/" symbol in the end, extract params and then
    # give back separated fixed context and params
    if "?" in context:
        context, raw_params_string = context.split('?')
        if context.endswith("/"):
            context = context[:-1]
        params = get_params_from_context_after_question_mark(raw_params_string)
        return context, params
    return context, None
    # #   check if there is any context before '?' symbol and if this context
    # # before '?' ends with '/' symbol
    # if len(context.split('?')[0]) > 1 and context.split('?')[0].endswith('/'):
    #     #   remove in the context before "?" the final "/" symbol
    #     context = context.replace(context.split('?')[0], context.split('?')[0][:-1])

    # #   once again, all before '?' is a context, after - params
    # if '?' in context:
    #     context, raw_string_of_params = context.split('?')
    #     # it will probably fail if we have more than 1 '?' which is totally fine with me
    #     params = get_params_from_context_after_question_mark(raw_string_of_params)
    #     return context, params
    # return context, None


def cleanup_request_type(request_type: str):
    """Make sure that request type is valid
    """
    if not request_type or not isinstance(request_type, str):
        raise Exception("Invalid request type variable")
    if request_type.upper() not in c.supported_request_types:
        raise Exception(f"Incorrect request method used: {request_type}")
    return request_type.upper()


def prepare_headers(headers):
    """Maker sure headers are of dict type
    """
    if headers and not isinstance(headers, dict):
        raise Exception(f"Headers should be a dict: {headers}")
    return headers


def prepare_parameters(params, possible_params):
    #   if both params and possible params are none, then none
    if not params and not possible_params:
        return None
    #   if we have params that are not dict
    if params and not isinstance(params, dict):
        raise Exception(
            f"Params variable should be a dict, but got {type(params)}"
        )
    #   if we have possible params that are not dict
    if possible_params and not isinstance(possible_params, dict):
        raise Exception(
            f"Possible params variable should be a dict, but got \
                {type(possible_params)}"
        )
    #   if we have params but no possible params
    if params and not possible_params:
        return params
    #   if we have no params, but have possible params
    if not params and possible_params:
        return possible_params
    #   if both params and possible params are present and valid
    params.update(possible_params)
    return params


def prepare_cookies(cookies):
    """check if existing cookies are of type dict
    """
    # once again, i want None cookies to be accepted
    if cookies and not isinstance(cookies, dict):
        raise Exception(
            # I hope this line itself doesnt fall
            f"Cookies variables should be a dict, but got {type(cookies)}"
        )
    return cookies


# this should be a method that anyone uses
def init_send_request(service, context=None, request_type='GET',
                      headers=None, data=None, params=None,
                      cookies=None, claimed_data_type=None):
    """initialize send request that will be transmitted to the
    specified service or adress

    Args:
        service (expecting str): name of service where to send request
        context (expecting str, optional): additional request info.
                Defaults to None.
        request_type (str, optional): what type of request to send.
                Defaults to 'GET'.
        headers (expecting dict, optional): headers of the request.
                Defaults to None.
        data (any, optional): information that must be transmitted
                via request (like for POST request). Defaults to None.
        params (expecting dict, optional): parameters of the given
                request. Defaults to None.
        cookies (expecting dict, optional): cookies for request.
                Defaults to None.
        claimed_data_type (expecting str, optional): information
                about type of transmitted in the request data. 
                Defaults to None.

    Returns:
        _type_: _description_
    """
    #   check if URL is either for local Fuse or remote one or just URL
    url = provide_url_from_service(service)
    context, possible_params = cleanup_context(context)
    request_type = cleanup_request_type(request_type)
    headers = prepare_headers(headers)

    # data should be prepared in a lower level function. why? 
    # here we have init checks, only after them data can be 
    # properly processed
    params = prepare_parameters(params, possible_params)
    cookies = prepare_cookies(cookies)

    return send_request(url=url,
                        context=context,
                        request_type=request_type,
                        headers=headers,
                        data=data,
                        params=params,
                        cookies=cookies,
                        claimed_data_type=claimed_data_type)
