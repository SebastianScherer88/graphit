from string import ascii_letters as letters
from string import digits
import random

def create_unique_reference_id() -> str:
    '''
    Helper function that creates a 20 character unique id from alphanumeric characters
    :return:
    '''

    return ''.join(random.choices(population=letters + digits,k=20))