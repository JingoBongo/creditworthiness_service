import uuid

import __init__
import pickle
from utils import logger_utils as log

def generate_random_uid4():
    return str(uuid.uuid4())