#python version is 3.4.3.

#==========================================================================
# IMPORTS
#==========================================================================
import subprocess
import random
import string
import os
import traceback
from datetime import datetime
import yaml


#==========================================================================
# GLOBALS AND CONSTANTS
#==========================================================================
cases = {} #dict with result of run tests
LOGS_FILE_NAME = "logs_file.log"
MAX_SUBSTRING_LENGHT = 100
MAX_TEXT_LENGHT = 1000
MAX_RAND_INT_NUMBER = 100
CONST_500_MB_BYTES = 500 * 1024 * 1024
CONST_1_GB_BYTES = CONST_500_MB_BYTES * 2
MAXIMUM_BIG_FILE_SIZE_BYTES = 500*1024*1024*8


#==========================================================================
# FRAMEWORK FUNCTIONS
#==========================================================================
def run_exe_file(list_of_three_args):
    """Get list of 3 strings: path to exe file, path to text, string need to find.
    Return result of test execution as a string."""
    run_exe = subprocess.Popen(list_of_three_args, stdout=subprocess.PIPE)
    exe_output = run_exe.communicate()
    output_string = exe_output[0].decode('utf-8')
    output_string = output_string.strip()
    return output_string


def printing_test_header(text_in_header):
    """Get some string and surround it by stars. Is used in logs file. Return string."""
    header_text = '********************************* ' + text_in_header.upper() + ' *********************************\n'
    return header_text


def writing_logs(file_name, function_name, substring, expected_string, real_string):
    """Get 5 strings: name of testing text, name of function which were executed,
    string which was looking for, string which was expected to get and string which was actually get.
    Write information about test execution in the log file. Return None."""
    logs_file = open(LOGS_FILE_NAME, "a")
    try:
        text_file = open(file_name, 'r')
        text_in_test_file = text_file.read()
        text_file.close()
        os.remove(file_name)
    except Exception:
        text_in_test_file = 'text file not exist or cannot open'
    log_text = printing_test_header(function_name)
    if expected_string == real_string:
        test_result = 'passed'.upper()
    else:
        test_result = 'failed'.upper()
    test_date = datetime.today()
    log_text = log_text + str(test_date) +"\nTest " + 'started' + ' ' \
               + '\n\n' + "In text:\n" + "'" + str(text_in_test_file) + "'" + "\n\nand substring\n" + "'" \
               + str(substring) + "'" + "\n\nExpected result:\n" + "'" + str(expected_string) + "'" \
               + "\n\nActual result:\n" + "'" + str(real_string) + "'" + '\n\nTest '\
               '"' + str(function_name) + '" ' + test_result.upper() + '\n' * 4
    print(log_text)
    logs_file.write(log_text)
    logs_file.close()


def compare_python_and_exe_results(function, text, substring):
    """Get test function to execute and 2 strings: test and substring. Execute test by python and by exe file.
    Compare results. Return True or False."""
    test_name = function.__name__
    print('Test ', test_name, ' started')
    text_file = open("test_file.txt", "w")
    text_file.write(text)
    text_file.close()
    text_file = open("test_file.txt", "r")
    content = text_file.read()
    if substring in content and len(substring) != 0:
        expected_string = 'Found at position ' + str(content.index(substring))
    else:
        expected_string = ''
    text_file.close()
    res = run_exe_file([path_to_exe_file, 'test_file.txt', substring])
    writing_logs('test_file.txt', test_name, substring, expected_string, res)
    if res == expected_string:
        return True
    else:
        return False


def genering_big_text_file(size_in_byte):
    """Give int number which means size of the future file. Create text file. Return string with information
    about successful creating or with error code if the file was not created."""
    try:
        text_file = open('big_test_file.txt', "wb")
        text_file.write(b"hello world")
        text_file.seek(size_in_byte)
        text_file.write(b"\0")
        text_file.close()
        log_string = 'File test_file.txt created. Its size is ' + str(os.stat("big_test_file.txt").st_size) + ' bytes.'
    except Exception as err:
        log_string = traceback.format_exc()
    return log_string


def execute_test(func):
    """Get function. Execute her and return True or False."""
    result = func()
    if result is True:
        cases[func.__name__] = 1
    else:
        cases[func.__name__] = 0
    return result


def test_function(list_of_tests_and_repeats):
    """Get list of tuples. Sending functions to execute as many times as need. Writing result in logs.
     Return None."""
    result_for_logs = {'Test(s) passed: ': 0, 'Test(s) failed: ': 0}
    for func in list_of_tests_and_repeats:
        i = 1
        while i <= func[1]:
            result = execute_test(func[0])
            if result is True:
                result_for_logs['Test(s) passed: '] += 1
            else:
                result_for_logs['Test(s) failed: '] += 1
            i += 1

    print(result_for_logs)
    logs_file = open(LOGS_FILE_NAME, "a")
    logs_string = 'Test(s) passed: ' + str(result_for_logs['Test(s) passed: ']) + '\n'\
        + 'Test(s) failed: ' + str(result_for_logs['Test(s) failed: '])
    logs_file.write(logs_string)


def get_list_of_functions():
    ''' Get information from the configurations file.
    Return list of 2 elements: path to exe file, list of tuples containing function and number of her repeats.'''
    list_of_functions = [all_is_okey, no_substring_in_file, file_is_empty, substring_is_empty,
                         substring_more_than_text, file_is_not_exists, not_three_args_given, file_is_very_big]
    list_of_strings = ['all_is_okey', 'no_substring_in_file', 'file_is_empty', 'substring_is_empty',
                       'substring_more_than_text', 'file_is_not_exists', 'not_three_args_given', 'file_is_very_big']
    list_to_execute = []
    list_of_repeats = []
    conf = yaml.safe_load(open('configurations.yml'))
    path_to_exe_file = conf['path_to_exe_file']
    config_list_of_functions = conf['tests']
    for item in config_list_of_functions:
        index = list_of_strings.index(''.join(item.keys
                                              ()))
        list_to_execute.append(list_of_functions[index])
        list_of_repeats.append(sum(item.values()))

    list_of_tests_and_repeats = list(zip(list_to_execute, list_of_repeats))
    print(list_of_tests_and_repeats)
    return [list_of_tests_and_repeats, path_to_exe_file]


#==========================================================================
# TEST FUNCTIONS
#==========================================================================
def all_is_okey():
    """Generating text file with random text and looking for one string of this text. Return True or False."""
    substring = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(1, MAX_SUBSTRING_LENGHT)))
    first_text_part = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(0, MAX_TEXT_LENGHT)))
    second_text_part = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(0, MAX_TEXT_LENGHT)))
    text = first_text_part + substring + second_text_part
    return compare_python_and_exe_results(all_is_okey, text, substring)


def no_substring_in_file():
    """Generating text file with random text and looking for the string which cannot be in this text.
    Return True or False"""
    text = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(0, MAX_TEXT_LENGHT)))
    substring = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(1, MAX_SUBSTRING_LENGHT)))
    substring = substring + str(random.randint(1, MAX_RAND_INT_NUMBER))
    return compare_python_and_exe_results(no_substring_in_file, text, substring)


def file_is_empty():
    """Generating empty text file and looking for the string in this text. Return True or False"""
    text = ''
    substring = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(1, MAX_RAND_INT_NUMBER)))
    return compare_python_and_exe_results(file_is_empty, text, substring)


def substring_is_empty():
    """Generating text file with random text and looking for the empty string in this text. Return True or False"""
    text = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(0, MAX_TEXT_LENGHT)))
    substring = ''
    return compare_python_and_exe_results(substring_is_empty, text, substring)


def substring_more_than_text():
    """Generating text file with random text and string which size is more than text size.
    Try to looking for this string. Return True or False"""
    text = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(0, MAX_SUBSTRING_LENGHT)))
    substring = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(1, MAX_TEXT_LENGHT)))
    return compare_python_and_exe_results(substring_more_than_text, text, substring)


def file_is_not_exists():
    '''Generate random string and try to find her in the text file which not exist, or cannot be open, or which path
    in configuration file was wrong. Return True or False.'''
    print('Test ', file_is_not_exists, ' started')
    substring = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) + ' ' * random.randint(0, 1)
        for _ in range(random.randint(1, MAX_RAND_INT_NUMBER)))
    try:
        f = open('file_not_exists.txt')
        f.close()
        os.remove('file_not_exists.txt')
    except Exception:
        pass
    expected_string = 'Cannot open file file_not_exists.txt'
    real_string = run_exe_file([path_to_exe_file, 'file_not_exists.txt', substring])
    writing_logs('', 'no_substring_in_file', substring, expected_string, real_string)
    if real_string == expected_string:
        return True
    else:
        return False


def not_three_args_given():
    """Try to execute exe file with more and less arguments than it needs. Return True or False."""
    print('Test not_three_args_given started')
    less_args = [path_to_exe_file]
    for _ in range(random.randint(0, 1)):
        less_args.append('qwerty')
    more_args = [path_to_exe_file]
    for _ in range(random.randint(4, 10)):
        more_args.append('qwerty')
    expected_string = "Usage: \r\n\tTest4Python.exe <source file> <string to find>"
    result_for_less_args = run_exe_file(less_args)
    result_for_more_args = run_exe_file(more_args)
    if expected_string == result_for_less_args and expected_string == result_for_more_args:
        test_res = 'passed'.upper()
        result_for_return = True
    else:
        test_res = 'failed'.upper()
        result_for_return = False
    logs_file = open(LOGS_FILE_NAME, "a")
    log_text = printing_test_header('not_three_args_given')
    log_text = log_text + str(datetime.today()) + '\nTest started' + '\n\n' + "With arguments:\n" + "'" + str(
        less_args) + "'" + \
               "\n\nand arguments\n" + "'" + str(more_args) + "'" + "\n\nExpected result:" + "'" + \
               str(expected_string) + "'" + "\n\nActual recults:\n" + "'" + str(result_for_less_args) + "'" \
               + '\n' + 'and\n' + str(result_for_more_args) + '\n\n' + 'Test "Not 3 args given" '\
               + test_res.upper() + '\n' * 4
    logs_file.write(log_text)
    print(log_text)
    logs_file.close()
    return result_for_return


def file_is_very_big():
    """Generating a big text file with some string and looking for this string.
    If it works, creating another text file which is more than the previous at 500 Mb.
    Test is passed when it works with 4 Gb file.
    Return True or False."""
    print('Test file_is_very_big started')
    log_header = printing_test_header('file_is_very_big') + '\nTest Started.\n' + str(datetime.today())
    print(log_header)
    try:
        file_size = CONST_500_MB_BYTES
        while file_size <= MAXIMUM_BIG_FILE_SIZE_BYTES:
            genering_big_text_file(file_size)
            expected_result = 'Found at position 6'
            real_result = run_exe_file([path_to_exe_file, 'big_test_file.txt', 'world'])
            os.remove('big_test_file.txt')
            if expected_result == real_result:
                file_size = file_size + CONST_500_MB_BYTES
                print('current size: ', file_size)
                print('result: ', real_result)
            elif real_result != '' and 'Found at position' not in real_result:
                log_text = "\n\nExpected result:\n" + 'Something error code' + ' \n\nActual result is:\n' \
                           + str(real_result) + "Test 'file_is_very_big' FAILED" + '\n' * 4
                logs_with_header = log_header + log_text
            elif 'Found at position' in real_result:
                log_text = "\n\nExpected result:\n" + str(expected_result) + ' \n\nActual result is:\n' \
                           + str(real_result) + "Test 'file_is_very_big' FAILED" + '\n'*4
                result_for_return = False
            else:
                log_text = "\n\nTest failed when file size was " \
                    + str(file_size) + ' bytes' + ' (' + str(float(file_size)/CONST_1_GB_BYTES) + ' Gb)' \
                    + "\n\nTest 'file_is_very_big' FAILED" + '\n'*4
                logs_with_header = log_header + log_text
                result_for_return = False
                break
        if file_size == MAXIMUM_BIG_FILE_SIZE_BYTES:
            log_text = "\n\n Maximum file size was " + str(file_size) + ' bytes'\
                       + ' (' + str(float(file_size)/CONST_1_GB_BYTES) + ' Gb)' "\n\nTest 'File is very big' PASSED" + '\n'*4
            logs_with_header = log_header + log_text
            result_for_return = True
    except Exception as err:
        log_string = traceback.format_exc()
        log_text = "\n\n File cannot be created because it needs as minimum 4Gb free space." \
                   + 'Test failed at' + str(file_size) + ' bytes' + ' (' + str(float(file_size)/CONST_1_GB_BYTES) + ' Gb)' \
                   + '\nError\n: ' + log_string + "\n\nTest 'File is very big' cannot execute" + '\n' * 4
        logs_with_header = log_header + log_text
        result_for_return = False
    finally:
        logs_file = open(LOGS_FILE_NAME, "a")
        logs_file.write(logs_with_header)
        logs_file.close()
        print(log_text)
        try:
            os.remove('big_test_file.txt')
        except Exception:
            pass
        return result_for_return


if __name__ == '__main__':
    list_of_tests_and_repeats = get_list_of_functions()[0]
    path_to_exe_file = get_list_of_functions()[1]
    test_function(list_of_tests_and_repeats)
