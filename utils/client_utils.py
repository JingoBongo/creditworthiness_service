import json

import __init__
import requests
from utils import constants as c


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
def checkContext(context):
    if context:
        if not isinstance(context, str):
            return True
        elif '=' in context or not context.startswith('/') or context.endswith('/'):
            return True
    return False


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
    text_data_types = {}
    # text section
    text_data_types['text/css'] = '.css'
    text_data_types['text/csv'] = '.csv'
    text_data_types['text/html'] = '.html'
    text_data_types['text/calendar'] = '.ics'
    text_data_types['text/plain'] = '.txt'
    # code file section
    text_data_types['text/javascript'] = '.js'
    text_data_types['text/python'] = '.py'
    text_data_types['text/jupyter'] = '.ipynb'
    text_data_types['text/java'] = '.java'
    text_data_types['text/c'] = '.c'
    text_data_types['text/cpp'] = '.cpp'
    # not sure about c libs tho

    if claimed_data_type['Content-Type'] in text_data_types.keys():
        if isinstance(data, str):
            if '.' in data:
                # Do I even need to check if it is in text_data_types extensions?? for now NOT CHECK and see what happens
                # if (data_type_of_string_data:= data.split('.')[-1]) in text_data_types.values():
                #                 then it must be a path to a file
                arg_name = 'files'
                remade_data = {'file': open(data, 'rb')}
                confirmed_data_type = claimed_data_type
                return arg_name, confirmed_data_type, remade_data
                # else:
                #     data_type_of_string_data = '.'+data_type_of_string_data#         dummy attempt to send file as declaredarg_name = 'files'remade_data =
            else:
                #       here we treat string as a content of the file.
                arg_name = 'files'
                ext = text_data_types[claimed_data_type['Content-Type']].split('/')[-1]
                confirmed_data_type = claimed_data_type
                remade_data = {'file': (f"data.{ext}", data)}
                return arg_name, confirmed_data_type, remade_data
        else:
            #         here we assume that NOT a string was attempted to be send as text_data_type. Not a path. Then it should be a file?
            arg_name = 'files'
            remade_data = {'file': data}
            confirmed_data_type = claimed_data_type
            return arg_name, confirmed_data_type, remade_data

    # despite code being very similar, I want checks for image/video/sound separately for logic division purposes

    # TODO, I hate to save these in the code, in future make it some config fileS(not only for text) or whatever
    # images, videos, music
    mm_data_types = {}
    mm_data_types['image/avif'] = '.avif'
    mm_data_types['image/bmp'] = '.bmp'
    mm_data_types['image/gif'] = '.gif'
    mm_data_types['image/vnd.microsoft.icon'] = '.ico'
    mm_data_types['image/jpeg'] = '.jpeg'
    mm_data_types['image/png'] = '.png'
    mm_data_types['image/svg+xml'] = '.svg'
    mm_data_types['image/tiff'] = '.tiff'
    mm_data_types['image/webp'] = '.webp'
    mm_data_types['video/x-msvideo'] = '.avi'
    mm_data_types['video/mp4'] = '.mp4'
    mm_data_types['video/ogg'] = '.ogv'
    mm_data_types['video/mp2t'] = '.ts'
    mm_data_types['video/webm'] = '.webm'
    mm_data_types['video/3gpp'] = '.3gp'
    mm_data_types['video/3gpp2'] = '.3g2'
    mm_data_types['audio/aac'] = '.aac'
    mm_data_types['audio/x-cdf'] = '.cda'
    mm_data_types['audio/x-midi'] = '.midi'
    mm_data_types['audio/midi'] = '.midi'
    mm_data_types['audio/mpeg'] = '.mp3'
    mm_data_types['audio/ogg'] = '.oga'
    mm_data_types['audio/opus'] = '.opus'
    mm_data_types['audio/wav'] = '.wav'
    mm_data_types['audio/webm'] = '.weba'
    mm_data_types['audio/3gpp'] = '.3gp'
    mm_data_types['audio/3gpp2'] = '.3g2'

    if claimed_data_type['Content-Type'] in mm_data_types.keys():
        if isinstance(data, str):
            if '.' in data:
                # Do I even need to check if it is in text_data_types extensions?? for now NOT CHECK and see what happens
                # if (data_type_of_string_data:= data.split('.')[-1]) in text_data_types.values():
                #                 then it must be a path to a file
                arg_name = 'files'
                remade_data = {'file': open(data, 'rb')}
                confirmed_data_type = claimed_data_type
                return arg_name, confirmed_data_type, remade_data
                # else:
                #     data_type_of_string_data = '.'+data_type_of_string_data#         dummy attempt to send file as declaredarg_name = 'files'remade_data =
            else:
                #       here we treat string as a content of the file.
                arg_name = 'files'
                ext = mm_data_types[claimed_data_type['Content-Type']].split('/')[-1]
                confirmed_data_type = claimed_data_type
                remade_data = {'file': (f"data.{ext}", data)}
                return arg_name, confirmed_data_type, remade_data
        else:
            #         here we assume that NOT a string was attempted to be send as mm_data_type. Not a path. Then it should be a file?
            arg_name = 'files'
            remade_data = {'file': data}
            confirmed_data_type = claimed_data_type
            return arg_name, confirmed_data_type, remade_data



    # despite code being very similar, I want checks for content-type application separately for logic division purposes
    application_data_types = {}
    application_data_types['application/x-abiword'] = '.abw'
    application_data_types['application/x-freearc'] = '.arc'
    application_data_types['application/vnd.amazon.ebook'] = '.azw'
    application_data_types['application/octet-stream'] = '.bin'
    application_data_types['application/x-bzip'] = '.bz'
    application_data_types['application/x-bzip2'] = '.bz2'
    application_data_types['application/x-x-cdf'] = '.cda'
    application_data_types['application/x-csh'] = '.csh'
    application_data_types['application/msword'] = '.doc'
    application_data_types['application/vnd.openxmlformats-officedocument.wordprocessingml.document'] = '.docx'
    application_data_types['application/vnd.ms-fontobject'] = '.eot'
    application_data_types['application/epub+zip'] = '.epub'
    application_data_types['application/gzip'] = '.gz'
    application_data_types['application/java-archive'] = '.jar'
    application_data_types['application/json'] = '.json'
    application_data_types['application/ld+json'] = '.jsonld'
    application_data_types['application/vnd.apple.installer+xml'] = '.mpkg'
    application_data_types['application/vnd.oasis.opendocument.presentation'] = '.odp'
    application_data_types['application/vnd.oasis.opendocument.spreadsheet'] = '.ods'
    application_data_types['application/vnd.oasis.opendocument.text'] = '.odt'
    application_data_types['application/ogg'] = '.ogx'
    application_data_types['application/pdf'] = '.pdf'
    application_data_types['application/x-httpd-php'] = '.php'
    application_data_types['application/vnd.ms-powerpoint'] = '.ppt'
    application_data_types['application/vnd.openxmlformats-officedocument.presentationml.presentation'] = '.pptx'
    application_data_types['application/vnd.rar'] = '.rar'
    application_data_types['application/rtf'] = '.rtf'
    application_data_types['application/x-sh'] = '.sh'
    application_data_types['application/x-tar'] = '.tar'
    application_data_types['application/vnd.visio'] = '.vsd'
    application_data_types['application/xhtml+xml'] = '.xhtml'
    application_data_types['application/vnd.ms-excel'] = '.xls'
    application_data_types['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] = '.xlsx'
    application_data_types['application/xml'] = '.xml'
    application_data_types['application/atom+xml'] = '.xml'
    application_data_types['application/vnd.mozilla.xul+xml'] = '.xul'
    application_data_types['application/zip'] = '.zip'
    application_data_types['application/x-7z-compressed'] = '.7z'

    if claimed_data_type['Content-Type'] in application_data_types.keys():
        if isinstance(data, str):
            if '.' in data:
                # Do I even need to check if it is in text_data_types extensions?? for now NOT CHECK and see what happens
                # if (data_type_of_string_data:= data.split('.')[-1]) in text_data_types.values():
                #                 then it must be a path to a file
                arg_name = 'files'
                remade_data = {'file': open(data, 'rb')}
                confirmed_data_type = claimed_data_type
                return arg_name, confirmed_data_type, remade_data
                # else:
                #     data_type_of_string_data = '.'+data_type_of_string_data#         dummy attempt to send file as declaredarg_name = 'files'remade_data =
            else:
                #       here we treat string as a content of the file.
                arg_name = 'files'
                ext = application_data_types[claimed_data_type['Content-Type']].split('/')[-1]
                confirmed_data_type = claimed_data_type
                remade_data = {'file': (f"data.{ext}", data)}
                return arg_name, confirmed_data_type, remade_data
        else:
            #         here we assume that NOT a string was attempted to be send as mm_data_type. Not a path. Then it should be a file?
            arg_name = 'files'
            remade_data = {'file': data}
            confirmed_data_type = claimed_data_type
            return arg_name, confirmed_data_type, remade_data

    # if we get array of bytes, lets treat as a file, shall we?
    arg_name = 'files'
    remade_data = {'file': data}
    confirmed_data_type = {'Content-Type':'unknown'}
    return arg_name, confirmed_data_type, remade_data



def send_request(url, context=None, request_type='GET', headers=None, data=None, params=None, cookies=None,
                 claimed_data_type=None):
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
    if not request_type in c.supported_request_types:
        raise Exception(f"Incorrect request method used: {request_type}")
    # prepare params
    # method that will choose url should also treat context. here we just check it is a dict
    if params and not isinstance(params, dict):
        raise Exception(f"Params should be a dict: {params}")

    # prepare context... if we find equals there we assume previous method of getting params out of there made an oopsie
    # also context should start with / and not finish with it
    if checkContext(context):
        raise Exception(f"Incorrect context used: {context}")

    # prepare data. now then. I want data-type header
    # thing is. there are so many data types that trying to handle them all here is dumb. let user specify this and make json default
    # However, if it contains 'audio', 'video', 'image' treat it as a file
    # If it is a text, try to treat string as a new file with specific .extension
    # if it application

    # wait. can we treat any data type user provides and try to send a file?
    kwarg_name, confirmed_data_type, remade_data = recognize_data_type(data, claimed_data_type)

    # prepare headers. if there would be any additional headers we always want to use: this is the place for it
    # for now check if is dict
    if headers and not isinstance(headers, dict):
        raise Exception(f"Headers should be a dict: {headers}")

    resp = requests.request(**{kwarg_name: remade_data})
