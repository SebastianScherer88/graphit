import os
import random
from datetime import datetime as dt
from pathlib import Path
from string import ascii_letters as letters
from string import digits

from graphit.settings import logger


def create_output_directory(output_directory: Path) -> Path:
    '''
    Utility function that checks the existence of the specified directory and creates a timestamped subdirectory, where
    possible.

    Args:
        output_directory:

    Returns:

    '''

    try:
        temp_output_subdir = f'{dt.strftime(dt.now(), "%Y-%m-%d %H-%M-%S")}'
        temp_output_dir = os.path.join(output_directory,temp_output_subdir)
        os.mkdir(temp_output_dir)

        logger.debug(f'Created the timestamped output directory {temp_output_dir}.')
    except FileNotFoundError as e:
        logger.error(f'The specified output directory {output_directory} does not exist.')
        raise e

    return temp_output_dir


def create_unique_reference_id() -> str:
    '''
    Helper function that creates a 20 character unique id from alphanumeric characters
    :return:
    '''

    return ''.join(random.choices(population=letters + digits,k=20))