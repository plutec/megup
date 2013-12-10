#Internals
from core import settings

#Externals
import logging
import logging.handlers
import os

log = logging.getLogger('megup')

levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
          logging.CRITICAL]

try:
    log_level = int(settings.get_config('global', 'log_level'))
except:
    log_level = 5

# Establising limits
if log_level < 0:
    log_level = 0
elif log_level >= len(levels):
    log_level = len(levels) - 1


log.setLevel(levels[log_level])

file_handler = logging.FileHandler(os.path.join(
                        settings.get_config('global', 'logs_folder'), 'log'))
file_handler.setLevel(levels[log_level])

stream_handler = logging.StreamHandler()
stream_handler.setLevel(levels[log_level])

# create formatter and add it to the handlers
formatter = logging.Formatter( \
'[%(levelname)s] %(asctime)s - %(funcName)s@%(filename)s: %(message)s' \
                                , datefmt='%Y/%m/%d %H:%M:%S')


file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add the handlers to the logger

log.addHandler(file_handler)
log.addHandler(stream_handler)
