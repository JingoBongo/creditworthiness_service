TODO

refactor endpoints to return at least JSON, not just some text <- always actual

flask is multithreaded by deafult. find how to specify thread count if what (gates and taskmaster will need more)
or just to enable the "economic" variant
add ability to lock multithreading in order to reduce performance hunger.

think about security and encrypting files and connection

possibly compliment db_utils with 
a) possibly db copy every 5 mins for failsafe and switch to it in case of problems run-time
b) possibly have a readers-db copy, but this brings the task of scheduler-copypaster of db.

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
some of the points are done, just a note to add: localhost can be changed to local IP, check

   
implement concatenator for logs and hide the result into zip file (this WILL be a disaster to make)

update settings file? I'd like to first find if I need it. Deleting for now.
(reminder tho, it can be generated using pycharm upper menu)

ah yes, add ability to update config file while fuse is up

Also NEW: 
dynamic UI for most common things like starting services, walking through DB, etc
documentation
cookies
security
SSL -> certificate
dynamic service scaling from config -> request counters
dynamic config update
task for bouncing any service
schedulers to be started from config  <-
processes to be started from config   <- these 2 need to be launched during the run, as well as services?
check post taskmaster steps
check 30 steps task
taskmaster to add way to download pickle
add a way to upload/download files. <- will be used for fisherman
The Fisherman