"""
run basic_mondrian with given parameters
"""

# !/usr/bin/env python
# coding=utf-8
from mondrian import mondrian
from utils.read_adult_data import read_data as read_adult
from utils.read_adult_data import read_tree as read_adult_tree
from utils.read_informs_data import read_data as read_informs
from utils.read_informs_data import read_tree as read_informs_tree
import sys, copy, random

DATA_SELECT = 'a'
DEFAULT_K = 10
# sys.setrecursionlimit(50000)


# If a list, concatenate its values into a string, separated by commas
def extend_result(val):
    # Check if val is a(n instance of) list
    if isinstance(val, list):
        # The string join() method returns a string by joining all the elements of an iterable (list, string, tuple), separated by the given separator.
        return ','.join(val)
    return val


# The input parameter result is the output of Mondrian
# Write the anonymized result to anonymized.data
def write_to_file(result):   
    with open("data/anonymized.data", "w") as output:
        for r in result:
            # The map() function executes a specified function for each item in an iterable
            #   map(extend_result, r):                      for each item in r, if that item is a list, make a string out of it separated by commas
            #   ';'.join( <a list of strings> ) + '\n':     join the string list into one string, separated by semicolons
            output.write(';'.join(map(extend_result, r)) + '\n')


# Run Mondrian once (with k, QIDs and the size of the dataset fixed)
def get_result_one(att_trees, data, k=DEFAULT_K):    
    print("K=", k)
    print("Mondrian")
    result, eval_result = mondrian(att_trees, data, k)
    write_to_file(result)
    print("NCP %0.2f" % eval_result[0] + "%")
    print("Running time %0.2f" % eval_result[1] + " seconds")


# Run the algorithm with different k values (with QIDs and the size of the dataset fixed)
def get_result_k(att_trees, data):
    data_backup = copy.deepcopy(data)
    all_ncp = []
    all_rtime = []
    # for k in range(5, 105, 5):
    for k in [2, 5, 10, 25, 50, 100]:
        print('#' * 30)
        print("K=" + k)
        print("Mondrian")
        _, eval_result = mondrian(att_trees, data, k)
        data = copy.deepcopy(data_backup)
        print("NCP %0.2f" % eval_result[0] + "%")
        all_ncp.append(round(eval_result[0], 2))
        print("Running time %0.2f" % eval_result[1] + " seconds")
        all_rtime.append(round(eval_result[1], 2))
    print("All NCP", all_ncp) 
    print("All Running time", all_rtime)


# Run the algorithm on dataset chunks of increasing size (with k and QIDs fixed)
# For each chunk, carry out the anonymization n times and average the results for the NPC metric
def get_result_dataset(att_trees, data, k=DEFAULT_K, n=10):
    data_backup = copy.deepcopy(data)
    length = len(data_backup)
    print("K=%d" % k)
    # The step by which to increase the size of the dataset in each iteration
    joint = 5000
    datasets = []
    # Check how many times the dataset can be increased
    check_time = length / joint
    if length % joint == 0:
        check_time -= 1
    # Store the chunks of dataset sizes to use
    for i in range(check_time):
        datasets.append(joint * (i + 1))
    datasets.append(length)
    all_ncp = []
    all_rtime = []

    for pos in datasets:
        ncp = rtime = 0
        print('#' * 30)
        print("size of dataset %d" % pos)
        # n received as an input parameter, repeat that many times the [take random sample of size pos AND run mondrian]
        for j in range(n):
            temp = random.sample(data, pos)
            result, eval_result = mondrian(att_trees, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_backup)
        ncp /= n
        rtime /= n
        print("Average NCP %0.2f" % ncp + "%")
        all_ncp.append(round(ncp, 2))
        print("Running time %0.2f" % rtime + "seconds")
        all_rtime.append(round(rtime, 2))
    print('#' * 30)
    print("All NCP", all_ncp)
    print("All Running time", all_rtime)


# Run mondrian with setting the number of desired QIDs to use in each run (with k and the size of the dataset fixed)
# Iterate from using 1 QID to using all of them
def get_result_qi(att_trees, data, k=DEFAULT_K):    
    data_backup = copy.deepcopy(data)
    ## The number of attributes in one line
    ls = len(data[0])
    all_ncp = []
    all_rtime = []
    for i in range(1, ls):
        print('#' * 30)
        print("Number of QI=%d" % i)
        _, eval_result = mondrian(att_trees, data, k, i)
        data = copy.deepcopy(data_backup)
        print("NCP %0.2f" % eval_result[0] + "%")
        all_ncp.append(round(eval_result[0], 2))
        print("Running time %0.2f" % eval_result[1] + "seconds")
        all_rtime.append(round(eval_result[1], 2))
    print("All NCP", all_ncp)
    print("All Running time", all_rtime)


if __name__ == '__main__':
    FLAG = ''
    LEN_ARGV = len(sys.argv)
    try:
        DATA_SELECT = sys.argv[1]
        FLAG = sys.argv[2]
    except:
        pass
    k = 10
    if DATA_SELECT == 'i':
        RAW_DATA = read_informs()
        ATT_TREES = read_informs_tree()
    else:
        RAW_DATA = read_adult()
        ATT_TREES = read_adult_tree()
    print('#' * 30)
    if DATA_SELECT == 'a':
        print("Adult data")
    else:
        print("INFORMS data")
    print('#' * 30)
    if FLAG == 'k':
        get_result_k(ATT_TREES, RAW_DATA)
    elif FLAG == 'qi':
        get_result_qi(ATT_TREES, RAW_DATA)
    elif FLAG == 'data':
        get_result_dataset(ATT_TREES, RAW_DATA)
    elif FLAG == 'one':
        if LEN_ARGV > 3:
            k = int(sys.argv[3])
            get_result_one(ATT_TREES, RAW_DATA, k)
        else:
            get_result_one(ATT_TREES, RAW_DATA)
    elif FLAG == '':
        get_result_one(ATT_TREES, RAW_DATA)
    else:
        print("Usage: python anonymizer.py [a | i] [k | qi | data | one]")
        print("a: adult dataset, 'i': INFORMS ataset")
        print("K: varying k, qi: varying qi numbers, data: varying size of dataset, \
                one: run only once")
    # anonymized dataset is stored in result
    print("Finish Basic_Mondrian!!")
