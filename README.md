TODO

check for busy port while assigning new port doesn't work as intended and needs fix

refactor endpoints to return at least JSON, not just some text

maybe add EXTRA bouncer for life_ping service as it is used to bounce everrything else

Front gateway: 
it needs to have at least these 2 features:
1. provide documentation about what this fuse instance can provide and how to use it in general
2. redirect everything.
   for now this redirect thing simply means literal redirecting to new url. I don't necessarily want this
    because localhost urls exist and user won't see them from other PC. If this way of doing things is kept
    below logic should be implemented:
1 gateway should get list of all services for all urls.
2 gateway should harvest and store time to time all available routs that those services can provide
3 gateway should fully mimic the request while redirecting
4 gateway should handle multiple instances of same service BUT report same routes in DIFFERENT services

Back Gateway will have no urls problems i think. 

Gateways should be a valid way for any service/user to call for another service.
this should be 100% dynamical





implement concatenator for logs and hide the result into zip file (this WILL be a disaster to make)

refactor flask_child a bit

refactor some functions to probably take its own utils file instead of general utils. 
It is unintuitive to find json utils in there.

update settings file? I'd like to first find if I need it. Deleting for now.
(reminder tho, it can be generated using pycharm upper menu)


add gateway
add task queue
TODO do i need to delete notes2? I will probably put it in docker one day, so not necessarily
