from config import settings
import random


def gen_verify_code():
    default_code_length = 6
    code_length = default_code_length if 'VERIFY_CODE_LENGTH' not in dir(settings) \
        else settings.VERIFY_CODE_LENGTH

    result = ''
    for i in range(code_length):
        result += str(random.randint(3, 9))
    return result
