How to run: start fuse.py

**For now requirements.txt doesn't exist, this is a TODO

agh. this will be a status thing for now I think

todo
list of processes, it doesn't work and is not needed
do I need busy ports in DB? or using it in other file just prevents read/write problems
add REACT TO DEAD SERVICE to life ping.
add gateway
add task queue
manage unused DB file somehow? for my system it is locked permanently
finish how template for business/system endpoint looks like
TODO do i need to delete notes2? I will probably put it in docker one day, so not necessarily
TODO some things from config should be moved into the code, like system table names. they are not to be changed. therefore,
out of scope of the config

db_decorator is GIGA CHAD, but!. If you see that functions from db_utils have args* but they are not used, don't believe it.
args* are consumed by decorator, but function only uses kwargs** that are supplemented by decorator
TODO PRINTS AND LOGGING
TODO add ability to show alive services to lifeping