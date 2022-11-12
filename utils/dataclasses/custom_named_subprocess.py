import __init__
import subprocess


class CustomNamedSubprocess(subprocess.Popen):
    def __init__(self, *args, name=None, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)

