import logging
from logging import DEBUG, INFO, WARNING, ERROR

# parsing settings
TAB_INDENTATION_LEVEL = 4
GENERIC_FUNCTION_DEFINITION_PATTERN = '(^[ \t\n]{0,20}def [a-zA-Z0-9_]{1,50}\()'
SPECIFIC_FUNCTION_DEFINITION_PATTERN_STUMP = '(^[ \t\n]{0,20}def '
SPECIFIC_FUNCTION_DEFINITION_PATTERN_TEMPLATE = '{function_handle}\()'
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_1 = '={function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_2 = ' {function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_3 = '[{function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_4 = '({function_handle}('
SPECIFIC_FUNCTION_CALL_PATTERN_TEMPLATE_5 = '  {function_handle}('

# flow chart visuals & layout
FLOW_CHART_FONT_SIZE = 7
FLOW_CHART_X_STEP_SMALL = 3.4
FLOW_CHART_X_STEP_STANDARD = 5
FLOW_CHART_Y_STEP_STANDARD = 1.2
FLOW_CHART_ELEMENT_HEIGHT_STANDARD = 0.8
FLOW_CHART_ELEMENT_WIDTH_STANDARD = 4
FLOW_CHART_ELEMENT_WIDTH_LONG = 20
FLOW_CHART_ELEMENT_WIDTH_MAX = 40
FLOW_CHART_CIRCLE_COLOR = 'gold'
FLOW_CHART_COLOR_PALETTE = [
    #'lightslategray',#778899
    #'lightslategrey',#778899
    'lightsteelblue',#B0C4DE
    #'lightblue', #ADD8E6
    'lightskyblue',#87CEFA,
    'lightcyan',#E0FFFF
    #'lightgray',#D3D3D3
    'lightseagreen',#20B2AA
    'lightgreen',#90EE90
    #'lightgrey',#D3D3D3
    'lightyellow', #FFFFE0,
    #'lightgoldenrodyellow',#FAFAD2
    'lightsalmon',#FFA07A
    'lightpink',#FFB6C1
    'lightcoral',#F08080
]

FLOW_CHART_FRAME_WIDTH=0.5
FLOW_CHART_LINE_WIDTH=1

FLOW_CHART_SIZE_Y = 250

# logging
LOG_LEVEL = INFO
logger = logging.getLogger()
logger.setLevel(level=LOG_LEVEL)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s() - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)