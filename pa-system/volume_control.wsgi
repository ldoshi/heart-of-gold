import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/html/grand-central/pa-system')
sys.path.insert(0, '/var/www/html/grand-central/venv/lib/python3.10/site-packages')

from volume_control import app as application

