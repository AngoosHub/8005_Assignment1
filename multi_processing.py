#!/usr/bin/env python3

"""
----------------------------------------------------------------------------------------------------
COMP 8005 Network Security & Applications Development
Assignment 1
Student:
    - Hung Yu (Angus) Lin, A01034410, Set 6J
----------------------------------------------------------------------------------------------------
multi_processing.py
    Performs mathematically intensive operations (Prime factorization) with file I/O.
    Implements multiprocessing.
    Measures performance with timing data.
----------------------------------------------------------------------------------------------------
"""
import sys
import time
import os
from functools import partial
from itertools import repeat
from multiprocessing import Pool, freeze_support

NUMBERS_PATH = "numbers.txt"
LOG_PATH = "log_processes.txt"


def read_user_input():
    """
    Display simple command line UI, prompts and reads user input.
    Enter the number of tasks to complete.
    (Input must be an integer from 0 to 50 inclusive).
    Commands:
        Enter 0 - Exit program.
        Enter number between 1 to 50 - Run number of tasks
    :return: none
    """

    print("Starting multiprocessing program.")

    try:
        keep_running = True
        while keep_running:
            print('--------------------------------------\n'
                  'Multiprocessing Implementation.\n'
                  'Enter the number of tasks to complete.\n'
                  '(Input must be an integer from 0 to 50 inclusive).\n'
                  'Commands:\n'
                  '    Enter number 0        - Exit program.\n'
                  '    Enter number 1 to 50  - Start program with # of tasks.\n'
                  '--------------------------------------')
            user_command = input("Please Enter Command: ")

            try:
                if not user_command.isdigit():
                    raise ValueError
                user_com_int = int(user_command)
                if user_com_int < 0:
                    raise ValueError
            except ValueError:
                print('Invalid input, please enter an integer from 0 to 50')
                continue

            user_com_int = int(user_command)

            if user_com_int == 0:
                keep_running = False
                print("Exiting...")
            elif 0 < user_com_int <= 50:
                print('Enter number of processes to create.\n'
                      '(Input must be an integer from 1 to 50 inclusive).\n'
                      '--------------------------------------')
                user_processes = input("Please enter number of processes: ")
                try:
                    if not user_processes.isdigit():
                        raise ValueError
                    processes_int = int(user_processes)
                    if not 0 < processes_int <= 50:
                        raise ValueError
                except ValueError:
                    print("Invalid input, returning to task menu.")
                    continue

                multiprocessing(user_com_int, processes_int)
            else:
                print("Invalid input, please re-enter.")

    except OSError as msg:
        print('Program Error Code : ' + msg.strerror)
        sys.exit()


def multiprocessing(total_tasks, total_processes):
    """
    Performs the mathematical and I/O tasks with simple for loop, with multiprocessing
    implementations.
    Reads numbers from text file up to total tasks assigned, and records the timing
    data of the operations to measure efficiency.
    :param total_tasks: (int) number of tasks to perform
    :param total_processes: (int) number of processes to create
    :return: None
    """
    time_total_start = time.perf_counter()

    int_list = []
    try:
        with open(file=NUMBERS_PATH, mode="r", encoding='utf8') as file:
            number_list = file.read().splitlines()
            if len(number_list) < 1:
                print("Empty numbers.txt detected, returning to menu.")
                return

            if len(number_list) < total_tasks:
                print(f"Error, tasks requested = {total_tasks}, numbers in numbers.txt = {len(number_list)}. "
                      f"Not enough numbers for tasks. Returning to menu.")
                return

            for idx, number in enumerate(number_list):
                try:
                    if not number.isdigit():
                        raise ValueError
                    number_int = int(number)
                    if number_int < 0:
                        raise ValueError

                    assert number_int >= 0, "Data from number.txt should only contain positive integers."
                    int_list.append(number_int)

                except ValueError:
                    print(f"Read invalid input: \"{number}\"(line {idx+1}) in numbers.txt, must be a positive integer. "
                          f"Returning to menu.")
                    return
                except AssertionError as msg:
                    print("Assertion Error detected.")
                    print(msg)
                    return
    except IOError:
        print("Could not read file:", NUMBERS_PATH)
        return

    process_time_list = list(range(total_tasks))
    process_time_list_raw = []
    index_list = list(range(total_tasks))

    with Pool(total_processes) as pool:
        process_results = pool.starmap(process_func, zip(int_list, index_list))

    total_time = time.perf_counter() - time_total_start

    for result in process_results:
        process_time_list_raw.append(result[2])
        process_time_list[result[1]] = result[0]

    avg_task_time = sum(process_time_list_raw) / len(process_time_list_raw)
    print(f"Avg task time: {avg_task_time}")
    print(f"Total time: {total_time}")

    try:
        with open(file=LOG_PATH, mode="a", encoding='utf8') as file:
            data_log = f"-----------------Timing Data-----------------\n"
            for idx, task_time in enumerate(process_time_list):
                data_log += f"{task_time}\n"
            data_log += f"\nAvg task time: {avg_task_time}\n"
            data_log += f"Total time: {total_time}\n"
            data_log += f"---------------------------------------------\n\n"
            file.write(data_log)
    except IOError:
        print("Could not read file:", NUMBERS_PATH)


def process_func(num, index):
    time_loop_start = time.perf_counter()

    factor_list = prime_factorization(num)
    save_data(num, factor_list)

    process_time = time.perf_counter() - time_loop_start
    timing_data = f"Task {index+1} time: {process_time}, by Process ID: {os.getpid()}"
    print(timing_data)
    return [timing_data, index, process_time]


def prime_factorization(number):
    """
    Computes prime factorization on given number.
    :param number: (int) number to factorize
    :return: (list) list of factors
    """
    n = number
    factor = 2
    factor_list = []
    while factor * factor <= number:
        if number % factor:
            factor += 1
        else:
            number //= factor
            factor_list.append(factor)
    if number > 1:
        factor_list.append(number)

    return factor_list


def save_data(number, factor_list):
    """
    Writes the factorization results into a log file.
    :param number: (int) Number to factorize
    :param factor_list: (list) List of factors
    :return: None
    """
    factors_string = ', '.join(map(str, factor_list))
    try:
        with open(file=LOG_PATH, mode="a", encoding='utf8') as file:
            data_log = f"Prime factorization: {number}\n{factors_string}"
            print(data_log)
            data_log += "\n"
            file.write(data_log)
    except IOError:
        print("Could not read file:", NUMBERS_PATH)


if __name__ == "__main__":
    freeze_support()
    read_user_input()
