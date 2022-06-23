It was decided to split TODOs and README since parts of this framework really need to be documented at least a bit

Fuse Framework

This is a framework written in Python that tries to solve a couple of issues I felt while trying Spring, Flask and Django.

1. It is a hub of microservices or other units and a bunch of tools to comfortably manage them.
2. It should be easy to launch and use. I had a need to run 3 to 9 different containers to run a small set of microservices and 
    their databases, redis, elastic etc. This was never easy to launch all together. Fuse aims to be launched by starting 1 script.
    For example, if not specified, services' ports are arranged dynamically, necessary DB and tables are re-created automatically,
    Ways to use logs, DB and endpoints are simplified.
    Python modules are installed automatically at launch.
3. It should be fast. Therefore, multiprocessing, launching every distinct module/node in a separate process. One could argue
    a lot about GIL, general Python slowness.. GIL is solved by having distinct python processes for each node, Python slowness..
    there I rely on Python devs, really. And better code.
4. It should have built in DB. I used Sqlite and Sqlalchemy, implemented a way to connect to DB concurrently.
5. It should use config for different stuff. Even nano'ing into config is better then messing with different scripts
6. (Work for later)It should be scalable. I already messed a bit with kubernetes and I found out that Fuse actually can scale
    by itself if updated properly. In theory one fuse can scale service(s) inside it and many fuses can work together
7. Gateway. Its necessary functions are still in re-thinking, but it should be main managing place for user, as well
   as main utility. In future it should provide static and dynamic documentation about current fuse. Right now 
   it can redirect or directly get result from ANY endpoint from ANY running service. User doesn't need to know specific
   port or anything, just necessary '/route'. There is a more preferred method of using distinct function for it tho.
8. DB endpoint. From case to case different functionality is added here, but now you can select from tables, drop or 
    clear tables just by requests.
    In general, if talking about DB utils, Fuse supports auto creating DB and tables based on config file and schemas.
    Using DB decorator also will provide necessary variables and wrapper functionality for proper DB functions/methods
9. Life ping. Fuse automatically checks if services(Nodes) are alive and tries to revive them if needed. It also allows
    user to start, finish (bounce stuff), see services statuses of any endpoints via requests.
10. Logs. Basically, if you write your code inside a FuseNode, you already have a distinct logger that writes both to
    console and distinct log file. Log files are of Rotating type, therefore they will never be too big
11. (Work for later)Taskmaster. It should handle multistep tasks and basically treat endpoints as actors.
12. (Work for later)Fisherman. It should be able to automatically download and use user specified modules from some
    available network resource.
13. This framework appeared to be more general purpose than I originally intended. It perfectly handles being a backend
    thing(FuseNode uses Flask as base), but also is capable of providing frontend part thanks to the Flask base. 
    And schedulers. AND it is able for literally any distinct python script. As a demo I had tetris and snake as JS code 
    inside HTML, but I plan to try a pygame module some time soon.
14. (Not a clue) Security? any ideas would be appreciated. I have an encrypting module in other repo, but what kind of 
    security is in general needed?
