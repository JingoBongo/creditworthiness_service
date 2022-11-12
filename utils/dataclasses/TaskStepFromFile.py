import __init__

# TODO write proper dataclasses file names, I feel I lack standardization over here

class TaskStepFromFile:
    __slots__ = ("step_number", "step_name", "service", "route", "request_type", "requires",
                 "requires_steps", "needs_to_provide", "is_finished")

    def __init__(self, step_number, step_name, service, route, request_type, requires, requires_steps,
                 needs_to_provide):
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
