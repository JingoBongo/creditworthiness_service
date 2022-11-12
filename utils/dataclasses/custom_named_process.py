import __init__
import multiprocessing


class CustomNamedProcess(multiprocessing.Process):
    def __init__(self, *args, name=None, **kwargs):
        self.name = name
        super().__init__(*args, **kwargs)