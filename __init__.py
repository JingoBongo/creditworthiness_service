import os
import sys
from pathlib import Path

myDir = os.getcwd()
sys.path.append(myDir)
path = Path(myDir)
a=str(path.parent.absolute())

sys.path.append(a)