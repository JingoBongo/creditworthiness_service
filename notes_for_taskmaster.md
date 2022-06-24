Reasons behind taskmaster:
    sometimes business logic is too hard to follow in the code, here we will have schema for the entire task route
    Sometimes we WANT task parts to be run in parallel but are too lazy to run threads
    Sometimes we need strict chain of steps but following it in the code is a problem

I assume taskmaster is complex enough to have a separate note file.

It should be able to read task either from file or class object.. most probably from schema file

it should store data for task in general and for steps

for task: name, number of steps?, current step (taslking about DB representation already?)... what else?

for step: needsResult, service + route to call, providesResult.. something like that

task should be able both to wait for some steps to be ready if next steps need its result
AND to launch steps in parallel in case they are independent of each other


taskmaster should needs modules: gevent, pickles, else? 

taskmaster will probably have a scheduler to actually reach different 
tasks. A pool where each thread is for 1 active task? Ye, why not
but then TODO ADD scheduler killer endpoint for life ping

taskmaster endpoint should be able to trigger tasks, even abort tasks? 
I'll try to just kill thread with stuck task? or free it? how does it work?

tasks should have statuses
'not started'
'in progress'
'finished'
'erorred'
and should be treated accordingly to statuses

How to store temp data and results of task?
in pickles. How to name pickles? taskname+unique id

temp data would be taskname+uniqueid+stepNo+someKey

step that would wait for some data would wait for result from
'taskname-___-stepNo-someKey'