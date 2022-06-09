TODO

init:
Create database  if doesn't exist. CHECK
populate DB by config              CHECK
 create tables by schemas(separate folder, json format), list from config      CHECK

make it possible for service to have predefined port from config               CHECK
make Bus\Sys tables etc have name & path variables instead of just name
make separate table for scheduled processes so we can kill them or maintain their count

 
general
 make LOGGER
 make 3 separate folders instead of utils. Business implementation; System implementation; Utils
 maka separate 




































TODO. ACTUALLY TRY FLASK APP CHILD WITH BUILT IN ROUTES


tasks for Andrew

1. class CustomProcessListElement(): seems to be unused, although script write those elements into a list.
 !!  never uses the list. Fix/make is useful or remove

2. clean the code
2.5 try to minimize amount of duplicated variables

3. LOGGING -> logs come from certain (log example: [TIMESTAMP][PROCESS PID][file name? endpoint name? idk yet] [info/debug] info)
3.5 replace prints with logging? or even store logs into files? or even into separate endpoint? last one is too much i think

4. replace service.name (short/abs path) into service.name and service.path . BOTH IN DB AND LISTS, etc.

5. make sure if you start second life_ping service second schedule job is not started

6. mark important functions and make them 'try except' rescue? proof


NOTES TODO:
LIFEPING CAN BE HIDEN AS FLASK CHILD CLASS

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
TODO AS FUCKING SAP: put methods where they belong.
