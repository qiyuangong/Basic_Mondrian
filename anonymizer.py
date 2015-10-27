"""
run semi_partition with given parameters
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
# sys.setrecursionlimit(50000)


def get_result_one(att_trees, data, K=10):
    "run semi_partition for one time, with k=10"
    print "K=%d" % K
    print "Mondrian"
    data_back = copy.deepcopy(data)
    _, eval_result = mondrian(att_trees, data, K)
    print "NCP %0.2f" % eval_result[0] + "%"
    print "Running time %0.2f" % eval_result[1] + "seconds"


def get_result_k(att_trees, data):
    """
    change K, whle fixing QD and size of dataset
    """
    data_back = copy.deepcopy(data)
    for K in range(5, 105, 5):
        print '#' * 30
        print "K=%d" % K
        print "Mondrian"
        _, eval_result = mondrian(att_trees, data, K)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        print "Running time %0.2f" % eval_result[1] + "seconds"


def get_result_dataset(att_trees, data, K=10, n=10):
    """
    fix k and QI, while changing size of dataset
    n is the proportion nubmber.
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    print "K=%d" % K
    joint = 5000
    datasets = []
    check_time = length / joint
    if length % joint == 0:
        check_time -= 1
    for i in range(check_time):
        datasets.append(joint * (i + 1))
    datasets.append(length)
    for pos in datasets:
        ncp = rtime = 0
        print '#' * 30
        print "size of dataset %d" % pos
        for j in range(n):
            temp = random.sample(data, pos)
            result, eval_result = semi_partition(att_trees, temp, K)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_back)
            # save_to_file((att_trees, temp, result, K, L))
        ncp /= n
        rtime /= n
        print "Average NCP %0.2f" % ncp + "%"
        print "Running time %0.2f" % rtime + "seconds"
        print '#' * 30


def get_result_qi(att_trees, data, K=10):
    """
    change nubmber of QI, whle fixing K and size of dataset
    """
    data_back = copy.deepcopy(data)
    ls = len(data[0])
    for i in reversed(range(1, ls)):
        print '#' * 30
        print "Number of QI=%d" % i
        _, eval_result = semi_partition(att_trees, data, K, i)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        print "Running time %0.2f" % eval_result[1] + "seconds"


if __name__ == '__main__':
    FLAG = ''
    LEN_ARGV = len(sys.argv)
    try:
        DATA_SELECT = sys.argv[1]
        FLAG = sys.argv[2]
    except:
        pass
    K = 10
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
            K = int(sys.argv[3])
            get_result_one(ATT_TREES, RAW_DATA, K)
        else:
            get_result_one(ATT_TREES, RAW_DATA)
    elif FLAG == '':
        get_result_one(ATT_TREES, RAW_DATA)
    else:
        print "Usage: python anonymizer [a | i] [k | qi | data | one]"
        print "a: adult dataset, 'i': INFORMS ataset"
        print "k: varying k, qi: varying qi numbers, data: varying size of dataset, \
                one: run only once"
    # anonymized dataset is stored in result
    print "Finish Semi_Partition!!"
