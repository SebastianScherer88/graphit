import logging
from logging import DEBUG, INFO, WARNING

LOG_LEVEL = INFO
TAB_INDENTATION_LEVEL = 4
FUNCTION_DEFINITION_PATTERN = '(^[ \t\n]{0,20}def [a-zA-Z0-9_]{1,50}\()'
FUNCTION_DEFINITION_PATTERN_STUMP = '(^[ \t\n]{0,20}def '
FUNCTION_DEFINITION_PATTERN_TEMPLATE = '{function_handle}\()'
FUNCTION_CALL_PATTERN_TEMPLATE = ''

logger = logging.getLogger()
logger.setLevel(level=LOG_LEVEL)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)