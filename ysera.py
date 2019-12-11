import sys
from app.core import redmine_ticket_report
from app.report import *

getattr(sys.modules[__name__], sys.argv[1])()

