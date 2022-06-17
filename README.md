TODO

implement concatenator for logs and hide the result into zip file (this WILL be a disaster to make)

refactor flask_child a bit

refactor some functions to probably take its own utils file instead of general utils. 
It is unintuitive to find json utils in there.

update settings file? I'd like to first find if I need it. Deleting for now.
(reminder tho, it can be generated using pycharm upper menu)


add gateway
add task queue
TODO do i need to delete notes2? I will probably put it in docker one day, so not necessarily


db_decorator is GIGA CHAD, but!. If you see that functions from db_utils have args* but they are not used, don't believe it.
args* are consumed by decorator, but function only uses kwargs** that are supplemented by decorator
