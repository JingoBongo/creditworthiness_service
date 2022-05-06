import subprocess


class CustomNamedProcess(subprocess.Popen):
    def __init__(self, *args, name=None, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)


class CustomProcessListElement():
    def __init__(self, full_name, port, short_name, pid, obj_reference):
        self.full_name = full_name
        self.port = port
        self.short_name = short_name
        self.pid = pid
        self.obj_reference = obj_reference
