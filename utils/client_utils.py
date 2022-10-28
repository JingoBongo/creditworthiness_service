import json

from sqlalchemy import true

import __init__
import requests
from utils import constants as c
from utils import db_utils


# functions to send post and get requests

# what to add about this util?
# it must decide to call local service or other one
# so if request leads to outside thing, we simply send request and hope that we can process the response
# note to check: only process if it is json one? put other stuff in json key?

# if request leads to inside thing, then find appropriate service/port. Method that does it while load balancing <- for later, when many
# service instances will be active

# then, call, collect results.... appropriate things will process them

# TODO: what headers do we want? for now: none probably


# so far service will be localhost/other fure/ other ulr. How to properly name it?
# let's try this: if it has a DOT, www, http or https it is a foreign webpage

# TODO, add retry mechanism or is it already there?
# TODO also check properly, and PROCESS properly different response types.
# TODO add to config ability to lock sending requests to other sites or even fuses
# TODO finally make DYNAMIC config info
# TODO probably not just get/post to do. other stuff too
# TODO probably add conversion from xml/other stuff into json
# TODO probably conversion herer or in separate utils
# TODO what headers?.. do we need them in steps????????????
# TODO I need response type headers. maybe even as a wrapper-decorator thingy. I NEED IT

# TODO. Think about authorization. like seriously tho

# TODO. make decorator that will count times an endpoint was used for statistics and possible anti-DOS functionality
# in DOS scenario, somehow I want hide-in-shell scenario, when fuse can be re-opened through secured connection only

# TODO auto code checks
# TODO ability to async task

# TODO in taskmaster. sometimes context might have VARIABLES inside. say if we use parameters. catch them.!!!

# "service": "db_endpoint",   <- we have services tables to check if local exists. we will implement search in other fuses later
# "route": "/clear/Harvested_Routes", <- context, necessary for request
# "request_type": "GET", <- request type
# "requires" : [],       <- what variables we will try to put into json
# headers???? in task file??? some default for fuse?
def check_context(context):
    if context:
        if not isinstance(context, str):
            return True
        elif '=' in context or not context.startswith('/') or (len(context) > 1 and context.endswith('/')):
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

    # TODO, I hate to save these in the code, in future make it some config fileS(not only for text) or whatever

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


def send_request(url, context=None, request_type='GET', headers=None, data=None, params=None, cookies=None,
                 claimed_data_type=None):
    # TODO: this was planned to be a lower leve requests caller, so in case variable checks here duplicate checks from the above method in the 
    # end, remove them

    # we need to prepare data somehow. let's say get MUST HAVE headers, make sure we have cookie session or whatever
    # TODO: how to authenticate in other fuses?

    # TODO: if our data is dict, try to send it as json?

    # TODO: if we send a file, try to send it in chunks? So, if data is a string and is a path, send a file
    # files = {'file': open('report.xls', 'rb')}
    # r = requests.post(url, files=files)
    # OR
    # files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}
    # we can avoid creating a file, but passing a string and filename instead

    # r.status_code == requests.codes.ok
    # True
    # we can use requests's check for ok status codes, neet

    # or try bad_r.raise_for_status() just to catch it automatically
    #
    # some good info about cookies: https://requests.readthedocs.io/en/latest/user/quickstart/

    # SESSION OBJECTS (cookies) will help track user and return him only tasks he needs
    # https://requests.readthedocs.io/en/latest/user/advanced/#advanced
    # TODO: this means fuse will give session cookies to whoever requests it and check session cookie later

    # prepare url. this method will be a low level one, meaning the one above should take care about how to get url
    # if method gets wrong url it is fault of upper method.
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

    # prepare data. now then. I want data-type header
    # thing is. there are so many data types that trying to handle them all here is dumb. let user specify this and make json default
    # However, if it contains 'audio', 'video', 'image' treat it as a file
    # If it is a text, try to treat string as a new file with specific .extension
    # if it application

    # wait. can we treat any data type user provides and try to send a file?
    if request_type == c.request_type_post or request_type == c.request_type_patch or request_type == c.request_type_put:
        kwarg_name, confirmed_data_type, remade_data = recognize_data_type(data, claimed_data_type)
        headers.update(confirmed_data_type)
        resp: requests.Response = requests.request(request_type, **{kwarg_name: remade_data}, url=url + context,
                                                   params=params, cookies=cookies)

    else:
        kwarg_name, confirmed_data_type, remade_data = None, None, None
        resp: requests.Response = requests.request(request_type, url=url + context,
                                                   params=params, cookies=cookies)
    # confirmed data type is a header that we want to send as well

    # prepare headers. if there would be any additional headers we always want to use: this is the place for it
    # for now check if is dict

    # TODO: authentication can be specifically defined in a call; figure it out

    resp.raise_for_status()
    return resp


def local_fuse_has_needed_service(service):
    rows1 = db_utils.select_from_table_by_one_column(c.sys_services_table_name, 'name', service, 'String')
    rows2 = db_utils.select_from_table_by_one_column(c.business_services_table_name, 'name', service, 'String')
    rows1.extend(rows2)
    if len(rows1) >= 1:
        return rows1
    return False


def provide_url_from_service(service):
    if not service or not isinstance(service, str):
        raise Exception(f"Service variable should be a str, but got {service} : {type(service)}")
    # url always has dot, fuse service/node is a name, supposedly without '/' etc
    # TODO: make this a regex check probably
    if '.' in service:  # we assume that it is an url. We will also try to clean the url
        if not service.startswith('http'):  # thing is, we can try to add http, and proper servers will try
            service = "http://" + service  # redirect http requests to https automatically
        return service
    else:  # it should be a fuse node name then, first try to find it locally then try to address other fuses
        # also remember about load balancing
        # without '.' means it is a fuse node
        if services_from_db := local_fuse_has_needed_service(service):
            # address to local + load banalnce
            if len(services_from_db) > 1:  # need to load balance
                raise Exception('Implement me')
            # so if locally such service exists, return localhost + port
            # TODO: [FFD-35] https for fuse
            port = services_from_db[0]['port']
            return f"http://localhost:{port}"


def get_params_from_context_after_question_mark(raw_string):
    return [{s.split['='][0]: s.split['='][1]} for s in raw_string.split('&')]


def cleanup_context(context):
    if not context or not isinstance(context, str):
        return '/'
    if not context.startswith('/'):  # we can try to just add it
        context = '/' + context
    #  it appears that here I actually check length of correct context.
    #  I really want to re-ask myself and my thoughtprocess while writing this code
    if len(context.split('?')[0]) > 1 and context.split('?')[0].endswith(
            '/'):  # we can try to just remove '/' in the end of context
        context = context.replace(context.split('?')[0],
                                  context.split('?')[0][:-1])  # this way we do no accidentally touch parameters
    if '?' in context:  # everything before is a context, everything after ARE params
        context, raw_string_of_params = context.split[
            '?']  # it will probably fail if we have more than 1 '?' which is totally fine with me
        params = get_params_from_context_after_question_mark(raw_string_of_params)
        return context, params
    return context, None


def cleanup_request_type(request_type):
    if not request_type or not isinstance(request_type, str):
        raise Exception(f"Invalid request type variable")
    if not request_type.upper() in c.supported_request_types:
        raise Exception(f"Incorrect request method used: {request_type}")
    return request_type.upper()


def prepare_headers(headers):
    # TODO: when we actually will start using and working with headers, make a way to define dafault ones for fuses and other urls
    # UPD: i actually want headers sometimes to be null, so allow it
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
        # or should we just straight ignore them then?... naah. this is a section we get if user made a mistake
        # therefore no guarantee this is fulfilled properly 
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
    # TODO: Implement actual cookies that we can do if we need. do we need them when we are SENDING requests? not sure. Probably not, anyhow..
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

    # result = find_valid_route(path)
    #     if len(result)<=0:
    #         return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
    #     if len(result)>1:
    #         return {'msg': 'there are multiple matching routes, either try to avoid this during development'
    #                        'or try to pick route by service_name or function_name from result list.',
    #                         'status':'ambiguous result',
    #                         'possible resolution':'remove duplicates and re-run harvester OR pick specific result from the list'}
    #     # pick service port by service name from result from db and go by path
    #     rows1 = db_utils.select_from_table_by_one_column(c.sys_services_table_name, 'name', result[0]['service_name'], 'String')
    #     rows2 = db_utils.select_from_table_by_one_column(c.business_services_table_name, 'name', result[0]['service_name'], 'String')
    #     rows = rows2 + rows1
    #     for row in rows:
    #     #     TODO. here could be your load balancing logic or multi service handling, but here is a TODO :)
    #     #     TODO this includes selects from db as well
    #         port = row['port']
    #         new_url = f"http://localhost:{port}/{path}"
    #         something = redirect(new_url)
    #         return something
    #     # return below should be unreachable in theory, but... still
    #     return {'msg': 'no such route. You want to start harvester? (/trigger-harvester)'}
