#Internals
from core import settings

#Externals
import logging
import logging.handlers
import os

log = logging.getLogger('megup')
log.setLevel(logging.DEBUG)

# create file handlers
dh = logging.FileHandler(os.path.join(
						settings.get_config('global','logs_folder'), 'debug'))
dh.setLevel(logging.DEBUG)

ih = logging.FileHandler(os.path.join(
						settings.get_config('global','logs_folder'), 'info'))
ih.setLevel(logging.INFO)

wh = logging.FileHandler(os.path.join(
						settings.get_config('global','logs_folder'), 'warning'))
wh.setLevel(logging.WARNING)

eh = logging.FileHandler(os.path.join(
						settings.get_config('global','logs_folder'),'error'))
eh.setLevel(logging.ERROR)

ch = logging.FileHandler(os.path.join(
						settings.get_config('global','logs_folder'),'critical'))
ch.setLevel(logging.CRITICAL)

# create formatter and add it to the handlers
formatter = logging.Formatter( \
'[%(levelname)s] %(asctime)s - %(funcName)s@%(filename)s: %(message)s' \
                                , datefmt='%Y/%m/%d %H:%M:%S')

dh.setFormatter(formatter)
ih.setFormatter(formatter)
wh.setFormatter(formatter)
eh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
log.addHandler(dh)
log.addHandler(ih)
log.addHandler(wh)
log.addHandler(eh)
log.addHandler(ch)