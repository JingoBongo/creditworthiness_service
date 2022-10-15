from utils import constants as c
from utils import logger_utils as log
from utils import general_utils as g

class Task_Step_From_File:
    def __init__(self, step_number, step_name, service, route, request_type, requires, requires_steps, needs_to_provide):
        self.step_number = int(step_number)
        self.step_name = step_name
        self.service = service
        self.route = route
        self.request_type = request_type
        rrequires = []
        rrequires.extend(requires)
        self.requires = rrequires

        rrequires_steps = []
        rrequires_steps.extend(requires_steps)
        self.requires_steps = rrequires_steps

        nneeds_to_provide = []
        nneeds_to_provide.extend(needs_to_provide)
        self.needs_to_provide = nneeds_to_provide
        self.is_finished = False
