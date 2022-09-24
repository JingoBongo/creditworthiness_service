import __init__

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

# "service": "db_endpoint",   <- we have services tables to check if local exists. we will implement search in other fuses later
# "route": "/clear/Harvested_Routes", <- context, necessary for request
# "request_type": "GET", <- request type
# "requires" : [],       <- what variables we will try to put into json
# headers???? in task file??? some default for fuse?
def send_request(url, context=None, request_type = 'GET'):