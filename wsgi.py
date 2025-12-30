import sys
import os

path = '/home/yourusername/schedule_site'
if path not in sys.path:
    sys.path.append(path)

from app import app as application