It was decided to split TODOs and README since parts of this framework really need to be documented at least a bit

Fuse Framework

This is a framework written in Python that tries to solve a couple of issues I felt while trying Spring, Flask and Django.
TODO: update this with proper structure
1. It is a hub of microservices or other units and a bunch of tools to comfortably manage them.

2. It should be easy to launch and use. I had a need to run 3 to 9 different containers to run a small set of microservices and 
    their databases, redis, elastic etc. This was never easy to launch all together. Fuse aims to be launched by starting 1 script.
    For example, if not specified, services' ports are arranged dynamically, necessary DB and tables are re-created automatically,
    Ways to use logs, DB and endpoints are simplified.
    Python modules are installed automatically at launch.
    There is a way to use threads and processes as a simplified version of asyncio to get performance boost and not make the code
    unstartable by common things (means I don't add async and same function can be used synchronously, from thread and from process,
    both fire and forget and with a result)
3. It should be fast. Therefore, multiprocessing, launching every distinct module/node in a separate process. One could argue
    a lot about GIL, general Python slowness.. GIL is solved by having distinct python processes for each node, Python slowness..
    Multithreading, multiprocessing, smart decisions, planning and architecture
4. It should have built in DB. I used Sqlite and Sqlalchemy, implemented a way to connect to DB concurrently.
    Once again, DB and tables are recreated based on config file from SCHEMA json files. All intuitive and easy
    DB provided by Fuse is concurrent capable, very fast and adopted to be used in pythonic way, not like SQL queries
5. It should use config for different stuff. Even nano'ing into config is better then messing with different scripts
    Right now config serves as a master setting file for all sorts of stuff, as it should. It already is updated every
    time user changes it, not only saved the 'on start' state, but the corresponding reactions to config change are TODO
6. (Work for later)It should be scalable. I already messed a bit with kubernetes and I found out that Fuse actually can scale
    by itself if updated properly. In theory one fuse can scale service(s) inside it and many fuses can work together
7. Gateway. Gateway can serve on a dish every endpoint, every context local fuse have. One doesn't need  to search on
    what port needed service is. Just address gateway and ask to deliver your request to needed service. This is planned
    to be main endpoint both user and the web address to. Therefore I need TODO a proper UI so it becomes a hub manager
    and a place for some static documentation, probably some more... but it is a TODO
8. DB endpoint. From case to case different functionality is added here, but now you can select from tables, drop or 
    clear tables just by requests.
    In general, if talking about DB utils, Fuse supports auto creating DB and tables based on config file and schemas.
    Using DB decorator also will provide necessary variables and wrapper functionality for proper DB functions/methods
9. Life ping. Fuse automatically checks if services(Nodes) are alive and tries to revive them if needed. It also allows
    user to start, finish (bounce stuff), see services statuses of any endpoints via requests.
10. Logs. Basically, if you write your code inside a FuseNode, you already have a distinct logger that writes both to
    console and distinct log file. Log files are of Rotating type, therefore they will never be too big. This is a 
    standardised way to have logs (and I also extract WWerkzeug logs) to be the same across every piece of code
11. Taskmaster. This service should be treated as an Orchestrator, and it treats every other service as an Actor. With
    this in mind, user can send a single request (task) to Taskmaster, and that task can trigger multiple endpoints (steps)
    at the right order. This means that tasks have SCHEMAS (also JSON files) where it is specified which step needs which
    prerequisites etc, meaning SOME steps can be launched in parallel to boost performance and SOME will wait until the
    Taskmaster has enough data for them or required steps are done. All this work is done by proper SCHEMAS and the 
    Taskmaster, user just needs to send a request. SCHEMAS are stored at Fuse, user can get a list of them or take a look
    how any of them works. This way the request itself that user does it kept simple
12. (Work for later)Fisherman. It should be able to automatically download and use user specified modules from some
    available network resource. The plan is to have a repo with available modules to download.
13. This framework appeared to be more general purpose than I originally intended. It perfectly handles being a backend
    thing(FuseNode uses Flask as base, and Flask uses Werkzeug), but also is capable of providing frontend part thanks to the Flask base. 
    And schedulers. AND it is able for literally any distinct python script. As a demo I had tetris and snake as JS code 
    inside HTML, but I plan to try a pygame module some time soon.
14. (Not a clue) Security? any ideas would be appreciated. I have an encrypting module in other repo, but what kind of 
    security is in general needed?
