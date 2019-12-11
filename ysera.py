import sys
from app.report import *

getattr(sys.modules[__name__], sys.argv[1])()
