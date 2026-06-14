
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.config import *

print(SQL_SERVER)
print(SQL_DB)
print(SQL_USER)