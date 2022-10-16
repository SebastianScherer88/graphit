from settings import logger
from helpers import record_all_modules, record_all_functions_basic, record_all_functions

all_modules = record_all_modules(reference_directory='.',
                                 scope=['.'],
                                 ignore_scope=['venv','tests'])

logger.info(f'Recorded modules: {all_modules}')

all_functions_basic = record_all_functions_basic(recorded_modules=all_modules)

logger.debug(f'Recorded functions meta data (basic): {all_functions_basic}')

all_functions = record_all_functions(recorded_functions_basic=all_functions_basic)

logger.debug(f'Recorded functions meta data (including scope and calls): {all_functions}')