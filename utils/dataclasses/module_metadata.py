import os
from datetime import datetime

from utils import random_utils


class ModuleMetadata:
    @staticmethod
    def get_module_name(metadata_dict):
        if name := metadata_dict.get('MDL_MODULE_NAME'):
            return name
        return 'unnamed_module_' + random_utils.generate_random_uid4()

    @staticmethod
    def get_module_file_name(filepath):
        return os.path.basename(filepath)

    def __eq__(self, other):
        return self.module_file_name == other.module_file_name

    def __init__(self, metadata_dict: dict, filepath=None):
        self.standalone = bool(metadata_dict.get('MDL_STANDALONE', True))
        self.module_name = ModuleMetadata.get_module_name(metadata_dict)
        self.module_file_name = ModuleMetadata.get_module_file_name(filepath)
        self.mono = bool(metadata_dict.get('MDL_MONO', True))
        self.local = bool(metadata_dict.get('MDL_LOCAL', False))
        self.role = metadata_dict.get('MDL_ROLE', 'BUSINESS')
        self.author = metadata_dict.get('MDL_AUTHOR', None)
        self.repository = metadata_dict.get('MDL_REPOSITORY', None)
        self.version = int(metadata_dict.get('MDL_VERSION', 1))
        date = metadata_dict.get('MDL_LAST_VERSION_DATE', '1/1/1111')
        self.last_version_date = datetime.strptime(date, '%m/%d/%Y').date()
        self.description = metadata_dict.get('MDL_DESCRIPTION', None)
