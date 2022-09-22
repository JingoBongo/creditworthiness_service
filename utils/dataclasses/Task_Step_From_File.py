from utils import constants as c
from utils import logger_utils as log
from utils import general_utils as g

class Task_Step_From_File:
    def __init__(self, step_number, step_name, service, route, request_type, requires, requires_steps):
        self.step_number = int(step_number)
        self.step_name = step_name
        self.service = service
        self.route = route
        self.request_type = request_type
        self.requires = [].extend(requires)
        self.requires_steps = [].extend(requires_steps)
        self.is_finished = False
