import sys
from logentries import LogentriesHandler
import logging
from django.conf import settings


"""Default logger should be visible"""
# debug_level = logging.DEBUG if settings.SYS_DEBUG else logging.INFO
debug_level = logging.INFO
root = logging.getLogger()
root.setLevel(debug_level)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


"""Application logger"""
logger = logging.getLogger('smarti')

if hasattr(settings, 'LOGENTRIES_TOKEN'):
    logger.addHandler(LogentriesHandler(settings.LOGENTRIES_TOKEN))
    logger.setLevel(logging.WARNING)
else:
    logger.setLevel(logging.DEBUG)
