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


def extend_result(val):
    """
    separated with ',' if it is a list
    """
    if isinstance(val, list):
        return ','.join(val)
    return val


def write_to_file(result):
    """
    write the anonymized result to anonymized.data
    """
    with open("data/anonymized.data", "w") as output:
        for r in result:
            output.write(';'.join(map(extend_result, r)) + '\n')


def get_result_one(att_trees, data, k=DEFAULT_K):
    "run basic_mondrian for one time, with k=10"
    print "K=%d" % k
    print "Mondrian"
    result, eval_result = mondrian(att_trees, data, k)
    write_to_file(result)
    print "NCP %0.2f" % eval_result[0] + "%"
    print "Running time %0.2f" % eval_result[1] + "seconds"


def get_result_k(att_trees, data):
    """
    change k, whle fixing QD and size of dataset
    """
    data_back = copy.deepcopy(data)
    all_ncp = []
    all_rtime = []
    # for k in range(5, 105, 5):
    for k in [2, 5, 10, 25, 50, 100]:
        print '#' * 30
        print "K=%d" % k
        print "Mondrian"
        _, eval_result = mondrian(att_trees, data, k)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        all_ncp.append(round(eval_result[0], 2))
        print "Running time %0.2f" % eval_result[1] + "seconds"
        all_rtime.append(round(eval_result[1], 2))
    print "All NCP", all_ncp
    print "All Running time", all_rtime


def get_result_dataset(att_trees, data, k=DEFAULT_K, n=10):
    """
    fix k and QI, while changing size of dataset
    n is the proportion nubmber.
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    print "K=%d" % k
    joint = 5000
    datasets = []
    check_time = length / joint
    if length % joint == 0:
        check_time -= 1
    for i in range(check_time):
        datasets.append(joint * (i + 1))
    datasets.append(length)
    all_ncp = []
    all_rtime = []
    for pos in datasets:
        ncp = rtime = 0
        print '#' * 30
        print "size of dataset %d" % pos
        for j in range(n):
            temp = random.sample(data, pos)
            result, eval_result = mondrian(att_trees, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_back)
        ncp /= n
        rtime /= n
        print "Average NCP %0.2f" % ncp + "%"
        all_ncp.append(round(ncp, 2))
        print "Running time %0.2f" % rtime + "seconds"
        all_rtime.append(round(rtime, 2))
    print '#' * 30
    print "All NCP", all_ncp
    print "All Running time", all_rtime


def get_result_qi(att_trees, data, k=DEFAULT_K):
    """
    change nubmber of QI, whle fixing k and size of dataset
    """
    data_back = copy.deepcopy(data)
    ls = len(data[0])
    all_ncp = []
    all_rtime = []
    for i in range(1, ls):
        print '#' * 30
        print "Number of QI=%d" % i
        _, eval_result = mondrian(att_trees, data, k, i)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        all_ncp.append(round(eval_result[0], 2))
        print "Running time %0.2f" % eval_result[1] + "seconds"
        all_rtime.append(round(eval_result[1], 2))
    print "All NCP", all_ncp
    print "All Running time", all_rtime


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
    print '#' * 30
    if DATA_SELECT == 'a':
        print "Adult data"
    else:
        print "INFORMS data"
    print '#' * 30
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
        print "Usage: python anonymizer.py [a | i] [k | qi | data | one]"
        print "a: adult dataset, 'i': INFORMS ataset"
        print "K: varying k, qi: varying qi numbers, data: varying size of dataset, \
                one: run only once"
    # anonymized dataset is stored in result
    print "Finish Basic_Mondrian!!"
