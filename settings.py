import logging
from logging import DEBUG, INFO, WARNING, ERROR

LOG_LEVEL = DEBUG
TAB_INDENTATION_LEVEL = 4
GENERIC_FUNCTION_DEFINITION_PATTERN = '(^[ \t\n]{0,20}def [a-zA-Z0-9_]{1,50}\()'
SPECIFIC_FUNCTION_DEFINITION_PATTERN_STUMP = '(^[ \t\n]{0,20}def '
SPECIFIC_FUNCTION_DEFINITION_PATTERN_TEMPLATE = '{function_handle}\()'
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_1 = '={function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_2 = ' {function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_3 = '[{function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_4 = '({function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_5 = '  {function_handle}('

FLOW_CHART_FONT_SIZE = 7
FLOW_CHART_X_STEP_SMALL = 3.8
FLOW_CHART_X_STEP_STANDARD = 6
FLOW_CHART_Y_STEP_STANDARD = 1.2
FLOW_CHART_ELEMENT_HEIGHT_STANDARD = 0.8
FLOW_CHART_ELEMENT_WIDTH_STANDARD = 5
FLOW_CHART_ELEMENT_WIDTH_LONG = 20
FLOW_CHART_ELEMENT_WIDTH_MAX = 40
FLOW_CHART_CIRCLE_COLOR = 'gold'
FLOW_CHART_COLOR_PALETTE = [
    'lightblue', #ADD8E6
    #'lightcoral',#F08080
    'lightcyan',#E0FFFF
    'lightgoldenrodyellow',#FAFAD2
    #'lightgray',#D3D3D3
    'lightgreen',#90EE90
    #'lightgrey',#D3D3D3
    #'lightpink',#FFB6C1
    #'lightsalmon',#FFA07A
    'lightseagreen',#20B2AA
    'lightskyblue',#87CEFA,
    'lightslategray',#778899
    'lightslategrey',#778899
    'lightsteelblue',#B0C4DE
    'lightyellow' #FFFFE0
]

FLOW_CHART_SIZE_Y = 250

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